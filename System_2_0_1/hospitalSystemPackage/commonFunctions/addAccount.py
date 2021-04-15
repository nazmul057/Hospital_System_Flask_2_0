from flask import Blueprint, render_template, flash, redirect, url_for
from hospitalSystemPackage import db, bcrypt, appValues
from hospitalSystemPackage.models import User, Patient, HospitalStaff, Doctor, Admin
from hospitalSystemPackage.commonFunctions.utils import randomSecretString,\
    randomSecretNumbers, getDocumentFromEncryptedId, encodeId, sendResetEmail, \
    randomSecretCode


def registerPatientFunction(form):
    try:
        user = User(email=form.email.data,
                    userType=appValues['p'],
                    password=bcrypt.generate_password_hash('password').decode('utf-8'),
                    # password = 'password',
                    passwordChangeCode = randomSecretCode(),
                    userToken=randomSecretString(20))

        db.session.add(user)
        db.session.commit()

        patient = Patient(username=form.username.data,
                          idFromUserModel=user.id,
                          name=form.name.data,
                          age=form.age.data,
                          totalUsedSpace=0)
        db.session.add(patient)
        db.session.commit()

        user.typeUserId = patient.id
        patient.patientIdEncrypted = encodeId(patient.id)
        db.session.commit()

        # sendResetEmail(user, False)

        flash(f'Account created for {form.username.data}!!!!', 'success')  # the second argument is called category

        return True

    except:
        flash('Something Went Wrong', 'danger')
        return False


def registerHospitalStaffFunction(form):
    try:
        user = User(email=form.email.data,
                    userType='hospitalStaff',
                    password=bcrypt.generate_password_hash('password').decode('utf-8'),
                    # password = 'password',
                    passwordChangeCode=randomSecretCode(),
                    userToken=randomSecretString(20))

        db.session.add(user)
        db.session.commit()

        hospitalStaff = HospitalStaff(username=form.username.data,
                                      idFromUserModel=user.id,
                                      name=form.name.data)
        db.session.add(hospitalStaff)
        db.session.commit()

        user.typeUserId = hospitalStaff.id
        hospitalStaff.hospitalStaffIdEncrypted = encodeId(hospitalStaff.id)
        db.session.commit()

        flash(f'Account created for {form.username.data}!!!!', 'success')  # the second argument is called category

        return True

    except:
        flash('Something Went Wrong', 'danger')
        return False


def registerDoctorFunction(form):
    try:
        user = User(email=form.email.data,
                    userType='doctor',
                    password=bcrypt.generate_password_hash('password').decode('utf-8'),
                    # password = 'password',
                    passwordChangeCode=randomSecretCode(),
                    userToken=randomSecretString(20))

        db.session.add(user)
        db.session.commit()

        doctor = Doctor(username=form.username.data,
                        idFromUserModel=user.id,
                        name=form.name.data,
                        field=form.field.data)
        db.session.add(doctor)
        db.session.commit()

        user.typeUserId = doctor.id
        doctor.doctorIdEncrypted = encodeId(doctor.id)
        db.session.commit()

        flash(f'Account created for {form.username.data}!!!!', 'success')  # the second argument is called category

        return True

    except:
        flash('Something Went Wrong', 'danger')
        return False


def registerAdminFunction(form):
    try:
        user = User(email=form.email.data,
                    userType=appValues['a'],
                    password=bcrypt.generate_password_hash('password').decode('utf-8'),
                    # password = 'password',
                    passwordChangeCode=randomSecretCode(),
                    userToken=randomSecretString(20))

        db.session.add(user)
        db.session.commit()

        admin = Admin(username=form.username.data,
                      idFromUserModel=user.id,
                      name=form.name.data,
                      title=form.title.data)

        db.session.add(admin)
        db.session.commit()

        user.typeUserId = admin.id
        admin.adminIdEncrypted = encodeId(admin.id)
        db.session.commit()

        flash(f'Account created for {form.username.data}!!!!', 'success')  # the second argument is called category

        return True

    except:
        flash('Something Went Wrong', 'danger')
        return False