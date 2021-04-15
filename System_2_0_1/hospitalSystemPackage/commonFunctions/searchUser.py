import os, datetime
from functools import wraps
import jwt
from PIL import Image
from flask import Blueprint, render_template, flash, redirect,\
    url_for, request, send_from_directory, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from hospitalSystemPackage import db, app, bcrypt, appValues
from hospitalSystemPackage.models import User, Patient, HospitalStaff,\
    Document, ValueInt, Doctor, Admin
from hospitalSystemPackage.commonFunctions.forms import  RegisterPatientForm, \
    RegisterHospitalStaffForm, RegisterDoctorForm
from hospitalSystemPackage.commonFunctions.addAccount import registerPatientFunction, \
    registerHospitalStaffFunction, registerDoctorFunction
from hospitalSystemPackage.admin.forms import RegisterAdminForm, SearchForm, \
    UdpateAdminInfoForm, ChangeValidSpaceForm
from hospitalSystemPackage.commonFunctions.utils import randomSecretString,\
    randomSecretNumbers, getDocumentFromEncryptedId, encodeId, getNumberName,\
    getPatientFromEncryptedId, getHospitalStaffFromEncryptedId,\
    getDoctorFromEncryptedId, getReturnPage, getAdminFromEncryptedId
from hospitalSystemPackage.commonFunctions.deleteAccount import\
    deletePatientAccount, deleteHospitalStaffAccount, deleteDoctorAccount, \
    deleteAdminAccount



def searchForPatient(searchBy = None, searchName = None):
    pass

def searchForHospitalStaff(searchBy = None, searchName = None):
    pass