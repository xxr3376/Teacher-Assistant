#! encoding=utf-8
from flask import Flask
import os
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

if 'SERVER_SOFTWARE' in os.environ:
    # SAE
    from sae.const import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB
    DB_CONNECT_STRING = 'mysql://%s:%s@%s:%s/%s' % (MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONNECT_STRING

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
from app import views
