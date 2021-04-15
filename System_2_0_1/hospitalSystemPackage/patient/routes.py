import os, datetime
from functools import wraps
import jwt
from PIL import Image
import pdfkit
from flask import Blueprint, render_template, flash, redirect,\
    url_for, request, send_from_directory, abort, make_response
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from hospitalSystemPackage import db, app, appValues
from hospitalSystemPackage.models import User, Patient, \
    Document, Prescription, ValueInt, Doctor
from hospitalSystemPackage.patient.forms import UpdatePatientInfoForm, \
    DoctorConnectionForm
from hospitalSystemPackage.commonFunctions.forms import UploadFileForm, CommonSearchForm
from hospitalSystemPackage.commonFunctions.utils import randomSecretString,\
    randomSecretNumbers, getDocumentFromEncryptedId, encodeId, getNumberName,\
    getReturnPage, getFileFolder, getPrescriptionFromEncryptedId, \
    getDoctorFromEncryptedId
from hospitalSystemPackage.commonFunctions.deleteAccount import\
    deletePatientAccount
from hospitalSystemPackage.commonFunctions.userSpecifics import\
    deleteDocument, uploadDocument, deleteOneDocument

patient = Blueprint("patient", __name__)

def patientAccessibleOnly(originalFunction):

    @wraps(originalFunction)
    def wrapperFunction(*args, **kwargs):
        if current_user.userType == appValues['p']:
            return originalFunction(*args, **kwargs)
        else:
            flash('You are not allowed to visit this page.', 'danger')
            return redirect(url_for('commonFunctions.home'))

    return wrapperFunction



@patient.route("/doctorsPage")
@login_required
@patientAccessibleOnly
def doctorsPage():
    return render_template('patient/doctorPage.html', linkDoctors = 'active')


@patient.route("/doctors")
@login_required
@patientAccessibleOnly
def allDoctors():
    patient = Patient.query.get_or_404(current_user.typeUserId)

    page = request.args.get('page', 1, type=int)
    doctors = patient.patientDoctors.paginate(page=page, per_page=2)

    allData = []
    for doctor in doctors.items:
        allData.append((User.query.get(doctor.idFromUserModel).profileImage, doctor))

    return render_template("patient/allDoctors.html",
                           doctors = doctors,
                           allData = allData,
                           fromPage = page,
                           linkDoctors = 'active')


@patient.route("/searchDoctor", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def searchDoctor():
    form = CommonSearchForm()
    if form.validate_on_submit():
        if form.searchBy.data == 'username':
            doctors = Doctor.query. \
                filter(Doctor.username.startswith(form.searchName.data)).limit(2).all()

            allData = []
            for doctor in doctors:
                allData.append((User.query.get(doctor.idFromUserModel).profileImage, doctor))

        elif form.searchBy.data == 'name':
            doctors = Doctor.query. \
                filter(Doctor.name.startswith(form.searchName.data)).limit(2).all()

            allData = []
            for doctor in doctors:
                allData.append((User.query.get(doctor.idFromUserModel).profileImage, doctor))

        else:
            allData = []

        return render_template('patient/searchDoctor.html',
                               title='searchDoctor',
                               allData=allData,
                               form=form,
                               linkDoctors='active')

    return render_template('patient/searchDoctor.html',
                           title='searchDoctor',
                           form=form,
                           linkDoctors='active')


@patient.route("/disconnectDoctor", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def disconnectDoctor():
    form = DoctorConnectionForm()
    if form.validate_on_submit():

        doctor = Doctor.query.filter_by(username = form.username.data).first()

        if not doctor:
            flash('Could not find the doctor. Please check the username.', 'danger')
            return redirect(url_for('patient.disconnectDoctor'))

        patient = Patient.query.get(current_user.typeUserId)

        if patient.patientDoctors.filter_by(id = doctor.id).first():
            patient.patientDoctors.remove(doctor)
            db.session.commit()

            flash('Successfully disconnected doctor', 'success')
            return redirect(url_for('patient.allDoctors'))

        else:
            flash('This doctor is not connected to you.', 'info')
            return redirect(url_for('patient.disconnectDoctor'))

    return render_template('patient/doctorConnection.html',
                           loadedText='If you perform this action, '
                                    'This doctor cannot see any of your file or write prescription.'
                                    ' However, already written prescriptions and '
                                    'given files will not be deleted.',
                           form=form,
                           connect=False,
                           linkDoctors='active')


@patient.route("/directDisconnectDoctorConfirmation/<string:storedDoctorName>/"
               "<int:fromPage>/<int:itemNumber>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def directDisconnectDoctorConfirmation(storedDoctorName = None, fromPage = None, itemNumber = None):
    return render_template('patient/deleteConfirmation.html',
                           loadedText='If you perform this action, '
                                      'This doctor cannot see any of your file or write prescription.'
                                      ' However, already written prescriptions and '
                                      'given files will not be deleted.',
                           confirmationAbout='doctorConnection',
                           storedDoctorName=storedDoctorName,
                           fromPage=fromPage,
                           itemNumber=itemNumber,
                           linkDoctors='active')


@patient.route("/directDisconnectDoctor/<string:storedDoctorName>/"
               "<int:fromPage>/<int:itemNumber>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def directDisconnectDoctor(storedDoctorName = None, fromPage = None, itemNumber = None):

    doctor = getDoctorFromEncryptedId(storedDoctorName)

    if not doctor:
        flash('Could not find the doctor. Please check the username.', 'danger')
        return redirect(url_for('patient.allDoctors'))

    patient = Patient.query.get(current_user.typeUserId)

    if patient.patientDoctors.filter_by(id = doctor.id).first():
        patient.patientDoctors.remove(doctor)
        db.session.commit()

        flash('Successfully disconnected doctor', 'success')
        return redirect(url_for('patient.allDoctors', page = getReturnPage(fromPage, itemNumber)))

    else:
        flash('This doctor is not connected to you.', 'info')
        return redirect(url_for('patient.allDoctors', page = getReturnPage(fromPage, itemNumber)))


@patient.route("/allDocuments")
@login_required
@patientAccessibleOnly
def allDocuments():
    patient = Patient.query.get_or_404(current_user.typeUserId)

    page = request.args.get('page', 1, type=int)
    documents = patient.documents.order_by(Document.id.desc()).paginate(page=page, per_page=8)

    return render_template("patient/allDocuments.html",
                           documents = documents,
                           fromPage = page,
                           spaceUsed = patient.totalUsedSpace,
                           totalSpace = ValueInt.query.filter_by(variableName='spaceSize').first().variableValue,
                           linkAllDocuments = 'active')


@patient.route("/uploadFile", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def uploadFile():
    form = UploadFileForm()
    if form.validate_on_submit():
        if uploadDocument(form.description.data,
                          form.file.data,
                          Patient.query.get_or_404(current_user.typeUserId),
                          appValues['p']):
            return redirect(url_for('patient.allDocuments'))
        else:
            return redirect(url_for('patient.uploadFile'))

    patient = Patient.query.get(current_user.typeUserId)
    actualSize = ValueInt.query.filter_by(variableName='spaceSize').first().variableValue
    # actualSize = validSpaceSize.variableValue
    # print(actualSize)
    return render_template("patient/uploadFile.html",
                           form=form,
                           spaceUsed=patient.totalUsedSpace,
                           spaceTotal=actualSize,
                           title='Upload File',
                           linkAllDocuments='active')


@patient.route("/viewDetails/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def viewDetails(storedName=None):
    patient = Patient.query.get_or_404(current_user.typeUserId)
    document = getDocumentFromEncryptedId(storedName)
    if document and document.documentOwner == patient:
        _, fExt = os.path.splitext(document.document)
        return render_template('patient/viewDetails.html',
                               document=document,
                               patient=patient,
                               fExt=fExt,
                               linkAllDocuments='active')
    else:
        flash('File not found', 'danger')
        return redirect(url_for('patient.allDocuments'))


@patient.route("/connectDoctorDocument/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def connectDoctorDocument(storedName = None):
    form = DoctorConnectionForm()
    if form.validate_on_submit():
        document = getDocumentFromEncryptedId(storedName)
        patient = Patient.query.get(current_user.typeUserId)
        if not document or document.documentOwner != patient:
            flash('You cannot perform this action.', 'danger')
            return redirect(url_for('patient.allDocuments'))

        doctor = Doctor.query.filter_by(username = form.username.data).first()

        if not doctor:
            flash('Could not find the doctor. Please check the username.', 'danger')
            return redirect(url_for('patient.connectDoctorDocument', storedName = storedName))
        
        if not patient.patientDoctors.filter_by(id=doctor.id).first(): 
            flash('You cannot allow a Doctor to see a file if the Doctor is not assigned to you.', 'danger')
            return redirect(url_for('patient.connectDoctorDocument', storedName=storedName))

        if document.referenceDoctor == doctor.id:
            flash('This doctor can already see this file.', 'info')
            # return redirect(request.url) # Alternative to next line
            return redirect(url_for('patient.connectDoctorDocument', storedName=storedName))

        try:
            document.documentDoctors.append(doctor)
            db.session.commit()

            flash('Successfully connected doctor. Now doctor can see this file.', 'success')
            return redirect(url_for('patient.viewDetails', storedName = storedName))

        except:
            flash('This doctor can already see this file.', 'info')
            # return redirect(request.url)
            return redirect(url_for('patient.connectDoctorDocument', storedName = storedName))

    return render_template('patient/doctorConnection.html',
                           form=form,
                           connect=True,
                           linkAllDocuments='active')


@patient.route("/disconnectDoctorDocument/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def disconnectDoctorDocument(storedName = None):
    form = DoctorConnectionForm()
    if form.validate_on_submit():
        document = getDocumentFromEncryptedId(storedName)
        if not document or document.documentOwner != Patient.query.get(current_user.typeUserId):
            flash('You cannot perform this action.', 'danger')
            return redirect(url_for('patient.allDocuments'))

        doctor = Doctor.query.filter_by(username = form.username.data).first()

        if not doctor:
            flash('Could not find the doctor. Please check the username.', 'danger')
            return redirect(url_for('patient.disconnectDoctorDocument', storedName = storedName))

        if document.referenceDoctor == doctor.id:
            flash('You cannot disallow a doctor to see a file that is referenced to him.', 'info')
            return redirect(url_for('patient.disconnectDoctorDocument', storedName=storedName))

        try:
            document.documentDoctors.remove(doctor)
            db.session.commit()

            flash('Successfully disconnected doctor. Now doctor cannot see this file.', 'success')
            return redirect(url_for('patient.viewDetails', storedName = storedName))

        except:
            flash('This doctor cannot see this file.', 'info')
            return redirect(url_for('patient.disconnectDoctorDocument', storedName = storedName))

    return render_template('patient/doctorConnection.html',
                           form = form,
                           connect = False,
                           linkAllDocuments='active')


@patient.route("/directDisconnectDoctorDocument/<string:storedDoctorName>/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def directDisconnectDoctorDocument(storedDoctorName = None, storedName = None):
    document = getDocumentFromEncryptedId(storedName)

    if not document or document.documentOwner != Patient.query.get(current_user.typeUserId):
        flash('You cannot perform this action.', 'danger')
        return redirect(url_for('patient.allDocuments'))

    doctor = getDoctorFromEncryptedId(storedDoctorName)

    if not doctor:
        flash('Could not find the doctor. Please check the username.', 'danger')
        return redirect(url_for('patient.authorizedDocumentViewers', storedName=storedName))

    if document.referenceDoctor == doctor.id:
        flash('You cannot disallow a doctor to see a file that is referenced to him.', 'info')
        return redirect(url_for('patient.disconnectDoctorDocument', storedName=storedName))

    try:
        document.documentDoctors.remove(doctor)
        db.session.commit()

        flash('Successfully disconnected doctor. Now doctor cannot see this file.', 'success')
        return redirect(url_for('patient.authorizedDocumentViewers', storedName=storedName))

    except:

        flash('This doctor cannot see this file.', 'info')
        return redirect(url_for('patient.authorizedDocumentViewers', storedName=storedName))


@patient.route("/authorizedDocumentViewers/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def authorizedDocumentViewers(storedName = None):
    document = getDocumentFromEncryptedId(storedName)

    patient = Patient.query.get(current_user.typeUserId)

    if document and document.documentOwner == patient:
        documentReferenceUserType = None
        documentReferenceUser = None
        documentReferenceUserProfileImage = None

        if document.referenceDoctor:
            documentReferenceUserType = appValues['d']
            documentReferenceUser = Doctor.query.get(document.referenceDoctor)
            documentReferenceUserProfileImage = User.query.get(documentReferenceUser.idFromUserModel).profileImage
        elif document.postedBy == appValues['p']:
            documentReferenceUserType = appValues['p']
            documentReferenceUser = appValues['p']
            documentReferenceUserProfileImage = None
        else:
            documentReferenceUserType = None
            documentReferenceUser = None
            documentReferenceUserProfileImage = None

        authorizedDoctorViewers = document.documentDoctors.all()

        allData = []

        for doctor in authorizedDoctorViewers:
            allData.append((User.query.get(doctor.idFromUserModel).profileImage, doctor))

        return render_template('patient/authorizedDocumentViewers.html',
                               referenceUserType = documentReferenceUserType,
                               referenceUser = documentReferenceUser,
                               referenceUserProfileImage = documentReferenceUserProfileImage,
                               allData = allData,
                               storedName = document.documentIdEncrypted,
                               linkAllDocuments='active')

    else:
        flash('You cannot see this', 'danger')
        return redirect(url_for('patient.allDocuments')) 


@patient.route("/seeFile/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def seeFile(storedName = None):
    # patient = Patient.query.filter_by(idFromUserModel=current_user.id).first_or_404()
    patient = Patient.query.get_or_404(current_user.typeUserId)
    document = getDocumentFromEncryptedId(storedName)
    # if any(i.file == fileName for i in patient.documents.all()):
    if document and document.documentOwner == patient:
        folder = getFileFolder(document.document)

        return send_from_directory(os.path.join(app.root_path, 'userFiles/' + folder),
                                   filename=document.document,
                                   attachment_filename=document.actualDocumentName)
    else:
        flash('You are not allowed to see this File.', 'danger')
        return redirect(url_for('patient.allDocuments'))


@patient.route("/download/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def download(storedName):
    patient = Patient.query.get_or_404(current_user.typeUserId)
    document = getDocumentFromEncryptedId(storedName)
    # if any(i.file == fileName for i in patient.documents.all()):
    if document and document.documentOwner == patient:
        folder = getFileFolder(document.document)

        return send_from_directory(os.path.join(app.root_path, 'userFiles/' + folder),
                                   filename=document.document,
                                   as_attachment=True,
                                   attachment_filename=document.actualDocumentName)
    else:
        flash('You are not allowed to see this File.', 'danger')
        return redirect(url_for('patient.allDocuments'))


@patient.route("/deleteDocumentConfirmation/<string:storedName>/"
               "<int:fromPage>/<int:itemNumber>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def deleteDocumentConfirmation(storedName=None, fromPage=None, itemNumber=None):
    return render_template('patient/deleteConfirmation.html',
                           confirmationAbout='document',
                           storedName=storedName,
                           fromPage=fromPage,
                           itemNumber=itemNumber,
                           linkAllDocuments='active')


@patient.route("/deleteDocument/<string:storedName>/"
               "<int:fromPage>/<int:itemNumber>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def deleteDocument(storedName=None, fromPage=None, itemNumber=None):
    # patient = Patient.query.filter_by(idFromUserModel=current_user.id).first_or_404()
    patient = Patient.query.get_or_404(current_user.typeUserId)
    theDocument = getDocumentFromEncryptedId(storedName)

    if theDocument and theDocument.documentOwner == patient:
        # if any(i.file == fileName for i in patient.documents.all()):
        if deleteOneDocument(patient, theDocument):
            flash('Your file has been deleted', 'success')
            return redirect(url_for('patient.allDocuments', page = getReturnPage(fromPage, itemNumber)))
        else:
            flash('Something went wrong.', 'danger')
            return redirect(url_for('patient.allDocuments'))
    else:
        flash('You are not allowed to delete this File.', 'danger')
        return redirect(url_for('patient.allDocuments'))


@patient.route("/allPrescriptions")
@login_required
@patientAccessibleOnly
def allPrescriptions():
    patient = Patient.query.get_or_404(current_user.typeUserId)

    page = request.args.get('page', 1, type=int)
    prescriptions = patient.prescriptions.order_by(Prescription.id.desc()).paginate(page=page, per_page=8)

    return render_template("patient/allPrescriptions.html",
                           prescriptions=prescriptions,
                           fromPage=page,
                           linkAllPrescriptions='active')


@patient.route("/seePrescription/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def seePrescription(storedName):
    patient = Patient.query.get_or_404(current_user.typeUserId)
    prescription = getPrescriptionFromEncryptedId(storedName)
    if prescription and prescription.prescriptionOwner == patient:
        return render_template('patient/seePrescription.html',
                               patient=patient,
                               prescription=prescription,
                               linkAllPrescriptions='active')
    else:
        flash('Prescription not found', 'danger')
        return redirect(url_for('patient.allPrescriptions'))


@patient.route("/getPrescriptionAsPdf/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def getPrescriptionAsPdf(storedName):
    patient = Patient.query.get_or_404(current_user.typeUserId)
    prescription = getPrescriptionFromEncryptedId(storedName)
    if prescription and prescription.prescriptionOwner == patient:
        rendered =  render_template('patient/pdfPrescriptionTemplate.html',
                               patient = patient,
                               prescription=prescription)
        pdf = pdfkit.from_string(rendered, False)

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=' + prescription.description + '.pdf'

        return response

    else:
        flash('Prescription not found', 'danger')
        return redirect(url_for('patient.allPrescriptions'))



@patient.route("/connectDoctorPrescription/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def connectDoctorPrescription(storedName = None):
    form = DoctorConnectionForm()
    if form.validate_on_submit():
        prescription = getPrescriptionFromEncryptedId(storedName)
        patient = Patient.query.get(current_user.typeUserId)
        if not prescription or prescription.prescriptionOwner != patient:
            flash('You cannot perform this action.', 'danger')
            return redirect(url_for('patient.allPrescriptions'))

        doctor = Doctor.query.filter_by(username = form.username.data).first()

        if not doctor:
            flash('Could not find the doctor. Please check the username.', 'danger')
            # return redirect(request.url)
            return redirect(url_for('patient.connectDoctorPrescription', storedName = storedName))
        
        if not patient.patientDoctors.filter_by(id=doctor.id).first():
            flash('You cannot allow a Doctor to see a file if the Doctor is not assigned to you.', 'danger')
            return redirect(url_for('patient.connectDoctorDocument', storedName=storedName))

        if prescription.referenceDoctor == doctor.id:
            flash('This doctor can already see this file.', 'info')
            # return redirect(request.url) # Alternative to next line
            return redirect(url_for('patient.connectDoctorPrescription', storedName=storedName))

        try:
            prescription.prescriptionDoctors.append(doctor)
            db.session.commit()

            flash('Successfully connected doctor. Now doctor can see this file.', 'success')
            return redirect(url_for('patient.seePrescription', storedName = storedName))

        except:
            flash('This doctor can already see this file.', 'info')
            # return redirect(request.url)
            return redirect(url_for('patient.connectDoctorPrescription', storedName=storedName))

    return render_template('patient/doctorConnection.html',
                           form=form,
                           connect=True,
                           linkAllPrescriptions='active')


@patient.route("/disconnectDoctorPrescription/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def disconnectDoctorPrescription(storedName = None):
    form = DoctorConnectionForm()
    if form.validate_on_submit():
        prescription = getPrescriptionFromEncryptedId(storedName)
        if not prescription or prescription.prescriptionOwner != Patient.query.get(current_user.typeUserId):
            flash('You cannot perform this action.', 'danger')
            return redirect(url_for('patient.allPrescriptions'))

        doctor = Doctor.query.filter_by(username = form.username.data).first()

        if not doctor:
            flash('Could not find the doctor. Please check the username.', 'danger')
            return redirect(url_for('patient.disconnectDoctorPrescription', storedName = storedName))

        if prescription.referenceDoctor == doctor.id:
            flash('You cannot disallow a doctor to see a prescription that is referenced to him.', 'info')
            return redirect(url_for('patient.disconnectDoctorPrescription', storedName=storedName))

        try:
            prescription.prescriptionDoctors.remove(doctor)
            db.session.commit()

            flash('Successfully disconnected doctor. Now doctor cannot see this prescription.', 'success')
            return redirect(url_for('patient.seePrescription', storedName = storedName))

        except:
            flash('This doctor cannot see this file.', 'info')
            return redirect(url_for('patient.disconnectDoctorPrescription', storedName=storedName))

    return render_template('patient/doctorConnection.html',
                           form=form,
                           connect=False,
                           linkAllPrescriptions='active')


@patient.route("/directDisconnectDoctorPrescription/<string:storedDoctorName>/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def directDisconnectDoctorPrescription(storedDoctorName = None, storedName = None):
    prescription = getPrescriptionFromEncryptedId(storedName)

    if not prescription or prescription.prescriptionOwner != Patient.query.get(current_user.typeUserId):
        flash('You cannot perform this action.', 'danger')
        return redirect(url_for('patient.allPrescriptions'))

    doctor = getDoctorFromEncryptedId(storedDoctorName)

    if not doctor:
        flash('Could not find the doctor. Please check the username.', 'danger')
        return redirect(url_for('patient.authorizedPrescriptionViewers', storedName=storedName))

    if prescription.referenceDoctor == doctor.id:
        flash('You cannot disallow a doctor to see a prescription that is referenced to him.', 'info')
        return redirect(url_for('patient.disconnectDoctorPrescription', storedName=storedName))

    try:
        prescription.prescriptionDoctors.remove(doctor)
        db.session.commit()

        flash('Successfully disconnected doctor. Now doctor cannot see this file.', 'success')
        return redirect(url_for('patient.authorizedPrescriptionViewers', storedName=storedName))

    except:

        flash('This doctor cannot see this file.', 'info')
        return redirect(url_for('patient.authorizedPrescriptionViewers', storedName=storedName))


@patient.route("/authorizedPrescriptionViewers/<string:storedName>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def authorizedPrescriptionViewers(storedName = None):
    prescription = getPrescriptionFromEncryptedId(storedName)

    patient = Patient.query.get(current_user.typeUserId)

    if prescription and prescription.prescriptionOwner == patient:
        prescriptionReferenceUser = None
        prescriptionReferenceUserProfileImage = None

        if prescription.referenceDoctor:
            prescriptionReferenceUser = Doctor.query.get(prescription.referenceDoctor)
            prescriptionReferenceUserProfileImage = User.query.get(prescriptionReferenceUser.idFromUserModel).profileImage
        else:
            prescriptionReferenceUser = None
            prescriptionReferenceUserProfileImage = None

        authorizedDoctorViewers = prescription.prescriptionDoctors.all()

        allData = []

        for doctor in authorizedDoctorViewers:
            allData.append((User.query.get(doctor.idFromUserModel).profileImage, doctor))

        return render_template('patient/authorizedPrescriptionViewers.html',
                               referenceUser=prescriptionReferenceUser,
                               referenceUserProfileImage=prescriptionReferenceUserProfileImage,
                               allData=allData,
                               storedName=prescription.prescriptionIdEncrypted,
                               linkAllPrescriptions='active')

    else:
        flash('You cannot see this', 'danger')
        return redirect(url_for('patient.allPrescriptions'))  


@patient.route("/deletePrescriptionConfirmation/<string:storedName>/"
               "<int:fromPage>/<int:itemNumber>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def deletePrescriptionConfirmation(storedName=None, fromPage=None, itemNumber=None):
    return render_template('patient/deleteConfirmation.html',
                           confirmationAbout='prescription',
                           storedName=storedName,
                           fromPage=fromPage,
                           itemNumber=itemNumber,
                           linkAllPrescriptions='active')


@patient.route("/deletePrescription/<string:storedName>/"
               "<int:fromPage>/<int:itemNumber>", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def deletePrescription(storedName=None, fromPage=None, itemNumber=None):
    patient = Patient.query.get_or_404(current_user.typeUserId)
    thePrescription = getPrescriptionFromEncryptedId(storedName)

    if thePrescription and thePrescription.prescriptionOwner == patient:

        db.session.delete(thePrescription)
        db.session.commit()

        flash('Successfully deleted Prescription', 'success')
        return redirect(url_for('patient.allPrescriptions', page=getReturnPage(fromPage, itemNumber)))

    else:
        flash('You are not allowed to delete this File.', 'danger')
        return redirect(url_for('patient.allPrescriptions'))


@patient.route("/userPatientInfo")
@login_required
@patientAccessibleOnly
def userPatientInfo():
    patient = Patient.query.get_or_404(current_user.typeUserId)
    return render_template("patient/userPatientInfo.html",
                           patient=patient,
                           linkUserInfo='active')


@patient.route("/updatePatientInfo", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def updatePatientInfo():
    patient = Patient.query.get_or_404(current_user.typeUserId)
    form = UpdatePatientInfoForm()
    if form.validate_on_submit():
        patient.username = form.username.data
        current_user.email = form.email.data
        patient.name = form.name.data

        patient.age = form.age.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('patient.userPatientInfo'))
    elif request.method == 'GET':
        form.username.data = patient.username
        form.email.data = current_user.email
        form.name.data = patient.name
        form.age.data = patient.age
    return render_template("patient/updatePatientInfo.html",
                           form=form,
                           title='Update Information',
                           linkUserInfo='active')


@patient.route("/deleteAccountConfirmation", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def deleteAccountConfirmation():
    return render_template('patient/deleteConfirmation.html',
                           confirmationAbout='account',
                           linkUserInfo='active')


@patient.route("/deleteAccount", methods=['GET', 'POST'])
@login_required
@patientAccessibleOnly
def deleteAccount():
    patient = Patient.query.get_or_404(current_user.typeUserId)
    logout_user()
    deletePatientAccount(patient)

    flash('Your Account has been deleted.', 'success')
    return redirect(url_for('commonFunctions.home'))