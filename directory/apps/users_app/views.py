from flask_marshmallow import Marshmallow

from .. import db, mail, app,jwt_manager
from flask import request, abort, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, \
    jwt_refresh_token_required, unset_access_cookies, unset_jwt_cookies, unset_refresh_cookies, current_user
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from . import users
from .models import User

import random


@users.route('/', methods=['POST'])
def create_user():
    if not request.is_json:
        return {'error': 'Only Json'}, 400
    arg = request.get_json()
    new_user = User()
    v_code = random.randint(1000, 9999)
    try:
        new_user.verification_code=v_code
        new_user.password=arg.get('password')
        new_user.username=arg.get('username')
        new_user.email=arg.get('email')
        new_user.is_active=0
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return {'m':str(e)}
    # msg = Message("hi, this is your code:" + str(v_code),
    #               sender="admin.xander-api.com",
    #               recipients=[arg.get('email')])
    # mail.send(msg)


    return {'message': 'user was created, pleas confrim your email address'}, 201


@users.route('/auth', methods=['POST'])
def login():
    if not request.is_json:
        return {'error': 'Only Json'}, 400
    arg = request.get_json()
    username = arg.get('username')
    password = arg.get('password')

    users = User.query.filter(User.username.ilike(username)).first()
    if not users:
        return {'error': 'user not exists'}, 403

    if not users.check_password(password):
        return {'error': 'wrong password'}, 403

    access_token = create_access_token(identity=users.username, fresh=True)
    refresh_token = create_refresh_token(identity=users.username)
    return {'access token:': access_token,
            'refresh token': refresh_token}, 200


@users.route('/', methods=['GET'])
@jwt_required
def get_user():
    identity = get_jwt_identity()
    user = User.query.filter(User.username.ilike(identity)).first()
    return {'user': user.username}


@users.route('/auth', methods=['PUT'])
@jwt_refresh_token_required
def get_new_access_token():
    identity = get_jwt_identity()
    return {'new access token:': create_access_token(identity=identity)}


@users.route('/auth/email/<string:user_email>/<int:v_code>', methods=['POST'])
def confrim_email(user_email, v_code):
    user = User.query.filter_by(email=user_email)
    if not user:
        return {'message': 'wrong email'}
    if user.verification_code != v_code:
        return {'message': 'wrong code'}
    user.is_active = 1
    db.session.commit()


@users.route('/auth/delete/<int:user_id>', methods=["DELETE"])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify(message='deleted'), 202
    else:
        return jsonify(message='dos not exists'), 404


ma = Marshmallow(app)


class UserScheme(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


user_schema = UserScheme(many=True)


@users.route('/all', methods=['GET'])
def all_users():
    user_list = User.query.all()
    result = user_schema.dump(user_list)
    return jsonify(result)


@users.route('/auth/password', methods=['PUT'])
def set_password():
    if not request.is_json:
        return {'error': 'Only Json'}, 400
    arg = request.get_json()
    username = arg.get('username')
    password = arg.get('password')
    new_password=arg.get('new_password')
    users = User.query.filter(User.username.ilike(username)).first()
    if not users:
        return {'error': 'user not exists'}, 403

    if not users.check_password(password):
        return {'error': 'wrong password'}, 403

    users.password=new_password
    db.session.commit()
    return {'message':'password changed'}

blacklist = set()
@users.route('/logout')
@jwt_manager.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist