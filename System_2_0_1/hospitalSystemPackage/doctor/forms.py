from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, \
    BooleanField, IntegerField, SelectField, TextAreaField
from wtforms.validators import (DataRequired, Length,
                                Email, NumberRange,
                                InputRequired, ValidationError)  # , EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.widgets.html5 import NumberInput, EmailInput
from hospitalSystemPackage.models import User
from hospitalSystemPackage.commonFunctions.myValidators \
    import myFileNameValidator, myUsernameUpdateValidator, myEmailUpdateValidator


class PrescriptionForm(FlaskForm):
    description = StringField('Description',
                           validators=[Length(min=0, max=60)]
                           )
    material = TextAreaField('Prescription', validators = [DataRequired()])

    submit = SubmitField('Post')


class UpdateDoctorInfoForm(FlaskForm):
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

    field = StringField('Field',
                       validators=[DataRequired("You must input something"),
                                   Length(min = 0, max = 20)]
                       )

    submit = SubmitField('Update Information')