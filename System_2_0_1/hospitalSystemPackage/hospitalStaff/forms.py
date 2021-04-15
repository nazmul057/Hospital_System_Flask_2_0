from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import (DataRequired, Length,
                                Email, NumberRange,
                                InputRequired, ValidationError)  # , EqualTo
from wtforms.widgets.html5 import NumberInput, EmailInput
from flask_wtf.file import FileField, FileAllowed, FileRequired
from hospitalSystemPackage.models import User, Patient, Doctor, Document
from hospitalSystemPackage.commonFunctions.myValidators\
    import myUsernameValidator, myEmailValidator, \
    myFileNameValidator, myUsernameUpdateValidator, myEmailUpdateValidator


class UploadPatientDocumentForm(FlaskForm):
    patientUsername = StringField('Patient Username', validators=[Length(min=0, max=60)])
    description = StringField('Description', validators=[Length(min=0, max=60)])
    referenceDoctorUsername = StringField('Reference Doctor Username', validators=[Length(min=0, max=60)])
    file = FileField('Upload File', validators=[myFileNameValidator,
                                                FileRequired(),
                                                FileAllowed(['jpg', 'png', 'jpeg', 'pdf'])]
                     )
    submit = SubmitField('Upload')

    '''
    def validate_patient(self, patient):
        if not Patient.query.filter_by(username=patient.data).first():
            raise ValidationError('Could not find the patient. Please check the Patient username')

    def validate_referenceDoctorName(self, referenceDoctorName):
        if not Doctor.query.filter_by(username=referenceDoctorName.data).first():
            raise ValidationError('Could not find the Doctor. Please check the Doctor username')
    '''

class UpdateHospitalStaffInfoForm(FlaskForm):
    username = StringField('Username',
                           validators=[myUsernameUpdateValidator,
                                       DataRequired("You must input something"),
                                       Length(min=2, max=60)]
                           )

    email = StringField('Email', widget=EmailInput(),
                        validators=[myEmailUpdateValidator,
                                    DataRequired("You must input something"),
                                    Email()]
                        )

    name = StringField('Name',
                            validators=[DataRequired("You must input something"),
                                        Length(min=0, max=120)]
                       )

    submit = SubmitField('Update Information')

class LinkPatientAndDoctorForm(FlaskForm):
    patientUsername = StringField('Patient Username', validators=[Length(min=0, max=60)])
    doctorUsername = StringField('Doctor Username', validators=[Length(min=0, max=60)])

    submit = SubmitField('Apply')