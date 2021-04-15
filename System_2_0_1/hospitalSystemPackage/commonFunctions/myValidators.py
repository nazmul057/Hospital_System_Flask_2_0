from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import (DataRequired, Length,
                                Email, NumberRange,
                                InputRequired, ValidationError)  # , EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.widgets.html5 import NumberInput, EmailInput
from hospitalSystemPackage import appValues
from hospitalSystemPackage.models import User, Patient, HospitalStaff, Doctor, Admin


def myFileNameValidator(form, field):
    if len(field.data.filename) > 60:
        raise ValidationError('File name is too large. Please change file name.')

def myUsernameValidator(form, username):
    if Patient.query.filter_by(username=username.data).first() or \
        HospitalStaff.query.filter_by(username=username.data).first() or \
        Doctor.query.filter_by(username=username.data).first() or \
        Admin.query.filter_by(username=username.data).first():
        raise ValidationError('Username taken. Please choose another one.')

def myEmailValidator(form, email):
    if User.query.filter_by(email=email.data).first():
        raise ValidationError('email already used. Please choose another one.')

def myUsernameUpdateValidator(form, username):
    if current_user.userType == appValues['p']:
        typeUser = Patient.query.get(current_user.typeUserId)
    elif current_user.userType == appValues['h']:
        typeUser = HospitalStaff.query.get(current_user.typeUserId)
    elif current_user.userType == appValues['d']:
        typeUser = Doctor.query.get(current_user.typeUserId)
    elif current_user.userType == appValues['a']:
        typeUser = Admin.query.get(current_user.typeUserId)
    else:
        raise ValidationError('Something went wrong in form validators.')

    if username.data != typeUser.username:
        if Patient.query.filter_by(username=username.data).first() or \
            HospitalStaff.query.filter_by(username=username.data).first() or \
            Doctor.query.filter_by(username=username.data).first() or \
            Admin.query.filter_by(username=username.data).first():
            raise ValidationError('That username is taken. Please choose a different one.')

def myEmailUpdateValidator(form, email):
    if email.data != current_user.email:
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('That email is taken. Please choose a different one.')