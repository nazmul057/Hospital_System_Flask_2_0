import string, secrets, jwt, os, sys, datetime
from cryptography.fernet import Fernet
from flask import url_for
from flask_mail import Message
from hospitalSystemPackage import db, app, appValues, mail
from hospitalSystemPackage.models import ValueInt,\
    ValueString, Document, Patient, Doctor, HospitalStaff, \
    Admin, Prescription, User



def sendResetEmailForTest(user = None, forgot = True):
    if user == None:
        return False

    token = None
    if forgot:
        token = getResetToken(user)
    else:
        token = getActivationToken(user)

    user.passwordChangeCode = randomSecretCode()
    db.session.commit()

    print('This is the email reset link with token:')
    print(url_for('commonFunctions.passwordReset', token=token, _external=True))
    print('Just a gap')
    print('This is the password change code:')
    print(user.passwordChangeCode)
    print('Just a gap 2')
    return True



def sendResetEmail(user = None, forgot = True):
    if user == None:
        return False

    token = None
    if forgot:
        token = getResetToken(user)
    else:
        token = getActivationToken(user)

    user.passwordChangeCode = randomSecretCode()
    db.session.commit()

    msg = Message('Password Set Request',
                  sender='hospitalSystem@demo.com',
                  recipients=[user.email])

    msg.body = f'''To set or reset password, visit the following link:

{url_for('commonFunctions.passwordReset', token=token, _external=True)}

This following code is necessary to reset password. Just copy and paste this code in the password reset form, where it is asked.
Your Password reset code is: {user.passwordChangeCode}

If you did not make this request then simply ignore this email.
'''
    mail.send(msg)
    return True


def getActivationToken(user):
    f = Fernet(appValues['cryptoKey'])
    encrypted = f.encrypt(str(user.id).encode())
    token = jwt.encode({'id': encrypted.hex(),
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)},
                       app.config['SECRET_KEY'])
    return token.decode('UTF-8')


def getResetToken(user):
    f = Fernet(appValues['cryptoKey'])
    encrypted = f.encrypt(str(user.id).encode())
    token = jwt.encode({'id': encrypted.hex(),
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                       app.config['SECRET_KEY'])
    return token.decode('UTF-8')


def verifyToken(token=None):
    if token == None:
        return None
    try:
        f = Fernet(appValues['cryptoKey'])
        data = jwt.decode(token, app.config['SECRET_KEY'])
        userIdEncryptedHex = data['id']
        userIdEncryptedBytes = bytes.fromhex(userIdEncryptedHex)
        userId = int(f.decrypt(userIdEncryptedBytes).decode())
        return User.query.get(userId)
    except:
        return None


def randomSecretString(length=8):
    return ''.join(secrets.choice(string.ascii_lowercase) # string.digits
                  for i in range(length))


def randomSecretCode(length=10):
    return ''.join(secrets.choice(string.ascii_letters + string.digits)
                  for i in range(length))


def randomSecretNumbers(length=8):
    return ''.join(secrets.choice(string.digits)
                  for i in range(length))


def getPatientFromEncryptedId(encryptedId):
    try:
        f = Fernet(appValues['cryptoKey'])
        patientIdEncrypted = bytes.fromhex(encryptedId)
        patientId = int(f.decrypt(patientIdEncrypted).decode())
        # print(patientId)
        # print(type(patientId))
        patient = Patient.query.get(patientId)
    except:
        patient = None
    return patient


def getHospitalStaffFromEncryptedId(encryptedId):
    try:
        f = Fernet(appValues['cryptoKey'])
        hospitalStaffIdEncrypted = bytes.fromhex(encryptedId)
        hospitalStaffId = int(f.decrypt(hospitalStaffIdEncrypted).decode())
        # print(hospitalStaffId)
        # print(type(hospitalStaffId))
        hospitalStaff = HospitalStaff.query.get(hospitalStaffId)
    except:
        hospitalStaff = None
    return hospitalStaff


def getDoctorFromEncryptedId(encryptedId):
    try:
        f = Fernet(appValues['cryptoKey'])
        doctorIdEncrypted = bytes.fromhex(encryptedId)
        doctorId = int(f.decrypt(doctorIdEncrypted).decode())
        # print(doctorId)
        # print(type(doctorId))
        doctor = Doctor.query.get(doctorId)
    except:
        doctor = None
    return doctor


def getAdminFromEncryptedId(encryptedId):
    try:
        f = Fernet(appValues['cryptoKey'])
        adminIdEncrypted = bytes.fromhex(encryptedId)
        adminId = int(f.decrypt(adminIdEncrypted).decode())
        # print(adminId)
        # print(type(adminId))
        admin = Admin.query.get(adminId)
    except:
        admin = None
    return admin


def getDocumentFromEncryptedId(encryptedId):
    try:
        f = Fernet(appValues['cryptoKey'])
        documentIdEncrypted = bytes.fromhex(encryptedId)
        documentId = int(f.decrypt(documentIdEncrypted).decode())
        # print(documentId)
        # print(type(documentId))
        document = Document.query.get(documentId)
    except:
        document = None
    return document


def getPrescriptionFromEncryptedId(encryptedId):
    try:
        f = Fernet(appValues['cryptoKey'])
        prescriptionIdEncrypted = bytes.fromhex(encryptedId)
        prescriptionId = int(f.decrypt(prescriptionIdEncrypted).decode())
        # print(prescriptionId)
        # print(type(prescriptionId))
        prescription = Prescription.query.get(prescriptionId)
    except:
        prescription = None
    return prescription


def getNumberName(fromHere):
    fromDb = ValueString.query.filter_by(variableName=fromHere).first()
    toBeReturned = str(int(fromDb.variableValue) + 1)
    fromDb.variableValue = toBeReturned
    db.session.commit()
    return toBeReturned


def encodeId(id):
    f = Fernet(appValues['cryptoKey'])
    encoded = f.encrypt(str(id).encode())
    # print()
    # print(sys.getsizeof(app)) # size = 56
    # print(sys.getsizeof(db)) # size = 56
    # print(sys.getsizeof(string)) # size = 80
    return encoded.hex()


def getReturnPage(fromPage=None, itemNumber=None):

    if fromPage == None or itemNumber == None:
        return 1

    if fromPage != 1 and itemNumber == 1:
        return fromPage-1
    elif fromPage != 1 and itemNumber != 1:
        return fromPage
    else:
        return 1


def getFileFolder(documentName):
    _, fExt = os.path.splitext(documentName)
    if fExt == '.pdf':
        folder = 'pdf'
    else:
        folder = 'images'

    return folder

