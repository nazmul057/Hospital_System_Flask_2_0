from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import (DataRequired, Length,
                                Email, NumberRange,
                                InputRequired, ValidationError)  # , EqualTo
from wtforms.widgets.html5 import NumberInput, EmailInput
from hospitalSystemPackage.models import User
from hospitalSystemPackage.commonFunctions.myValidators\
    import myUsernameValidator, myEmailValidator, myUsernameUpdateValidator, myEmailUpdateValidator


class ChangeValidSpaceForm(FlaskForm):
    space = IntegerField('Space', widget=NumberInput(min=0, max=100000000000, step=100000000),
                       validators=[InputRequired("You must input something"),
                                   NumberRange(min=0, max=100000000000, message='Invalid length')]
                       )

    submit = SubmitField('Change Valid Space')

class UdpateAdminInfoForm(FlaskForm):
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

    title = StringField('Title',
                        validators=[DataRequired("You must input something"),
                                    Length(min=0, max=20)]
                        )

    submit = SubmitField('Update Information')


class RegisterAdminForm(FlaskForm):
    username = StringField('Username',
                           validators=[myUsernameValidator,
                                       DataRequired("You must input something"),
                                       Length(min=2, max=60)]
                           )

    email = StringField('Email', widget=EmailInput(),
                        validators=[myEmailValidator,
                                    DataRequired("You must input something"),
                                    Email()]
                        )

    name = StringField('Name',
                            validators=[DataRequired("You must input something"),
                                        Length(min=0, max=120)]
                       )

    title = StringField('Title',
                       validators=[DataRequired("You must input something"),
                                   Length(min=0, max=20)]
                       )

    submit = SubmitField('Add Admin')


class SearchForm(FlaskForm):
    searchBy = SelectField('Search By', choices=[('username', 'Username'),
                                                 ('email', 'Email'),
                                                 ('name', 'Name')],
                        validators=[DataRequired("You must input something")])

    searchName = StringField('Search Name',
                        validators=[DataRequired("You must input something"),
                                    Length(min=0, max=120)]
                        )

    submit = SubmitField('Search')

'''
class SearchDoctorForm(FlaskForm):
    searchBy = SelectField('Search By', choices=[('username', 'Username'),
                                                 ('email', 'Email'),
                                                 ('name', 'Name')],
                        validators=[DataRequired("You must input something")])

    searchName = StringField('Search Name',
                        validators=[DataRequired("You must input something"),
                                    Length(min=0, max=120)]
                        )

    submit = SubmitField('Search')


class SearchHospitalStaffForm(FlaskForm):
    searchBy = SelectField('Search By', choices=[('username', 'Username'),
                                                 ('email', 'Email'),
                                                 ('name', 'Name')],
                        validators=[DataRequired("You must input something")])

    searchName = StringField('Search Name',
                        validators=[DataRequired("You must input something"),
                                    Length(min=0, max=120)]
                        )

    submit = SubmitField('Search')

'''