import os, datetime
from functools import wraps
import jwt
from PIL import Image
from flask import Blueprint, render_template, flash, redirect,\
    url_for, request, send_from_directory, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from hospitalSystemPackage import db, app, bcrypt, appValues
from hospitalSystemPackage.models import User, Patient, HospitalStaff,\
    Document, ValueInt, Doctor, Admin
from hospitalSystemPackage.commonFunctions.forms import  RegisterPatientForm, \
    RegisterHospitalStaffForm, RegisterDoctorForm
from hospitalSystemPackage.commonFunctions.addAccount import registerPatientFunction, \
    registerHospitalStaffFunction, registerDoctorFunction
from hospitalSystemPackage.admin.forms import RegisterAdminForm, SearchForm, \
    UdpateAdminInfoForm, ChangeValidSpaceForm
from hospitalSystemPackage.commonFunctions.utils import randomSecretString,\
    randomSecretNumbers, getDocumentFromEncryptedId, encodeId, getNumberName,\
    getPatientFromEncryptedId, getHospitalStaffFromEncryptedId,\
    getDoctorFromEncryptedId, getReturnPage, getAdminFromEncryptedId
from hospitalSystemPackage.commonFunctions.addAccount import registerAdminFunction
from hospitalSystemPackage.commonFunctions.deleteAccount import\
    deletePatientAccount, deleteHospitalStaffAccount, deleteDoctorAccount, \
    deleteAdminAccount



admin = Blueprint("admin", __name__)

def adminAccessibleOnly(originalFunction):

    @wraps(originalFunction)
    def wrapperFunction(*args, **kwargs):
        if current_user.userType == appValues['a']:
            return originalFunction(*args, **kwargs)
        else:
            flash('You are not allowed to visit this page.', 'danger')
            return redirect(url_for('commonFunctions.home'))

    return wrapperFunction



@admin.route("/changeValidSpace", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def changeValidSpace():
    currentSpace = ValueInt.query.filter_by(variableName = 'spaceSize').first()
    form = ChangeValidSpaceForm()
    if form.validate_on_submit():
        currentSpace.variableValue = form.space.data
        db.session.commit()
        flash('Valid space size changed', 'success')
        return redirect(request.url)
    elif request.method == 'GET':
        form.space.data = currentSpace.variableValue
    return render_template("admin/changeValidSpace.html",
                           form = form,
                           currentSpace = currentSpace.variableValue,
                           linkChangeValidSpace = 'active')


@admin.route("/Users", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def users():
    return render_template('admin/users.html', title='Users', linkUsers='active')


@admin.route("/allPatients", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def allPatients():
    page = request.args.get('page', 1, type=int)
    patients = Patient.query.order_by(Patient.id.desc()).paginate(page=page, per_page=2)

    allData = []
    for patient in patients.items:
        allData.append((User.query.get(patient.idFromUserModel), patient))
    return render_template('admin/allPatients.html',
                           title='allPatients',
                           patients=patients,
                           allData = allData,
                           refCount=(page - 1) * 2,
                           fromPage=page,
                           linkUsers='active')


@admin.route("/allHospitalStaff", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def allHospitalStaff():
    page = request.args.get('page', 1, type=int)
    hospitalStaff = HospitalStaff.query.order_by(HospitalStaff.id.desc()).paginate(page=page, per_page=2)

    allData = []
    for staff in hospitalStaff.items:
        allData.append((User.query.get(staff.idFromUserModel), staff))
    return render_template('admin/allHospitalStaff.html',
                           title='allHospitalStaff',
                           hospitalStaff=hospitalStaff,
                           allData = allData,
                           refCount=(page - 1) * 2,
                           fromPage=page,
                           linkUsers='active')


@admin.route("/allDoctors", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def allDoctors():
    page = request.args.get('page', 1, type=int)
    doctors = Doctor.query.order_by(Doctor.id.desc()).paginate(page=page, per_page=2)

    allData = []
    for doctor in doctors.items:
        allData.append((User.query.get(doctor.idFromUserModel), doctor))
    return render_template('admin/allDoctors.html',
                           title='allDoctors',
                           doctors=doctors,
                           allData = allData,
                           refCount=(page - 1) * 2,
                           fromPage=page,
                           linkUsers='active')


@admin.route("/allAdmins", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def allAdmins():
    page = request.args.get('page', 1, type=int)
    admins = Admin.query.order_by(Admin.id.desc()).paginate(page=page, per_page=2)

    allData = []
    for admin in admins.items:
        allData.append((User.query.get(admin.idFromUserModel), admin))
    return render_template('admin/allAdmins.html',
                           title='allAdmins',
                           admins=admins,
                           allData = allData,
                           refCount=(page - 1) * 2,
                           fromPage=page,
                           linkUsers='active')


@admin.route("/searchPatient", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def searchPatient():
    form = SearchForm()
    if form.validate_on_submit():
        if form.searchBy.data == 'username':
            patients = Patient.query. \
                filter(Patient.username.startswith(form.searchName.data)).limit(2).all()

            allData=[]
            for patient in patients:
                allData.append((User.query.get(patient.idFromUserModel), patient))


        # users = User.query.filter(User.username.like('%{}%'.format(form.searchName.data))).all()
        # users = User.query.filter(User.username.ilike('%{}%'.format(form.searchName.data))).all()


        elif form.searchBy.data == 'email':
            users = User.query.filter_by(userType='patient'). \
                filter(User.email.startswith(form.searchName.data)).limit(2).all()

            allData=[]
            for user in users:
                allData.append((user, Patient.query.get(user.typeUserId)))

        elif form.searchBy.data == 'name':
            patients = Patient.query. \
                filter(Patient.name.startswith(form.searchName.data)).limit(2).all()

            allData = []
            for patient in patients:
                allData.append((User.query.get(patient.idFromUserModel), patient))

        else:
            allData = []

        return render_template('admin/searchPatient.html',
                               title='searchPatient',
                               allData=allData,
                               form=form,
                               linkUsers='active')

    return render_template('admin/searchPatient.html',
                           title='searchPatient',
                           form=form,
                           linkUsers='active')


@admin.route("/searchHospitalStaff", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def searchHospitalStaff():
    form = SearchForm()
    if form.validate_on_submit():
        if form.searchBy.data == 'username':
            allHospitalStaff = HospitalStaff.query. \
                filter(HospitalStaff.username.startswith(form.searchName.data)).limit(2).all()

            allData = []
            for hospitalStaff in allHospitalStaff:
                allData.append((User.query.get(hospitalStaff.idFromUserModel), hospitalStaff))


        # users = User.query.filter(User.username.like('%{}%'.format(form.searchName.data))).all()
        # users = User.query.filter(User.username.ilike('%{}%'.format(form.searchName.data))).all()

        elif form.searchBy.data == 'email':
            users = User.query.filter_by(userType='hospitalStaff'). \
                filter(User.email.startswith(form.searchName.data)).limit(2).all()

            allData = []
            for user in users:
                allData.append((user, HospitalStaff.query.get(user.typeUserId)))

        elif form.searchBy.data == 'name':
            allHospitalStaff = HospitalStaff.query. \
                filter(HospitalStaff.name.startswith(form.searchName.data)).limit(2).all()

            allData = []
            for hospitalStaff in allHospitalStaff:
                allData.append((User.query.get(hospitalStaff.idFromUserModel), hospitalStaff))

        else:
            allData = []

        return render_template('admin/searchHospitalStaff.html',
                               title='searchHospitalStaff',
                               allData=allData,
                               form=form,
                               linkUsers='active')

    return render_template('admin/searchHospitalStaff.html',
                           title='searchHospitalStaff',
                           form=form,
                           linkUsers='active')


@admin.route("/searchDoctor", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def searchDoctor():
    form = SearchForm()
    if form.validate_on_submit():
        if form.searchBy.data == 'username':
            doctors = Doctor.query. \
                filter(Doctor.username.startswith(form.searchName.data)).limit(2).all()

            allData = []
            for doctor in doctors:
                allData.append((User.query.get(doctor.idFromUserModel), doctor))


        # users = User.query.filter(User.username.like('%{}%'.format(form.searchName.data))).all()
        # users = User.query.filter(User.username.ilike('%{}%'.format(form.searchName.data))).all()

        elif form.searchBy.data == 'email':
            users = User.query.filter_by(userType='patient'). \
                filter(User.email.startswith(form.searchName.data)).limit(2).all()

            allData = []
            for user in users:
                allData.append((user, Doctor.query.get(user.typeUserId)))

        elif form.searchBy.data == 'name':
            doctors = Doctor.query. \
                filter(Doctor.name.startswith(form.searchName.data)).limit(2).all()

            allData = []
            for doctor in doctors:
                allData.append((User.query.get(doctor.idFromUserModel), doctor))

        else:
            allData = []

        return render_template('admin/searchDoctor.html',
                               title='searchDoctor',
                               allData=allData,
                               form=form,
                               linkUsers='active')

    return render_template('admin/searchDoctor.html',
                           title='searchDoctor',
                           form=form,
                           linkUsers='active')


@admin.route("/allPatients/<string:userType>/<string:storedName>", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def particularUserInfo(userType, storedName):
    if userType == 'patient':
        userVariable = getPatientFromEncryptedId(storedName)
        user = User.query.get(userVariable.idFromUserModel)
    elif userType == 'hospitalStaff':
        userVariable = getHospitalStaffFromEncryptedId(storedName)
        user = User.query.get(userVariable.idFromUserModel)
    elif userType == 'doctor':
        userVariable = getDoctorFromEncryptedId(storedName)
        user = User.query.get(userVariable.idFromUserModel)
    elif userType == 'admin':
        userVariable = getAdminFromEncryptedId(storedName)
        user = User.query.get(userVariable.idFromUserModel)
    else:
        userVariable = None
        user = None
    return render_template('admin/particularUserInfo.html',
                           title='particularUserInfo',
                           user=user,
                           userVariable=userVariable,
                           linkUsers='active')


@admin.route("/register", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def register():
    return render_template('admin/register.html', title='Register', linkRegister='active')


@admin.route("/registerPatient", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def registerPatient():
    form = RegisterPatientForm()
    if form.validate_on_submit():
        registerPatientFunction(form)
        return redirect(url_for('admin.registerPatient')) # (multi line) If it is not
        # (multi line) redirected here, previous data from previous
        # (multi Line) form remains, as render template is executed next.
    # print(form.errors)  --> prints the errors in forms
    return render_template('admin/registerPatient.html',
                           title='registerPatient',
                           form=form,
                           linkRegister='active')


@admin.route("/registerHospitalStaff", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def registerHospitalStaff():
    form = RegisterHospitalStaffForm()
    if form.validate_on_submit():
        registerHospitalStaffFunction(form)
        return redirect(url_for('admin.registerHospitalStaff')) # (multi line) If it is not
        # (multi line) redirected here, previous data from previous
        # (multi Line) form remains, as render template is executed next.
    # print(form.errors)  --> prints the errors in forms
    return render_template('admin/registerHospitalStaff.html',
                           title='registerHospitalStaff',
                           form=form,
                           linkRegister='active')


@admin.route("/registerDoctor", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def registerDoctor():
    form = RegisterDoctorForm()
    if form.validate_on_submit():
        registerDoctorFunction(form)
        return redirect(url_for('admin.registerDoctor')) # (multi line) If it is not
        # (multi line) redirected here, previous data from previous
        # (multi Line) form remains, as render template is executed next.
    # print(form.errors)  --> prints the errors in forms
    return render_template('admin/registerDoctor.html',
                           title='registerDoctor',
                           form=form,
                           linkRegister='active')


@admin.route("/registerAdmin", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def registerAdmin():
    form = RegisterAdminForm()
    if form.validate_on_submit():
        registerAdminFunction(form)
        return redirect(url_for('admin.registerAdmin'))  # (multi line) If it is not
        # (multi line) redirected here, previous data from previous
        # (multi Line) form remains, as render template is executed next.
        # print(form.errors)  --> prints the errors in forms
    return render_template('admin/registerAdmin.html',
                           title='registerAdmin',
                           form=form,
                           linkRegister='active')


@admin.route("/deleteUserConfirmation/"
             "<string:userType>/<string:storedName>", methods=['GET', 'POST'])
@admin.route("/deleteUserConfirmation/"
             "<string:userType>/<string:storedName>/"
             "<int:fromPage>/<int:itemNumber>", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def deleteUserConfirmation(userType=None, storedName=None, fromPage=None, itemNumber=None):
    if userType == None or storedName == None:
        flash('Could not find user', 'danger')
        return redirect(url_for('admin.users'))

    if fromPage == None and itemNumber == None:
        return render_template('admin/deleteConfirmation.html',
                               userType=userType,
                               storedName=storedName,
                               cameFrom='search',
                               linkUserInfo='active')
    else:
        return render_template('admin/deleteConfirmation.html',
                               userType=userType,
                               storedName=storedName,
                               cameFrom='userList',
                               fromPage = fromPage,
                               itemNumber=itemNumber,
                               linkUserInfo='active')


@admin.route("/deleteUser/"
             "<string:userType>/<string:storedName>", methods=['GET', 'POST'])
@admin.route("/deleteUser/<string:userType>/"
             "<string:storedName>/"
             "<int:fromPage>/<int:itemNumber>", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def deleteUser(userType=None, storedName=None, fromPage=None, itemNumber=None):
    if userType == 'patient':
        patient = getPatientFromEncryptedId(storedName)

        deletePatientAccount(patient)

        flash('Patient account has been deleted.', 'success')

        if fromPage == None and itemNumber == None:
            return redirect(url_for('admin.searchPatient'))

        return redirect(url_for('admin.allPatients', page=getReturnPage(fromPage, itemNumber)))

    elif userType=='hospitalStaff':
        hospitalStaff = getHospitalStaffFromEncryptedId(storedName)

        deleteHospitalStaffAccount(hospitalStaff)

        flash('Hospital Staff account has been deleted.', 'success')

        if fromPage == None and itemNumber == None:
            return redirect(url_for('admin.searchHospitalStaff'))

        return redirect(url_for('admin.allHospitalStaff', page=getReturnPage(fromPage, itemNumber)))

    elif userType=='doctor':
        doctor = getDoctorFromEncryptedId(storedName)

        deleteDoctorAccount(doctor)

        flash('Doctor account has been deleted.', 'success')

        if fromPage == None and itemNumber == None:
            return redirect(url_for('admin.searchDoctor'))

        return redirect(url_for('admin.allDoctors', page=getReturnPage(fromPage, itemNumber)))

    else:
        flash('Not proper request sent.')

    # return redirect(request.referrer)

    return redirect(url_for('admin.users'))


@admin.route("/userAdminInfo", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def userAdminInfo():
    admin = Admin.query.get_or_404(current_user.typeUserId)
    return render_template("admin/userAdminInfo.html",
                           admin=admin,
                           linkUserInfo='active')


@admin.route("/updateAdminInfo", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def updateAdminInfo():
    admin = Admin.query.get_or_404(current_user.typeUserId)
    form = UdpateAdminInfoForm()
    if form.validate_on_submit():
        admin.username = form.username.data
        current_user.email = form.email.data
        admin.name = form.name.data

        admin.title = form.title.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('admin.userAdminInfo'))
    elif request.method == 'GET':
        form.username.data = admin.username
        form.email.data = current_user.email
        form.name.data = admin.name
        form.title.data = admin.title
    return render_template("admin/updateAdminInfo.html",
                           form=form,
                           title='Update Information',
                           linkUserInfo='active')


@admin.route("/deleteAccountConfirmation", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def deleteAccountConfirmation():
    return render_template('admin/deleteConfirmation.html',
                           cameFrom = 'account',
                           linkUserInfo = 'active')


@admin.route("/deleteAccount", methods=['GET', 'POST'])
@login_required
@adminAccessibleOnly
def deleteAccount():
    admin = Admin.query.get_or_404(current_user.typeUserId)
    logout_user()
    deleteAdminAccount(admin)

    flash('Your Account has been deleted.', 'success')
    return redirect(url_for('commonFunctions.home'))