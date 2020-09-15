from flask import Blueprint
# Flask-RESTful is an extension for Flask that adds support for
# quickly building REST APIs.
from flask_restful import Api

# Registrate new  Blueprint
data = Blueprint("data", __name__)
api = Api(data)

from . import views
