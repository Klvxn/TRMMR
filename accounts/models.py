from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from database import db


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email_address = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)

    links = db.relationship("Link", backref="user_links", lazy=True)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_user_by_email(cls, email):
        user = cls.query.filter_by(email_address=email).first()
        return user
