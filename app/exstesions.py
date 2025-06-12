from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from itsdangerous import URLSafeTimedSerializer

SESSION_TOKEN_KEY_PATTERN = "token_from_password_{}"


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager() 
mail = Mail()
cache = Cache()

serializer = None 

def init_serializer(app: Flask):
    global serializer
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    