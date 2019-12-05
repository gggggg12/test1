from app import db
import enum
from sqlalchemy.dialects.mysql import BIGINT
import datetime
from flask_login import LoginManager, UserMixin
#from sqlalchemy.dialects.mysql import BIGINT




class User(db.Model, UserMixin):
    __tablename__ = 'user'
 
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    user_name = db.Column(db.String(length=20))
    password = db.Column(db.String(length=100))
    date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    ch_profile = db.relationship("Profile")
    ch_auth = db.relationship("Auth")
    #ch_subscriber = db.relationship("Subscriber")
    ch_post = db.relationship("Post")
    ch_like = db.relationship("Likes")
    #def __repr__(self):
    #    return "<User(name='{0}', fullname='{1}', nickname='{2}')>".format(
    #                        self.name, self.fullname, self.nickname)


class Profile(db.Model):
    __tablename__ = 'profile'

    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    user_id = db.Column(BIGINT(unsigned=True), db.ForeignKey('user.id'))
    f_name = db.Column(db.String(length=20))
    s_name = db.Column(db.String(length=20))
    year = db.Column(db.SmallInteger)
    type_profile = db.Column(db.Boolean())
    date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


class Auth(db.Model):
    __tablename__ = 'auth'

    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    user_id = db.Column(BIGINT(unsigned=True), db.ForeignKey('user.id'))
    token = db.Column(db.String(length=150))
    date = db.Column(db.DateTime())


class Subscriber(db.Model):
    __tablename__ = 'subscriber'

    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    user_id_from = db.Column(BIGINT(unsigned=True), db.ForeignKey('user.id'))
    user_id_to = db.Column(BIGINT(unsigned=True), db.ForeignKey('user.id'))
    approve = db.Column(db.Boolean())
    date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
   


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    user_id = db.Column(BIGINT(unsigned=True), db.ForeignKey('user.id'))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)




class all_attach(enum.Enum):
    img = 1
    video = 2
    audio = 3
    link = 4


class Attach(db.Model):
    __tablename__ = 'attach'

    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    entity_id = db.Column(BIGINT(unsigned=True))
    entity_type = db.Column(db.String(length=50))
    link = db.Column(db.String(length=100))
    type_attach = db.Column(db.Enum(all_attach))
    date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)



class Likes(db.Model):
    __tablename__ = 'likes'

    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    user_id = db.Column(BIGINT(unsigned=True), db.ForeignKey('user.id'))
    entity_id = db.Column(BIGINT(unsigned=True))
    entity_type = db.Column(db.String(length=50))
    date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)



db.create_all()
