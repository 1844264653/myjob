from ..public_course.orm import *


class Users(Model):
    email = StringField('email')
    password = StringField('password')


u = Users(email='zhou11111@greedai.com', password='greedai')
u.insert()
