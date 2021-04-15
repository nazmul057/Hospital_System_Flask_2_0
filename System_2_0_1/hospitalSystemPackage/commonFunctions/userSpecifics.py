import string, secrets, jwt, os, sys
from flask import flash
from werkzeug.utils import secure_filename
from hospitalSystemPackage import db, app
from hospitalSystemPackage.models import ValueInt,\
    ValueString, Document, Patient, Doctor,\
    HospitalStaff, User
from hospitalSystemPackage.commonFunctions.utils import getNumberName, \
    encodeId, getFileFolder

def deleteDocument(user=None, inputDocument=None):

    if type(inputDocument) == Document:
        # print('from userSpecifics one document')
        # print(type(inputDocument))
        if inputDocument and inputDocument.documentOwner == user:
            folder = getFileFolder(inputDocument.document)

            '''
            user.totalUsedSpace -= os.stat(
                os.path.join(app.root_path, 'userFiles/' + folder, inputDocument.document)).st_size
            print(os.stat(os.path.join(app.root_path, 'userFiles/' + folder, inputDocument.document)).st_size)
            '''

            os.remove(os.path.join(app.root_path, 'userFiles/' + folder, inputDocument.document))

            user.totalUsedSpace -= inputDocument.documentSize

            db.session.delete(inputDocument)
            db.session.commit()

            return True

        else:
            return False

    else:
        # print('from userSpecifics multiple document')
        # print(type(inputDocument))
        for eachDocument in inputDocument:
            if eachDocument and eachDocument.documentOwner == user:
                folder = getFileFolder(eachDocument.document)

                # patient.totalUsedSpace -= os.stat(
                # os.path.join(app.root_path, 'userFiles/' + folder, fileToBeDeleted.document)).st_size

                os.remove(os.path.join(app.root_path, 'userFiles/' + folder, eachDocument.document))

                db.session.delete(eachDocument)

        db.session.commit()

        return True


def deleteOneDocument(user=None, inputDocument=None):
    # print('from NEW one document userSpecifics')
    # print(type(inputDocument))
    try:
        folder = getFileFolder(inputDocument.document)

        '''
        user.totalUsedSpace -= os.stat(
            os.path.join(app.root_path, 'userFiles/' + folder, inputDocument.document)).st_size
        print(os.stat(os.path.join(app.root_path, 'userFiles/' + folder, inputDocument.document)).st_size)
        '''

        os.remove(os.path.join(app.root_path, 'userFiles/' + folder, inputDocument.document))

        user.totalUsedSpace -= inputDocument.documentSize

        db.session.delete(inputDocument)
        db.session.commit()

        return True

    except:

        return False


def deleteMultipleDocuments(user=None, inputDocuments=None):
    try:
        # print('from NEW multiple document userSpecifics')
        # print(type(inputDocuments))
        for eachDocument in inputDocuments:
            if eachDocument and eachDocument.documentOwner == user:
                folder = getFileFolder(eachDocument.document)

                # patient.totalUsedSpace -= os.stat(
                # os.path.join(app.root_path, 'userFiles/' + folder, fileToBeDeleted.document)).st_size

                os.remove(os.path.join(app.root_path, 'userFiles/' + folder, eachDocument.document))

                db.session.delete(eachDocument)

        db.session.commit()

        return True

    except:

        return False


def uploadDocument(description = None,
                   receivedFile = None,
                   owner = None,
                   postedBy = None,
                   referenceDoctor = None,
                   referenceDoctorName = None):
    if not receivedFile:
        flash('No File Part', 'danger')
        return False

    if receivedFile.filename == '':
        flash('No selected file', 'danger')
        return False

    fileName = secure_filename(receivedFile.filename)
    _, fExt = os.path.splitext(fileName)

    
    newFileName = getNumberName('documentName') + fExt

    # this folder name can be stored in database in document table to
    # reference the folder where the file is saved. Currently the system gets
    # the stored folder reference from the file extension.
    folder = getFileFolder(newFileName)

    receivedFile.save(os.path.join(app.root_path, 'userFiles/' + folder, newFileName))

    receivedFile.seek(0, 2)
    fileSize = receivedFile.tell()

    # patient = Patient.query.filter_by(idFromUserModel=current_user.id).first_or_404()
    validSpaceSize = ValueInt.query.filter_by(variableName='spaceSize').first()
    actualSize = validSpaceSize.variableValue

    if fileSize + owner.totalUsedSpace > actualSize:
        os.remove(os.path.join(app.root_path, 'userFiles/' + folder, newFileName))
        flash("Space is full, cannot upload", 'danger')
        return False

    # To get the last Item: https://stackoverflow.com/questions/8551952/how-to-get-last-record
    # lastItem = db.session.query(Document).order_by(Document.id.desc()).first() # This worked

    newFile = Document(description = description,
                       postedBy = postedBy,
                       document = newFileName,
                       actualDocumentName = fileName,
                       documentSize = fileSize,
                       documentOwner = owner,
                       referenceDoctor = referenceDoctor,
                       referenceDoctorName = referenceDoctorName)

    owner.totalUsedSpace += fileSize

    db.session.add(newFile)
    db.session.commit()

    # print("the id is")
    # print(newFile.id)
    newFile.documentIdEncrypted = encodeId(newFile.id)
    db.session.commit()
    flash('File Uploaded.', 'success')
    return True