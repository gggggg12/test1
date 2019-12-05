#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
from flask import request
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.mysql import BIGINT
import base64
from PIL import Image
from io import BytesIO
from passlib.hash import argon2
import os



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:159753a@localhost/sqlalchemy?charset=utf8mb4&autocommit=true'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['SECRET_KEY'] = "fdf"
app.config['UPLOAD_FOLDER'] = "app/static/file"


db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)



from app.views import *


#app.run(debug=True)