from hospitalSystemPackage import db, bcrypt
from hospitalSystemPackage.models import ValueInt, ValueString, Admin, User
from hospitalSystemPackage.commonFunctions.utils import randomSecretString, encodeId, \
    randomSecretCode

v1 = ValueInt(variableName='spaceSize', variableValue=100000000)

v2 = ValueString(variableName='documentName', variableValue='0')
v3 = ValueString(variableName='profileImageFileName', variableValue='0')

db.session.add(v1)
db.session.add(v2)
db.session.add(v3)

user = User(email='admin1@mail.com',
            userType='admin',
            password=bcrypt.generate_password_hash('password').decode('utf-8'),
            # password = 'password',
            passwordChangeCode = randomSecretCode(),
            userToken= randomSecretString(20))

db.session.add(user)
db.session.commit()

admin = Admin(username = 'admin1',
              idFromUserModel=user.id,
              name='Admin',
              title='Title')

db.session.add(admin)
db.session.commit()

user.typeUserId = admin.id
admin.adminIdEncrypted = encodeId(admin.id)
db.session.commit()