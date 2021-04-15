import os
from PIL import Image
from flask import Blueprint, render_template,\
    flash, redirect, url_for, session, request,\
    send_from_directory
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from hospitalSystemPackage import db, app, appValues
from hospitalSystemPackage.commonFunctions.forms import LoginForm,\
    UpdateProfileImageForm, ChangePasswordForm, PasswordResetEmailForm, \
    PasswordResetForm
from hospitalSystemPackage.models import User
from hospitalSystemPackage import bcrypt
from hospitalSystemPackage.commonFunctions.utils import randomSecretString,\
    randomSecretNumbers, getDocumentFromEncryptedId, getNumberName, \
    verifyToken, getActivationToken, getResetToken, sendResetEmail, sendResetEmailForTest

commonFunctions = Blueprint("commonFunctions", __name__)

'''
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('commonFunctions.home'))
'''

@commonFunctions.route("/")
@commonFunctions.route("/home")
def home():
    return render_template("commonFunctions/home.html", linkHome='active')


@commonFunctions.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('commonFunctions.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
        # if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            # next_page = request.args.get('next')
            if user.userType == appValues['p']:
                return redirect(url_for('patient.allDocuments'))
            elif current_user.userType == appValues['h']:
                return redirect(url_for('hospitalStaff.registerPatient'))
            elif current_user.userType == appValues['a']:
                return redirect(url_for('admin.users'))
            else:
                return redirect(url_for('commonFunctions.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("commonFunctions/login.html", title='login', form=form, linkLogin='active')


@commonFunctions.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('commonFunctions.home'))


@commonFunctions.route("/changePassword", methods=['GET', 'POST'])
@login_required
def changePassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = bcrypt.generate_password_hash(form.newPassword.data).decode('utf-8')
        db.session.commit()

        flash("Password changed successfully", 'success')
        if current_user.userType == appValues['p']:
            return redirect(url_for('patient.userPatientInfo'))
        elif current_user.userType == appValues['h']:
            return redirect(url_for('hospitalStaff.userHospitalStaffInfo'))
        elif current_user.userType == appValues['a']:
            return redirect(url_for('admin.userAdminInfo'))
        elif current_user.userType == appValues['d']:
            return redirect(url_for('doctor.userDoctorInfo'))
        else:
            return redirect(url_for('commonFunctions.home'))

        # return redirect(url_for('commonFunctions.home'))
    return render_template('commonFunctions/changePassword.html',
                           form=form,
                           title='Update Information',
                           linkUserInfo='active')


@commonFunctions.route("/updateProfileImage", methods=['GET', 'POST'])
@login_required
def updateProfileImage():
    form = UpdateProfileImageForm()
    if form.validate_on_submit():
        if not form.profileImage.data:
            flash('No File Part', 'danger')
            return redirect(request.url)

        pictureFile = form.profileImage.data

        if pictureFile.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if current_user.profileImage != 'default.png':
            os.remove(os.path.join(app.root_path, 'userFiles/profileImages', current_user.profileImage))

        filename = secure_filename(pictureFile.filename)
        fName, fExt = os.path.splitext(filename)
        
        newFilename = getNumberName('profileImageFileName') + fExt

        output_size = (256, 256)
        i = Image.open(pictureFile)
        i.thumbnail(output_size)
        i.save(os.path.join(app.root_path, 'userFiles/profileImages', newFilename))

        current_user.profileImage = newFilename

        db.session.commit()
        flash('Your account has been updated!', 'success')

        if current_user.userType == appValues['p']:
            return redirect(url_for('patient.userPatientInfo'))
        elif current_user.userType == appValues['h']:
            return redirect(url_for('hospitalStaff.userHospitalStaffInfo'))
        elif current_user.userType == appValues['a']:
            return redirect(url_for('admin.userAdminInfo'))
        elif current_user.userType == appValues['d']:
            return redirect(url_for('doctor.userDoctorInfo'))
        else:
            return redirect(url_for('commonFunctions.home'))
    return render_template("commonFunctions/updateProfileImage.html",
                           form=form,
                           title='Update Information',
                           linkUserInfo='active')


@commonFunctions.route("/deleteProfileImage", methods=['GET', 'POST'])
@login_required
def deleteProfileImage():
    if current_user.profileImage != 'default.png':
        os.remove(os.path.join(app.root_path, 'userFiles/profileImages', current_user.profileImage))
        current_user.profileImage = 'default.png'
        db.session.commit()

    '''
    if current_user.userType == appValues['p']:
        return redirect(url_for('patient.userPatientInfo'))
    elif current_user.userType == appValues['a']:
        return redirect(url_for('admin.userAdminInfo'))
    else:
        return redirect(url_for('commonFunctions.home'))
    '''

    if current_user.userType == appValues['p']:
        return redirect(url_for('patient.userPatientInfo'))
    elif current_user.userType == appValues['h']:
        return redirect(url_for('hospitalStaff.userHospitalStaffInfo'))
    elif current_user.userType == appValues['a']:
        return redirect(url_for('admin.userAdminInfo'))
    elif current_user.userType == appValues['d']:
        return redirect(url_for('doctor.userDoctorInfo'))
    else:
        return redirect(url_for('commonFunctions.home'))


@commonFunctions.route("/showProfileImage/<string:fileName>", methods=['GET', 'POST'])
@login_required
def showProfileImage(fileName):
    return send_from_directory(os.path.join(app.root_path, 'userFiles/profileImages'), filename=fileName)


@commonFunctions.route("/passwordResetEmail", methods=['GET', 'POST'])
def passwordResetEmail():
    if current_user.is_authenticated:
        return redirect(url_for('commonFunctions.home'))

    form = PasswordResetEmailForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # result = sendResetEmail(user, True)
        result = sendResetEmailForTest(user, True)
        if result:
            flash('An email has been sent to your email with instructions.', 'info')
            return redirect(url_for('commonFunctions.login'))
        else:
            flash('Something went wrong. Please try again.', 'info')
            return redirect(url_for('commonFunctions.passwordResetEmail'))
    return render_template('commonFunctions/passwordResetEmail.html',
                           title='password reset',
                           form=form,
                           linkLogin='active')


@commonFunctions.route("/passwordReset/<token>", methods=['GET', 'POST'])
def passwordReset(token = None):
    if current_user.is_authenticated:
        return redirect(url_for('commonFunctions.home'))

    user = verifyToken(token)

    if user == None:
        flash('Your request is either invalid or expired.', 'warning')
        return redirect(url_for('commonFunctions.home'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        if form.passwordChangeCode.data != user.passwordChangeCode:
            flash('The code is invalid', 'danger')
            return redirect(url_for('commonFunctions.passwordReset', token=token))
        hashedPassword = bcrypt.generate_password_hash(form.newPassword.data).decode('utf-8')
        user.password = hashedPassword

        db.session.commit()

        flash('New password set. Please Log In with the new password.', 'success')
        return redirect(url_for('commonFunctions.login'))

    return render_template('commonFunctions/passwordReset.html',
                           title='password reset',
                           form=form,
                           linkLogin='active')