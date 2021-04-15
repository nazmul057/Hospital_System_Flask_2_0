from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, ValidationError, \
    EqualTo, InputRequired, NumberRange
from wtforms.widgets.html5 import EmailInput, NumberInput
from flask_wtf.file import FileField, FileAllowed, FileRequired
from hospitalSystemPackage import bcrypt
from hospitalSystemPackage.models import User
from hospitalSystemPackage.commonFunctions.myValidators \
    import myFileNameValidator, myUsernameValidator, myEmailValidator, \
    myUsernameUpdateValidator, myEmailUpdateValidator



class LoginForm(FlaskForm):
    email = StringField('Email', widget=EmailInput(),
                        validators=[DataRequired("You must input something"), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateProfileImageForm(FlaskForm):
    profileImage = FileField('Update Profile Picture', validators=[myFileNameValidator,
                                                                   FileAllowed(['jpg', 'png'])]
                             )
    submit = SubmitField('Update')


class ChangePasswordForm(FlaskForm):
    oldPassword = PasswordField('Old Password', validators=[DataRequired()])
    newPassword = PasswordField('New Password',
                                validators=[DataRequired(),
                                            EqualTo('confirmNewPassword', message='New Passwords did not match.')]
                                )
    confirmNewPassword = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

    def validate_oldPassword(self, oldPassword):
        if not bcrypt.check_password_hash(current_user.password, oldPassword.data):
            raise ValidationError('Old password did not verify')

    '''
    def validate_newPassword(self, newPassword):
        if newPassword.data != self.confirmNewPassword.data:
            raise ValidationError('paswords must match')
    '''


class RegisterPatientForm(FlaskForm):
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

    age = IntegerField('Age', widget=NumberInput(min=0, max=200, step=1),
                       validators=[InputRequired("You must input something"),
                                   NumberRange(min=0, max=200, message='Invalid length')]
                       )

    submit = SubmitField('Add Patient')


'''
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username taken. Please choose another one.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('email taken. Please choose another one.')
'''


class RegisterHospitalStaffForm(FlaskForm):
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

    submit = SubmitField('Add Hospital Staff')


class RegisterDoctorForm(FlaskForm):
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

    field = StringField('Field of work',
                            validators=[DataRequired("You must input something"),
                                        Length(min=0, max=20)]
                       )

    submit = SubmitField('Add Doctor')


class CommonSearchForm(FlaskForm):
    searchBy = SelectField('Search By', choices=[('username', 'Username'),
                                                 ('name', 'Name')],
                           validators=[DataRequired("You must input something")])

    searchName = StringField('Search Name',
                             validators=[DataRequired("You must input something"),
                                         Length(min=0, max=120)]
                             )

    submit = SubmitField('Search')


class UploadFileForm(FlaskForm):
    description = StringField('Description', validators=[Length(min=0, max=60)])
    file = FileField('Upload File', validators=[myFileNameValidator,
                                                FileRequired(),
                                                FileAllowed(['jpg', 'png', 'jpeg', 'pdf'])]
                     )
    submit = SubmitField('Upload')


class PasswordResetEmailForm(FlaskForm):
    email = StringField('Your Account Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('We could not find the account. Please check the email address.')


class PasswordResetForm(FlaskForm):
    passwordChangeCode = StringField('The Code Sent to Your Email', validators=[Length(min=0, max=20)])
    newPassword = PasswordField('Please Type a New Password',
                                validators=[DataRequired(),
                                            EqualTo('confirmNewPassword', message='New Passwords did not match.')]
                                )
    confirmNewPassword = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')