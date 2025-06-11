from flask import Flask
from .config import Config
from .exstesions import db 

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    

    db.init_app(app)
    with app.app_context():
        from .models import user, passwords

        db.create_all()

    return app
