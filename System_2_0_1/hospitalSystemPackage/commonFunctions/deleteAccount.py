import string, secrets, jwt, os, sys
from hospitalSystemPackage import db, app
from hospitalSystemPackage.models import ValueInt,\
    ValueString, Document, Patient, Doctor,\
    HospitalStaff, User
from hospitalSystemPackage.commonFunctions.userSpecifics import \
    deleteDocument, deleteMultipleDocuments


def deletePatientAccount(patient):
    user = User.query.get_or_404(patient.idFromUserModel)
    documents = patient.documents.all()

    deleteMultipleDocuments(patient, documents)

    if user.profileImage != 'default.png':
        os.remove(os.path.join(app.root_path, 'userFiles/profileImages', user.profileImage))

    patient.prescriptions.delete()

    db.session.delete(patient)
    db.session.delete(user)
    db.session.commit()


def deleteHospitalStaffAccount(hospitalStaff):
    user = User.query.get_or_404(hospitalStaff.idFromUserModel)

    if user.profileImage != 'default.png':
        os.remove(os.path.join(app.root_path, 'userFiles/profileImages', user.profileImage))

    db.session.delete(hospitalStaff)
    db.session.delete(user)
    db.session.commit()


def deleteDoctorAccount(doctor):
    user = User.query.get_or_404(doctor.idFromUserModel)

    # Document.query.filter_by(referenceDoctor = doctor.id).update({'referenceDoctor' : None})
    Document.query.filter_by(referenceDoctor = doctor.id).update({Document.referenceDoctor : None})

    if user.profileImage != 'default.png':
        os.remove(os.path.join(app.root_path, 'userFiles/profileImages', user.profileImage))

    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()


def deleteAdminAccount(admin):
    user = User.query.get_or_404(admin.idFromUserModel)

    if user.profileImage != 'default.png':
        os.remove(os.path.join(app.root_path, 'userFiles/profileImages', user.profileImage))

    db.session.delete(admin)
    db.session.delete(user)
    db.session.commit()
