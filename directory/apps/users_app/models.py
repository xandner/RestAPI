from directory.apps import db
from sqlalchemy.orm import validates

from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    verification_code = db.Column(db.Integer)
    is_active = db.Column(db.Boolean)

    def saveToDb(self):
        db.session.add(self)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def return_password(self):
        return self.password
