from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import Required, EqualTo

class LoginForm(Form):
    username = TextField('username', validators = [Required()])
    password = PasswordField('password', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)
class RegisterForm(Form):
    username = TextField('username', validators = [Required()])
    password = PasswordField('password', validators = [
        Required(),
        EqualTo('confirm', message="Password must match")
    ])
    confirm = PasswordField('Repeat Password')
    email = TextField('email', validators = [Required()])
class ClassForm(Form):
    name = TextField('name', validators = [Required()])
    describe = TextField('describe')
class HomeworkForm(Form):
    name = TextField('name', validators = [Required()])
class StudentForm(Form):
    name = TextField('name', validators = [Required()])

