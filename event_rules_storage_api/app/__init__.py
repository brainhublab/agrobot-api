# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)

    # A Flask extension for handling Cross Origin Resource Sharing (CORS),
    # making cross-origin AJAX possible.
    # official documentation: https://flask-cors.readthedocs.io/en/latest/
    CORS(app)

    # flask_migrate here is used for create/upgrade db
    migrate = Migrate(app, db)

    # We need to import every single model as below to can server use them when is started
    from app.models import rules
    from app.models import controllers

    # Flask uses a concept of blueprints for making application components and
    # supporting common patterns within an application or across applications.
    # official documentation: http://flask.pocoo.org/docs/1.0/blueprints/
    from .services.rules import rules as rules_blueprint
    app.register_blueprint(rules_blueprint)

    from .services.controllers import controllers as controllers_blueprint
    app.register_blueprint(controllers_blueprint)

    return app

