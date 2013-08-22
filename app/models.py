from app import db
import random
import hashlib

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    password = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime)

    klasses = db.relationship('Class', backref = 'belong_to', lazy = 'dynamic')
    def __init__(self, **kwargs):
        self.token = self.create_token(16)
        if 'password' in kwargs:
            raw = kwargs.pop('password')
            self.password = self.create_password(raw)
        if 'username' in kwargs:
            username = kwargs.pop('username')
            self.username = username.lower()
        if 'email' in kwargs:
            email = kwargs.pop('email')
            self.email = email.lower()
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __repr__(self):
        return '<User %r>' % (self.username)
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return unicode(self.id)
    def check_password(self, raw):
        if not self.password:
            return False
        if '$' not in self.password:
            return False
        salt, hsh = self.password.split('$')
        passwd = '%s%s%s' % (salt, raw, db.app.config['PASSWORD_SECRET'])
        verify = hashlib.sha1(passwd).hexdigest()
        return verify == hsh
    @staticmethod
    def create_password(raw):
        salt = User.create_token(8)
        passwd = '%s%s%s' % (salt, raw, 
                db.app.config['PASSWORD_SECRET'])
        hsh = hashlib.sha1(passwd).hexdigest()
        return "%s$%s" % (salt, hsh)
    @staticmethod
    def create_token(length=16):
        chars = ('0123456789'
                    'abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        salt = ''.join([random.choice(chars) for i in range(length)])
        return salt
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + hashlib.md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40));
    describe= db.Column(db.String(400))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    students = db.relationship('Student', backref = 'belong_to', lazy = 'dynamic')
    homeworks = db.relationship('Homework', backref = 'belong_to', lazy = 'dynamic')
    def __repr__(self):
        return '<Class %r>' % (self.name)
class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40));
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    def __repr__(self):
        return '<Student %r>' % (self.name)
    def barcode(self):
        return str(self.id).zfill(10)
class Homework(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40));
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    records = db.relationship('Record', backref = 'belong_to', lazy = 'dynamic')
    def __repr__(self):
        return '<Homework %r>' % (self.name)
class Record(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'))
    state = db.Column(db.Integer)
    def __repr__(self):
        return '<Record %d>' % (self.id)
    @staticmethod
    def getRecord(homework, student):
        #add a record if record do not presend, then return it
        record = Record.query.filter_by(student_id=student.id).filter_by(homework_id=homework.id).first()
        if not record:
            record = Record(student_id=student.id, homework_id=homework.id, state=0)
            db.session.add(record)
        return record
