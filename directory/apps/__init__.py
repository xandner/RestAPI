from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Development
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config.from_object(Development)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt_manager = JWTManager(app)
mail = Mail(app=None)
mail.init_app(app)
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
ma = Marshmallow(app)
@app.route('/')
def home():
    return {'message': 'hello'}


from directory.apps.users_app import users

app.register_blueprint(users)
