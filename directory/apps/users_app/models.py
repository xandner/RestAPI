from sqlalchemy.orm import validates
from directory.apps import db
from werkzeug.security import generate_password_hash


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=False, nullable=False)

    @validates('password')
    def validate_password(self, key, value):
        if len(value) < 6:
            raise ValueError('password is low')
        return generate_password_hash(value)

    # @validates('username')
    # def validate_username(self, key, value):
    #     if not value.isidentifire():
    #         raise
    #     return value
# db.create_all()