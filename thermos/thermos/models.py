from datetime import datetime
from __init__ import db
from sqlalchemy import desc
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

tags = db.Table('trip_tag',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                db.Column('trip_id', db.Integer, db.ForeignKey('trip.id')))


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(300))
    destination = db.Column(db.String(300))

    #need to figure out a way to store DateTime properly
    outbound_date = db.Column(db.String(300))
    outbound_time = db.Column(db.String(300))
    inbound_date = db.Column(db.String(300))
    inbound_time = db.Column(db.String(300))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    _tags = db.relationship('Tag', secondary=tags, lazy='joined', backref=db.backref('trips', lazy='dynamic'))
    privacy = db.Column(db.Boolean, default=False)

    @staticmethod
    def newest(num):
        return Trip.query.filter(Trip.privacy.is_(False)).order_by(desc(Trip.date)).limit(num)

    @property
    def tags(self):
        return ",".join([t.name for t in self._tags])

    @tags.setter
    def tags(self, string):
        if string:
            self._tags = [Tag.get_or_create(name) for name in string.split(',')]

    def __repr__(self):
        return "<Trip '{}': '{}'>".format(self.description, self.url)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    trips = db.relationship('Trip', backref='user', lazy='dynamic')
    password_hash = db.Column(db.String)

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def __repr__(self):
        return '<User %r>' % self.username


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True, index=True)

    @staticmethod
    def get_or_create(name):
        try:
            return Tag.query.filter_by(name=name).one()
        except:
            return Tag(name=name)

    @staticmethod
    def all():
        return Tag.query.all()

    def __repr__(self):
        return self.name
