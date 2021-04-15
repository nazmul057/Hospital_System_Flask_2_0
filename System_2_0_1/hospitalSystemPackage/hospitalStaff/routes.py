import os, datetime
from functools import wraps
import jwt
from PIL import Image
from functools import wraps
from flask import Blueprint, render_template, flash, redirect,\
    url_for, request, send_from_directory, abort

from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from hospitalSystemPackage import db, app, appValues
from hospitalSystemPackage.models import User, Patient, Document, ValueInt, Doctor, HospitalStaff
from hospitalSystemPackage.commonFunctions.utils import randomSecretString,\
    randomSecretNumbers, getDocumentFromEncryptedId, encodeId, getNumberName,\
    getReturnPage, getFileFolder
from hospitalSystemPackage.commonFunctions.deleteAccount import \
    deleteHospitalStaffAccount
from hospitalSystemPackage.commonFunctions.userSpecifics import \
    deleteDocument, uploadDocument
from hospitalSystemPackage.commonFunctions.forms import RegisterPatientForm
from hospitalSystemPackage.commonFunctions.addAccount import registerPatientFunction
from hospitalSystemPackage.hospitalStaff.forms import \
    UploadPatientDocumentForm, UpdateHospitalStaffInfoForm, LinkPatientAndDoctorForm


hospitalStaff = Blueprint("hospitalStaff", __name__)


def hospitalStaffAccessibleOnly(originalFunction):

    @wraps(originalFunction)
    def wrapperFunction(*args, **kwargs):
        if current_user.userType == appValues['h']:
            return originalFunction(*args, **kwargs)
        else:
            flash('You are not allowed to visit this page.', 'danger')
            return redirect(url_for('commonFunctions.home'))

    return wrapperFunction



@hospitalStaff.route("/linkPatientToDoctor", methods=['GET', 'POST'])
@login_required
@hospitalStaffAccessibleOnly
def linkPatientToDoctor():
    form = LinkPatientAndDoctorForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(username=form.patientUsername.data).first()
        doctor = Doctor.query.filter_by(username=form.doctorUsername.data).first()
        if not patient or not doctor:
            if not patient:
                flash('Could not find the patient. Please check the Patient username', 'danger')
            if not doctor:
                flash('Could not find the doctor. Please check the Doctor username', 'danger')
            return render_template('hospitalStaff/linkPatientAndDoctor.html',
                                   form=form,
                                   title='Link Patient to Doctor',
                                   linkType = 'addLink',
                                   linkPatientToDoctor='active')

        try:
            patient.patientDoctors.append(doctor)
            db.session.commit()
            flash('Linked Successfully', 'success')
        except:
            flash('Link already exists.', 'success')
        return redirect(request.url)
    return render_template('hospitalStaff/linkPatientAndDoctor.html',
                           form=form,
                           title='Link Patient to Doctor',
                           linkType='addLink',
                           linkPatientToDoctor='active')


@hospitalStaff.route("/removeLinkPatientToDoctor", methods=['GET', 'POST'])
@login_required
@hospitalStaffAccessibleOnly
def removeLinkPatientToDoctor():
    form = LinkPatientAndDoctorForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(username=form.patientUsername.data).first()
        doctor = Doctor.query.filter_by(username=form.doctorUsername.data).first()
        if not patient or not doctor:
            if not patient:
                flash('Could not find the patient. Please check the Patient username', 'danger')
            if not doctor:
                flash('Could not find the doctor. Please check the Doctor username', 'danger')
            return render_template('hospitalStaff/linkPatientAndDoctor.html',
                                   form=form,
                                   title='Remove Link',
                                   removeLinkPatientToDoctor='active')

        try:
            patient.patientDoctors.remove(doctor)
            db.session.commit()
            flash('Link Removed Successfully', 'success')
        except:
            flash('Link does not exist.', 'success')

        return redirect(request.url)

    return render_template('hospitalStaff/linkPatientAndDoctor.html',
                           form=form,
                           title='Remove Link',
                           removeLinkPatientToDoctor='active')


@hospitalStaff.route("/registerPatient", methods=['GET', 'POST'])
@login_required
@hospitalStaffAccessibleOnly
def registerPatient():
    form = RegisterPatientForm()
    if form.validate_on_submit():

        registerPatientFunction(form)
        return redirect(url_for('hospitalStaff.registerPatient')) # (multi line) If it is not
        # (multi line) redirected here, previous data from previous
        # (multi Line) form remains, as render template is executed next.
    # print(form.errors)  --> prints the errors in forms
    return render_template('hospitalStaff/registerPatient.html',
                           title='registerPatient',
                           form=form,
                           linkRegisterPatient='active')


@hospitalStaff.route("/uploadPatientDocument", methods=['GET', 'POST'])
@login_required
@hospitalStaffAccessibleOnly
def uploadPatientDocument():
    form = UploadPatientDocumentForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(username=form.patientUsername.data).first()
        referenceDoctor = Doctor.query.filter_by(username=form.referenceDoctorUsername.data).first()
        if not patient or not referenceDoctor:
            if not patient:
                flash('Could not find the patient. Please check the Patient username', 'danger')
            if not referenceDoctor:
                flash('Could not find the doctor. Please check the Doctor username', 'danger')
            return render_template('hospitalStaff/uploadPatientDocument.html',
                                   form = form,
                                   title = 'Upload Patient Document',
                                   linkUploadPatientDocument = 'active')

        
        
        if not patient.patientDoctors.filter_by(id=referenceDoctor.id).first():
            flash('You cannot allow a Doctor to see a file if the Doctor is not assigned to the patient.', 'danger')
            return render_template('hospitalStaff/uploadPatientDocument.html',
                                   form=form,
                                   title='Upload Patient Document',
                                   linkUploadPatientDocument='active')

        uploadDocument(form.description.data,
                       form.file.data,
                       patient,
                       appValues['h'],
                       referenceDoctor.id,
                       referenceDoctor.name)

        return redirect(request.url)
    return render_template('hospitalStaff/uploadPatientDocument.html',
                                   form = form,
                                   title = 'Upload Patient Document',
                                   linkUploadPatientDocument = 'active')


@hospitalStaff.route("/userHospitalStaffInfo", methods=['GET', 'POST'])
@login_required
@hospitalStaffAccessibleOnly
def userHospitalStaffInfo():
    hospitalStaff = HospitalStaff.query.get_or_404(current_user.typeUserId)
    return render_template("hospitalStaff/userHospitalStaffInfo.html",
                           hospitalStaff = hospitalStaff,
                           linkUserInfo='active')


@hospitalStaff.route("/updateHospitalStaffInfo", methods=['GET', 'POST'])
@login_required
@hospitalStaffAccessibleOnly
def updateHospitalStaffInfo():
    hospitalStaff = HospitalStaff.query.get_or_404(current_user.typeUserId)
    form = UpdateHospitalStaffInfoForm()
    if form.validate_on_submit():
        hospitalStaff.username = form.username.data
        current_user.email = form.email.data
        hospitalStaff.name = form.name.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('hospitalStaff.userHospitalStaffInfo'))
    elif request.method == 'GET':
        form.username.data = hospitalStaff.username
        form.email.data = current_user.email
        form.name.data = hospitalStaff.name
    return render_template("hospitalStaff/updateHospitalStaffInfo.html",
                           form=form,
                           title='Update Information',
                           linkUserInfo='active')


@hospitalStaff.route("/deleteAccountConfirmation", methods=['GET', 'POST'])
@login_required
@hospitalStaffAccessibleOnly
def deleteAccountConfirmation():
    return render_template('hospitalStaff/deleteConfirmation.html',
                           linkUserInfo='active')


@hospitalStaff.route("/deleteAccount", methods=['GET', 'POST'])
@login_required
@hospitalStaffAccessibleOnly
def deleteAccount():
    hospitalStaff = HospitalStaff.query.get_or_404(current_user.typeUserId)
    logout_user()
    deleteHospitalStaffAccount(hospitalStaff)

    flash('Your Account has been deleted.', 'success')
    return redirect(url_for('commonFunctions.home'))