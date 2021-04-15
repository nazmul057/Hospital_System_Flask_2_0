import os
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecretkey' # secrets.token_hex(20) --> can create random string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=2)
app.config['REMEMBER_COOKIE_DURATION'] =  timedelta(days=5)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'Your_Email_Address' # Recommended to use environmental variable here
app.config['MAIL_PASSWORD'] = 'Your_Email_Password' # Recommended to use environmental variable here
mail = Mail(app)

appValues = {'p' : 'patient',
             'h' : 'hospitalStaff',
             'd' : 'doctor',
             'a' : 'admin',
             'hospital' : 'hospital',
             'cryptoKey' : b'2KC8TXKr75KD5oacVcciX9zHxUeedJhcHUgZvMRFn84='
             }

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'commonFunctions.login'
login_manager.login_message_category = 'info'

from hospitalSystemPackage.commonFunctions.routes import commonFunctions 
from hospitalSystemPackage.patient.routes import patient 
from hospitalSystemPackage.hospitalStaff.routes import hospitalStaff 
from hospitalSystemPackage.doctor.routes import doctor
from hospitalSystemPackage.admin.routes import admin

app.register_blueprint(commonFunctions)
app.register_blueprint(patient, url_prefix="/patient")
app.register_blueprint(hospitalStaff, url_prefix="/hospitalStaff")
app.register_blueprint(doctor, url_prefix="/doctor")
app.register_blueprint(admin, url_prefix="/admin")
