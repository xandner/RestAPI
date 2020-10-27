from flask import request,abort

from . import users
from .models import User
from .. import db


@users.route('/', methods=['POST'])
def create_user():
    if not request.is_json:
        return {'error':'Only Json'},400
    arg=request.get_json()
    new_user=User()
    try:
        new_user.username=arg.get('username')
        new_user.password=arg.get('password')
        db.session.add(new_user)
        db.session.commit()
    except ValueError as e:
        return {'message':str(e)}
    return {'message':'user was created'}
