from flask import Flask, jsonify
from flask import render_template, request

from app.models import User, Profile, Attach, Subscriber, Auth
from app import app
from app import db
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
from sqlalchemy.dialects.mysql import BIGINT
from passlib.hash import argon2
import base64
import flask_login

import sqlalchemy
from sqlalchemy import (Table, Column, String, Integer,
                        MetaData, select, func)
from functools import wraps
from datetime import datetime, timedelta
import jwt
import os
from app.utils_disk import Storage

storage = Storage()
login_manager = LoginManager()
login_manager.init_app(app)





#проверка токена
def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):

        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registeration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }

        if len(auth_headers) < 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, app.config['SECRET_KEY'])

            user_auth = Auth.query.filter_by(user_id=data['sub']).first()

            if not user_auth:
                raise RuntimeError('User not found')

            return f(user_auth, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401 # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError, Exception) as e:

            return jsonify(invalid_msg), 401

    return _verify













# создать юзера
@app.route('/api/create_user/<string:user1>:<string:password1>', methods=['POST'])
def create_user(user1,password1):

    db.session.execute("insert into user (user_name,password,date) values ('{u}', '{p}', '{d}')".format(u=user1, p=argon2.hash(password1), d=datetime.utcnow()))

    return jsonify({'info': "user created successfully"})



# ЛОГИН
@app.route('/api/login/<string:user_name1>:<string:password1>', methods=['GET'])
def login_api(user_name1,password1):

    usr = User.query.filter_by(user_name=user_name1).first()
    if usr:
        user_pas = usr.password
        if argon2.verify(password1, user_pas):
            token = jwt.encode({
            'sub': usr.id,
            'iat':datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=300)},
            app.config['SECRET_KEY'])
        else:
            return jsonify({ 'message': 'Invalid credentials', 'authenticated': False }), 401
    else:
        return jsonify({ 'message': 'Invalid credentials', 'authenticated': False }), 401

    db.session.execute("insert into auth (user_id,token, date) values ('{n}', '{t}','{d}')".format(n=usr.id, t=token.decode('UTF-8'), d=datetime.utcnow()))

    return jsonify({ 'token': token.decode('UTF-8') })







# Создать профиль type_profile, 1 - открытй, 2 -закрытый профиль
# инф. предеатся через form
@app.route('/api/create_profile',  methods=['POST'])
@token_required
def create_prolile(user_id1):

    file = request.files['file']
    f_name = request.form.get("f_name")
    s_name = request.form.get("s_name")
    year = int(request.form.get("year"))
    type_profile = int(request.form.get("type_profile"))

    db.session.execute("insert into profile (user_id,f_name,s_name,year,type_profile,date) values ({u}, '{f}', '{s}', {y}, {t}, '{d}')".format(u=user_id1.user_id, f=f_name, s=s_name, y=year, t=type_profile, d=datetime.utcnow()))

    # сохранения изображения
    _, ext = file.filename.split(".")
    file.filename = "profile_" + str(user_id1.user_id)+"."+ext
    link = storage.disk("local").put(file)

    db.session.execute("insert into attach (entity_id,entity_type,link,type_attach) values ((select max(id) from profile), '{et}', '{l}', '{t}', '{d}')".format(ui=user_id1.user_id, et="profile", l=link, t="img", d=datetime.utcnow()))

    return jsonify({'info': "profile " + " created successfully"})









# подписаться на пользователя
@app.route('/api/sub/<int:id1>',  methods=['POST'])
@token_required
def subscribe(user_id1,id1):

    usr = User.query.filter_by(id=id1).first()
    
    if usr:
        db.session.execute("insert into subscriber (user_id_from,user_id_to,approve, date) values ({uf}, {ut}, (select type_profile from profile where user_id='{ui}'), '{d}')".format(ui=id1, uf=user_id1.user_id, ut=id1, d=datetime.utcnow()))
    else:
        return jsonify({'info': "User is not found"})

    return jsonify({'info': "success"})


# список запросов на закрытый профиль
@app.route('/api/list_sub',  methods=['GET'])
@token_required
def list_sub(user_id1):

    resultproxy = db.session.execute("SELECT user_name FROM user WHERE id in (SELECT user_id_from FROM subscriber WHERE user_id_to = {t} AND approve = 0)".format(t=user_id1.user_id))
    d = []
    for rowproxy in resultproxy:
        for column, value in rowproxy.items():
        	d.append(value)

    return jsonify({'info': d})


# апрув запроса подписчика
@app.route('/api/sub_approve/<int:id1>',  methods=['POST'])
@token_required
def subscribe_approve(user_id1,id1):

    db.session.execute("UPDATE subscriber SET approve = 1 WHERE user_id_from = {f} AND user_id_to = {t}".format(f=id1, t=user_id1.user_id))

    return jsonify({'info': "success"})


# отказ запроса подписчика
@app.route('/api/sub_approve/<int:id1>',  methods=['DELETE'])
@token_required
def subscribe_approve_d(user_id1,id1):

    db.session.execute("DELETE from subscriber WHERE user_id_from = {uf} AND user_id_to = {ut}".format(uf=id1, ut=user_id1.user_id))

    return jsonify({'info': "success"})









# создать пост, инф. предеатся через form
@app.route('/api/create_post',  methods=['POST'])
@token_required
def create_post(user_id1):

    file = request.files['file']
    post_text = request.form.get("post")

    db.session.execute("insert into post (user_id,text,date) values ({u}, '{t}', '{d}')".format(u=user_id1.user_id, t=post_text, d=datetime.utcnow()))

    _, ext = file.filename.split(".")
    file.filename = "post_" + str(storage.random_path())+"."+ext
    link = storage.disk("local").put(file)

    # расширения
    db.session.execute("insert into attach (entity_id,entity_type,link,type_attach,date) values ((select max(id) from post), '{et}', '{l}', '{t}','{d}')".format(ui=user_id1.user_id, et="post", l=link, t="img", d=datetime.utcnow()))

    return jsonify({'info': "post " + " created successfully"})


# просмотр всем постов подписчиков в хрон. порядке
@app.route('/api/view_posts',  methods=['GET'])
@token_required
def view_posts(user_id1):

    sql = "SELECT post.id, post.user_id, post.text, attach.link, attach.type_attach FROM attach RIGHT OUTER JOIN post ON attach.entity_id = post.id AND attach.entity_type = 'post' WHERE post.user_id in (SELECT user_id_to FROM subscriber WHERE user_id_from = {u} and approve = 1) ORDER BY post.date DESC".format(u=user_id1.user_id)

    resultproxy = db.session.execute(sql)

    return_json = []

    for rowproxy in resultproxy:
        a = {}
        for column, value in rowproxy.items():
            a.update({column : value})
        return_json.append(a)

    return jsonify({'info_post': return_json})









# лайкнуть пост
@app.route('/api/like_post/<int:id1>',  methods=['POST'])
@token_required
def like_posts(user_id1, id1):

    sql = "INSERT INTO likes (user_id,entity_id,entity_type,date) VALUES ({u}, {i}, 'post','{d}')".format(u=user_id1.user_id, i=id1, d=datetime.utcnow())
    db.session.execute(sql)


    return jsonify({'info': "like post success"})


# убрать лайк
@app.route('/api/like_post/<int:id1>',  methods=['DELETE'])
@token_required
def like_posts_del(user_id1, id1):

    sql = "DELETE from likes WHERE user_id = {u} AND entity_id = {ei} AND entity_type = 'post'".format(u=user_id1.user_id, ei=id1)
    db.session.execute(sql)


    return jsonify({'info': "delete like post success"})


# просмотр всех лайкнувших пользователей
@app.route('/api/view_like/<int:id1>',  methods=['GET'])
@token_required
def view_like(user_id1, id1):

    sql = "SELECT profile.f_name, attach.link, attach.type_attach FROM likes JOIN profile ON profile.user_id = likes.user_id JOIN attach ON attach.entity_id = profile.id AND attach.entity_type = 'profile' WHERE likes.entity_id = {i} and likes.entity_type = 'post'".format(i=id1)
    resultproxy = db.session.execute(sql)

    return_json = []

    for rowproxy in resultproxy:
        a = {}
        for column, value in rowproxy.items():
            a.update({column : value})
        return_json.append(a)

    return jsonify({'info_like': return_json})



