import datetime
import jwt
from flask import url_for
from flask_login import UserMixin
from hospitalSystemPackage import db, app, login_manager

DoctorAndPatient = db.Table('doctor_and_patient',
                db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id'), primary_key=True),
                db.Column('patient_id', db.Integer, db.ForeignKey('patient.id'), primary_key=True)
)

DoctorAndDocument = db.Table('doctor_and_document',
                db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id'), primary_key=True),
                db.Column('document_id', db.Integer, db.ForeignKey('document.id'), primary_key=True)
)

DoctorAndPrescription = db.Table('doctor_and_prescription',
                db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id'), primary_key=True),
                db.Column('prescription_id', db.Integer, db.ForeignKey('prescription.id'), primary_key=True)
)


@login_manager.user_loader
def loadUser(userId):
    return User.query.get(int(userId))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    userType = db.Column(db.String(20), nullable=False)

    profileImage = db.Column(db.String(120), nullable=False, default='default.png')
    password = db.Column(db.String(120), nullable=False)
    passwordChangeCode = db.Column(db.String(20), nullable=False)
    userToken = db.Column(db.String(20), nullable=False)

    typeUserId = db.Column(db.Integer)

    def __repr__(self):
        return f"User('{self.id}', '{self.email}', '{self.profileImage}')"


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    idFromUserModel = db.Column(db.Integer, unique=True, nullable=False)
    patientIdEncrypted = db.Column(db.String(241))

    totalUsedSpace = db.Column(db.Integer, nullable=False)
    
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # aboutPatient = db.Column(db.String(200))

    documents = db.relationship('Document', backref='documentOwner', lazy='dynamic')
    prescriptions = db.relationship('Prescription', backref='prescriptionOwner', lazy='dynamic')

    def __repr__(self):
        return f"Patient('{self.username}')"


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    documentIdEncrypted = db.Column(db.String(241))

    description = db.Column(db.String(60))
    postedBy = db.Column(db.String(15), nullable=False)
    postDate = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    document = db.Column(db.String(40), nullable=False)
    actualDocumentName = db.Column(db.String(60), nullable=False)
    documentSize = db.Column(db.Integer, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    referenceDoctor = db.Column(db.Integer)
    referenceDoctorName = db.Column(db.String(120))

    def __repr__(self):
        return f"Document('{self.description}', '{self.postDate}', {self.document})"


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescriptionIdEncrypted = db.Column(db.String(241))

    description = db.Column(db.String(60))
    postDate = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    material = db.Column(db.Text, nullable = False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    referenceDoctor = db.Column(db.Integer)
    referenceDoctorName = db.Column(db.String(120))

    def __repr__(self):
        return f"Prescription('{self.description}', '{self.postDate}')"


class HospitalStaff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    idFromUserModel = db.Column(db.Integer, unique=True, nullable=False)
    hospitalStaffIdEncrypted = db.Column(db.String(241))

    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"HospitalStaff('{self.username}')"


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    idFromUserModel = db.Column(db.Integer, unique=True, nullable=False)
    doctorIdEncrypted = db.Column(db.String(241))

    name = db.Column(db.String(120), nullable=False)
    field = db.Column(db.String(20), nullable=False)

    # Many to Many
    doctorPatients = db.relationship('Patient',
                                    secondary=DoctorAndPatient,
                                    lazy='dynamic',
                                    backref=db.backref('patientDoctors', lazy='dynamic'))

    # Many to Many
    doctorDocuments = db.relationship('Document',
                                    secondary=DoctorAndDocument,
                                    lazy='dynamic',
                                    backref=db.backref('documentDoctors', lazy='dynamic'))

    # Many to Many
    doctorPrescriptions = db.relationship('Prescription',
                                    secondary=DoctorAndPrescription,
                                    lazy='dynamic',
                                    backref=db.backref('prescriptionDoctors', lazy='dynamic'))

    def __repr__(self):
        return f"Doctor('{self.username}', '{self.field}')"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    idFromUserModel = db.Column(db.Integer, unique=True, nullable=False)
    adminIdEncrypted = db.Column(db.String(241))

    name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(20))

    def __repr__(self):
        return f"Admin('{self.idFromUserModel}', '{self.title}')"


class ValueInt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    variableName = db.Column(db.String(60)) # Maybe it can be unique
    variableValue = db.Column(db.Integer, nullable=False)
    

    def __repr__(self):
        return f"ValueInt('{self.variableName}', '{self.variableValue}')"


class ValueString(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    variableName = db.Column(db.String(60)) # Maybe it can be unique
    variableValue = db.Column(db.String(60))

    
    def __repr__(self):
        return f"ValueString('{self.variableName}', '{self.variableValue}')"