from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import (DataRequired, Length,
                                Email, NumberRange,
                                InputRequired, ValidationError)  # , EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.widgets.html5 import NumberInput, EmailInput
from hospitalSystemPackage.models import User
from hospitalSystemPackage.commonFunctions.myValidators \
    import myFileNameValidator, myUsernameUpdateValidator, myEmailUpdateValidator


class UpdatePatientInfoForm(FlaskForm):
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

    age = IntegerField('Age', widget=NumberInput(min=0, max=200, step=1),
                       validators=[InputRequired("You must input something"),
                                   NumberRange(min=0, max=200, message='Invalid length')]
                       )

    

    submit = SubmitField('Update Information')

'''
    def validate_username(self, username):
        if username.data != current_user.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError('That email is taken. Please choose a different one.')

def my_fileName_validator(form, field):
    if len(field.data.filename) > 60:
        raise ValidationError('File name is too large. Please change file name.')

'''

class DoctorConnectionForm(FlaskForm):
    username = StringField('Doctor Username',
                           validators=[DataRequired("You must input something"),
                                       Length(min=2, max=60)]
                           )

    submit = SubmitField('Apply')