from flask import Flask
from .config import Config
from .exstesions import db ,cache , login_manager , mail , init_serializer
from .routes.home import home
from .routes.welcome import welcome
from .routes.auth import auth

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(welcome)
    app.register_blueprint(home)
    app.register_blueprint(auth)
    
    
    db.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    init_serializer(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message ='вы не можете получить доступ'
    with app.app_context():
        from .models import user, passwords

        db.create_all()

    return app
