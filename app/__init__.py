import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from 
from flask_bcrypt import Bcrypt
from config import config


db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bcrypt = Bcrypt(app)
    login_manager.init_app(app)

    api = Api(app)
    db.init_app(app)
    from .router import initialize_routes
    initialize_routes(api)
    migrate = Migrate(app, db)

    return app
