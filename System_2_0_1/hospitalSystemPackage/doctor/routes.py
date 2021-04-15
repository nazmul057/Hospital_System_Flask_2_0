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
from hospitalSystemPackage.models import User, Patient, Document, \
    ValueInt, Doctor, HospitalStaff, Prescription
from hospitalSystemPackage.commonFunctions.utils import randomSecretString,\
    randomSecretNumbers, getDocumentFromEncryptedId, encodeId, getNumberName,\
    getReturnPage, getFileFolder, getPatientFromEncryptedId, getPrescriptionFromEncryptedId
from hospitalSystemPackage.commonFunctions.deleteAccount import\
    deleteDoctorAccount
from hospitalSystemPackage.commonFunctions.userSpecifics import\
    deleteDocument, uploadDocument
from hospitalSystemPackage.commonFunctions.forms import CommonSearchForm, UploadFileForm
from hospitalSystemPackage.doctor.forms import PrescriptionForm, UpdateDoctorInfoForm



doctor = Blueprint("doctor", __name__)


def doctorAccessibleOnly(originalFunction):

    @wraps(originalFunction)
    def wrapperFunction(*args, **kwargs):
        if current_user.userType == appValues['d']:
            return originalFunction(*args, **kwargs)
        else:
            flash('You are not allowed to visit this page.', 'danger')
            return redirect(url_for('commonFunctions.home'))

    return wrapperFunction


@doctor.route("/mainPage", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def mainPage():
    return render_template('doctor/mainPage.html', title = 'Patients', linkMainPage = 'active')


@doctor.route("/patientInfo/<string:storedPatientName>", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def patientInfo(storedPatientName = None):

    patient = getPatientFromEncryptedId(storedPatientName)

    
    
    if patient == None or patient.patientDoctors.filter_by(id = current_user.typeUserId).first() == None:
        flash('You cannot see this patient Information.', 'danger')
        return redirect(url_for('doctor.mainPage'))

    user = User.query.get(patient.idFromUserModel)

    return render_template('doctor/patientInfo.html',
                           title = 'patientInfo',
                           user = user,
                           patient = patient,
                           linkMainPage = 'active')


@doctor.route("/patientDocuments/<string:storedPatientName>", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def patientDocuments(storedPatientName = None):

    patient = getPatientFromEncryptedId(storedPatientName)

    if patient == None or patient.patientDoctors.filter_by(id = current_user.typeUserId).first() == None:
        flash('You cannot see this patient Information', 'danger')
        return redirect(url_for('doctor.mainPage'))

    page = request.args.get('page', 1, type=int)

    documents = patient.documents. \
        filter_by(referenceDoctor = current_user.typeUserId). \
        order_by(Document.id.desc()).paginate(page=page, per_page=2) 

    return render_template('doctor/patientHistory.html',
                           type = 'document',
                           documents = documents,
                           refCount=(page - 1) * 2,
                           patientIdEncrypted = patient.patientIdEncrypted,
                           linkMainPage = 'active')


@doctor.route("/particularDocument/<string:storedName>", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def particularDocument(storedName = None):
    document = getDocumentFromEncryptedId(storedName)

    if document and document.referenceDoctor == current_user.typeUserId:
        patient = document.documentOwner
        return render_template('doctor/document.html',
                               fExt = os.path.splitext(document.document)[1],
                               patient = patient,
                               document = document,
                               linkMainPage = 'active')

    elif document.documentDoctors.filter_by(id=current_user.typeUserId).first():
        
        
        patient = document.documentOwner
        return render_template('doctor/document.html',
                               fExt = os.path.splitext(document.document)[1],
                               patient = patient,
                               document = document,
                               linkMainPage = 'active')

    else:
        flash('You are not allowed to see this.', 'danger')
        return redirect(url_for('doctor.mainPage'))


@doctor.route("/patientAccessedDocuments/<string:storedPatientName>", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def patientAccessedDocuments(storedPatientName = None):

    patient = getPatientFromEncryptedId(storedPatientName)

    if patient == None or patient.patientDoctors.filter_by(id=current_user.typeUserId).first() == None:
        flash('You cannot see this patient Information', 'danger')
        return redirect(url_for('doctor.mainPage'))

    page = request.args.get('page', 1, type=int)

    # any() documentation here = https://docs.sqlalchemy.org/en/13/orm/internals.html
    documents = patient.documents. \
        filter(Document.documentDoctors.any(id = current_user.typeUserId)). \
        order_by(Document.id.desc()).paginate(page=page, per_page=2)
    # doctor = Doctor.query.get(current_user.typeUserId)
    # documents = doctor.doctorDocuments.filter_by(patient_id = patient.id). \
        # order_by(Document.id.desc()).paginate(page=page, per_page=2)

    return render_template('doctor/patientHistoryAccessed.html',
                           type='document',
                           documents=documents,
                           refCount=(page - 1) * 2,
                           patientIdEncrypted=patient.patientIdEncrypted,
                           linkMainPage = 'active')


@doctor.route("/seeFile/<string:storedName>", methods=['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def seeFile(storedName = None):
    document = getDocumentFromEncryptedId(storedName)

    if document and document.referenceDoctor == current_user.typeUserId:

        folder = getFileFolder(document.document)

        return send_from_directory(os.path.join(app.root_path, 'userFiles/' + folder),
                                   filename=document.document,
                                   attachment_filename=document.actualDocumentName)

    elif document.documentDoctors.filter_by(id=current_user.typeUserId).first():

        folder = getFileFolder(document.document)

        return send_from_directory(os.path.join(app.root_path, 'userFiles/' + folder),
                                   filename=document.document,
                                   attachment_filename=document.actualDocumentName)

    else:
        flash('You are not allowed to see this File.', 'danger')
        return redirect(url_for('doctor.mainPage'))


@doctor.route("/newDocument/<string:storedPatientName>", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def newDocument(storedPatientName = None):
    patient = getPatientFromEncryptedId(storedPatientName)
    if patient == None:
        flash('Could not find patient.', 'danger')
        return redirect(url_for('doctor.mainPage'))
        # redirecting here to url_for('doctor.newDocument', storedPatientName = storedPatientName) here results
        # in an infinite loop if patient = None

    form = UploadFileForm()
    if form.validate_on_submit():

        if patient.patientDoctors.filter_by(id=current_user.typeUserId).first() == None:
            flash('You cannot see this patient Information', 'danger')
            return redirect(url_for('doctor.mainPage'))

        uploadDocument(form.description.data,
                        form.file.data,
                        patient,
                        appValues['d'],
                        current_user.typeUserId,
                        Doctor.query.get(current_user.typeUserId).name)

        return redirect(url_for('doctor.patientDocuments',
                                storedPatientName = patient.patientIdEncrypted))

    return render_template("doctor/newDocument.html",
                           patient=patient,
                           form = form,
                           title = 'Upload Document',
                           linkMainPage = 'active')


@doctor.route("/patientPrescriptions/<string:storedPatientName>", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def patientPrescriptions(storedPatientName = None):

    patient = getPatientFromEncryptedId(storedPatientName)

    if patient == None or patient.patientDoctors.filter_by(id = current_user.typeUserId).first() == None:
        flash('You cannot see this patient Information', 'danger')
        return redirect(url_for('doctor.mainPage'))

    page = request.args.get('page', 1, type=int)

    prescriptions = patient.prescriptions. \
        filter_by(referenceDoctor = current_user.typeUserId). \
        order_by(Prescription.id.desc()).paginate(page=page, per_page=2) 

    return render_template('doctor/patientHistory.html',
                           type = 'prescription',
                           prescriptions = prescriptions,
                           refCount=(page - 1) * 2,
                           patientIdEncrypted = patient.patientIdEncrypted,
                           linkMainPage = 'active')


@doctor.route("/particularPrescription/<string:storedName>", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def particularPrescription(storedName = None):
    prescription = getPrescriptionFromEncryptedId(storedName)

    if prescription and prescription.referenceDoctor == current_user.typeUserId:
        patient = prescription.prescriptionOwner
        return render_template('doctor/prescription.html',
                               patient = patient,
                               prescription = prescription,
                               linkMainPage = 'active')

    elif prescription.prescriptionDoctors.filter_by(id = current_user.typeUserId).first():
        patient = prescription.prescriptionOwner
        return render_template('doctor/prescription.html',
                               patient = patient,
                               prescription = prescription,
                               linkMainPage = 'active')

    else:
        flash('You are not allowed to see this.', 'danger')
        return redirect(url_for('doctor.mainPage'))


@doctor.route("/patientAccessedPrescriptions/<string:storedPatientName>", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def patientAccessedPrescriptions(storedPatientName = None):

    patient = getPatientFromEncryptedId(storedPatientName)

    if patient == None or patient.patientDoctors.filter_by(id=current_user.typeUserId).first() == None:
        flash('You cannot see this patient Information', 'danger')
        return redirect(url_for('doctor.mainPage'))

    page = request.args.get('page', 1, type=int)

    # any() documentation here = https://docs.sqlalchemy.org/en/13/orm/internals.html
    prescriptions = patient.prescriptions. \
        filter(Prescription.prescriptionDoctors.any(id = current_user.typeUserId)). \
        order_by(Prescription.id.desc()).paginate(page=page, per_page=2)
    # doctor = Doctor.query.get(current_user.typeUserId)
    # documents = doctor.doctorDocuments.filter_by(patient_id = patient.id). \
        # order_by(Document.id.desc()).paginate(page=page, per_page=2)

    return render_template('doctor/patientHistoryAccessed.html',
                           type = 'prescription',
                           prescriptions = prescriptions,
                           refCount = (page - 1) * 2,
                           patientIdEncrypted = patient.patientIdEncrypted,
                           linkMainPage = 'active')


@doctor.route("/newPrescriptions/<string:storedPatientName>", methods = ['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def newPrescription(storedPatientName = None):
    patient = getPatientFromEncryptedId(storedPatientName)
    if patient == None:
        flash('Could not find patient.', 'danger')
        return redirect(url_for('doctor.mainPage'))

    form = PrescriptionForm()
    if form.validate_on_submit():

        if patient == None or patient.patientDoctors.filter_by(id = current_user.typeUserId).first() == None:
            flash('You cannot see this patient Information', 'danger')
            return redirect(url_for('doctor.mainPage'))

        prescription = Prescription(description = form.description.data,
                                    material = form.material.data,
                                    prescriptionOwner = patient,
                                    referenceDoctor = current_user.typeUserId,
                                    referenceDoctorName = Doctor.query.get(current_user.typeUserId).name)
        db.session.add(prescription)
        db.session.commit()

        prescription.prescriptionIdEncrypted = encodeId(prescription.id)

        db.session.commit()
        flash('Prescription Set', 'success')
        return redirect(url_for('doctor.patientPrescriptions',
                                storedPatientName = patient.patientIdEncrypted))

    return render_template("doctor/newPrescription.html",
                           patient = patient,
                           form = form,
                           title = 'Update Information',
                           linkMainPage = 'active')


@doctor.route("/searchPatient", methods=['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def searchPatient():
    form = CommonSearchForm()
    if form.validate_on_submit():
        doctor = Doctor.query.get(current_user.typeUserId)
        if form.searchBy.data == 'username':
            patients = doctor.doctorPatients. \
                filter(Patient.username.startswith(form.searchName.data)).limit(2).all()

        elif form.searchBy.data == 'name':
            patients = doctor.doctorPatients. \
                filter(Patient.name.startswith(form.searchName.data)).limit(2).all()

        else:
            patients = [] 

        return render_template('doctor/searchPatient.html',
                               title = 'searchPatient',
                               patients = patients,
                               form = form,
                               linkMainPage = 'active')

    return render_template('doctor/searchPatient.html',
                           title = 'searchPatient',
                           form = form,
                           linkMainPage = 'active')


@doctor.route("/allPatients", methods=['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def allPatients():
    doctor = Doctor.query.get_or_404(current_user.typeUserId)

    page = request.args.get('page', 1, type=int)
    patients = doctor.doctorPatients.paginate(page=page, per_page=2)

    return render_template("doctor/allPatients.html",
                           patients = patients,
                           linkMainPage = 'active')


@doctor.route("/userDoctorInfo")
@login_required
@doctorAccessibleOnly
def userDoctorInfo():
    doctor = Doctor.query.get_or_404(current_user.typeUserId)
    return render_template("doctor/userDoctorInfo.html",
                           doctor = doctor,
                           linkUserInfo = 'active')


@doctor.route("/updateDoctorInfo", methods=['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def updateDoctorInfo():
    doctor = Doctor.query.get_or_404(current_user.typeUserId)
    form = UpdateDoctorInfoForm()
    if form.validate_on_submit():
        doctor.username = form.username.data
        current_user.email = form.email.data
        doctor.name = form.name.data

        doctor.field = form.field.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('doctor.userDoctorInfo'))
    elif request.method == 'GET':
        form.username.data = doctor.username
        form.email.data = current_user.email
        form.name.data = doctor.name
        form.field.data = doctor.field
    return render_template("doctor/updateDoctorInfo.html",
                           form=form,
                           title='Update Information',
                           linkUserInfo='active')


@doctor.route("/deleteAccountConfirmation", methods=['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def deleteAccountConfirmation():
    return render_template('doctor/deleteConfirmation.html',
                           loadedText = 'All your information will be removed.',
                           linkUserInfo='active')


@doctor.route("/deleteAccount", methods=['GET', 'POST'])
@login_required
@doctorAccessibleOnly
def deleteAccount():
    doctor = Doctor.query.get_or_404(current_user.typeUserId)
    logout_user()
    deleteDoctorAccount(doctor)

    flash('Your Account has been deleted.', 'success')
    return redirect(url_for('commonFunctions.home'))