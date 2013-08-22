#! encoding=utf-8
from flask import render_template, flash, redirect, g, url_for, request, abort, json
from datetime import datetime
from app import app, db, login_manager

from forms import LoginForm, RegisterForm, ClassForm, HomeworkForm, StudentForm
from models import User, Class, Student, Homework, Record
from util import auth_user
from sqlalchemy.exc import IntegrityError
from flask.ext.login import login_user, logout_user, current_user, login_required


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
            g.user.last_seen = datetime.utcnow()
            db.session.add(g.user)
            db.session.commit()
@app.after_request
def after_request(response):
     db.session.close()
     return response

@app.route('/')
@app.route('/index')
def index():
    UserData = None
    if g.user is not None and g.user.is_authenticated():
        UserData = g.user
    if UserData:
        klasses = UserData.klasses.all()
    else:
        klasses = []
    return render_template("index.html",
            title = u'首页',
            user = UserData, 
            klasses = klasses)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if g.user is not None and g.user.is_authenticated():
        flash('You are already logged in')
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User(username = username, password = password, email = email)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Register success')
            return redirect(url_for('index'))
        except IntegrityError, data:
            flash(data.message.replace('(IntegrityError)', '').strip())
    return render_template('register.html', form = form)
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = auth_user(username, password)
        if user is not None:
            login_user(user, remember = form.remember_me.data)
            flash('Login request for user: ' + form.username.data);
            return redirect(request.args.get("next") or url_for("index"))
        flash('Wrong username or password')
    return render_template("login.html", 
            title = 'Login In',
            form = form)
@login_manager.user_loader
def load_user(id):
    try:
        return User.query.get(int(id))
    except Exception:
        return None

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/user")
@app.route("/user/<username>")
@login_required
def user(username=None):
    if username is None:
        user = g.user
    else:
        user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user = user)
    
@app.route("/class/new", methods = ['GET', 'POST'])
@login_required
def newClass():
    form = ClassForm()
    if form.validate_on_submit():
        name = form.name.data
        describe = form.describe.data
        post = Class(name = name, describe = describe, user_id = current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post success')
        return redirect(url_for('index'))
    return render_template('newClass.html', form = form)

@app.route("/class/view/<classId>")
@login_required
def viewClass(classId=None):
    if classId is None:
        abort(404)
    klass = Class.query.filter_by(id=classId).first_or_404()
    if klass.user_id != g.user.id:
        abort(401)
    homeworks = klass.homeworks.all()
    students = klass.students.all()
    return render_template('viewClass.html', klass=klass, homeworks=homeworks, students=students)
@app.route("/class/markbook/<classId>")
@login_required
def markbook(classId=None):
    if classId is None:
        abort(404)
    klass = Class.query.filter_by(id=classId).first_or_404()
    if klass.user_id != g.user.id:
        abort(401)
    homeworks = klass.homeworks.all()
    records = dict()
    for homework in homeworks:
        for record in homework.records.all():
            records[(homework.id, record.student_id)] =  1
    students = klass.students.all()
    return render_template('markbook.html', klass=klass, homeworks=homeworks, students=students, records=records)
@app.route("/class/addStudent/<classId>", methods=['GET', 'POST'])
@login_required
def addStudent(classId=None):
    if classId is None:
        abort(404)
    klass = Class.query.filter_by(id=classId).first_or_404()
    if klass.user_id != g.user.id:
        #Access Denied
        abort(401)
    form = StudentForm()
    if form.validate_on_submit():
        name = form.name.data
        student = Student(name = name, class_id = classId)
        db.session.add(student)
        db.session.commit()
        flash('add Student success')
        return redirect(url_for('viewClass', classId=classId))
    return render_template('addStudent.html', form = form, klass=klass)
@app.route("/homework/add/<classId>", methods=['GET', 'POST'])
@login_required
def addHomework(classId=None):
    if classId is None:
        abort(404)
    klass = Class.query.filter_by(id=classId).first_or_404()
    if klass.user_id != g.user.id:
        #Access Denied
        abort(401)
    form = HomeworkForm()
    if form.validate_on_submit():
        name = form.name.data
        homework = Homework(name = name, class_id = classId)
        db.session.add(homework)
        db.session.commit()
        flash('addHomework success')
        return redirect(url_for('viewClass', classId=classId))
    return render_template('addHomework.html', form = form, klass=klass)
@app.route("/homework/view/<homeworkId>")
@login_required
def viewHomework(homeworkId=None):
    if homeworkId is None:
        abort(404)
    homework = Homework.query.filter_by(id=homeworkId).first_or_404()
    if homework.belong_to.user_id != g.user.id:
        # no access permission
        abort(401)
    students = homework.belong_to.students.all()
    records = dict((record.student_id, record.state) for record in homework.records.all())
    return render_template('viewHomework.html', homework=homework, students=students, records=records)
@app.route("/homework/finish/<homeworkId>/<studentId>/<targetState>")
@login_required
def finishHomework(homeworkId=None, studentId=None, targetState=None):
    if homeworkId is None or studentId is None or targetState is None:
        abort(404)
    homework = Homework.query.filter_by(id=homeworkId).first_or_404()
    if homework.belong_to.user_id != g.user.id:
        # no access permission
        abort(401)
    student = homework.belong_to.students.filter_by(id=studentId).first_or_404()
    record = Record.getRecord(homework, student)
    record.state = targetState
    db.session.commit()
    return json.jsonify(homeworkId=homeworkId, studentId=studentId, state=targetState);
