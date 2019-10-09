from . import api
# If we do something with db data we need to import SQLalchemy object (db for example)
# and also to import all models that we will use in our view (for example model "example1")
from ... import db
from ...models.controllers import Controller
from ..utils import parser, is_there_an_object

from flask_restful import Resource

# Parse arguments from requests
# official documentation: https://flask-restful.readthedocs.io/en/0.3.5/reqparse.html

parser_post_put = parser.copy()
parser_post_put.add_argument("name",
                             required=True,
                             location="json",
                             type=str,
                             help="Name field cannot be blank ")
parser_post_put.add_argument("description",
                             required=True,
                             location="json",
                             type=str,
                             help="Description field cannot be blank ")
parser_post_put.add_argument("pins_configuration", required=True,
                             location="json",
                             type=dict,
                             help="pins_configuration dict is required!")


class Controllers(Resource):
    # Documentation for Minimal Flaks-RESTful API you can find here:
    # https://flask-restful.readthedocs.io/en/latest/quickstart.html#resourceful-routing

    # SQLAlchemy documentation queryng:
    # https://docs.sqlalchemy.org/en/latest/orm/query.html

    # Put request
    def get(self):
        all_controllers = Controller.query.order_by("updated_on")
        return [x.toDict() for x in all_controllers], 200

    # Delete request
    def post(self):
        args = parser_post_put.parse_args()

        new_controller = Controller(
            name=args["name"],
            description=args["description"],
            pins_configuration=args["pins_configuration"]
        )
        db.session.add(new_controller)

        db.session.commit()
        print("++++++++++++++++++++++++++++++==")
        print("New controller was born")
        return new_controller.toDict(), 201


api.add_resource(Controllers, "/api/controllers/")


class CControllers(Resource):
    # Documentation for Minimal Flaks-RESTful API you can find here:
    # https://flask-restful.readthedocs.io/en/latest/quickstart.html#resourceful-routing

    # SQLAlchemy documentation queryng:
    # https://docs.sqlalchemy.org/en/latest/orm/query.html

    def get(self, id):
        controller = Controller.query.filter_by(id=id).first()
        if is_there_an_object(controller):
            return controller.toDict(), 200
        else:
            return {
                "message": "Obj not found!"
            }, 404

    def put(self, id):
        args = parser_post_put.parse_args()
        controller_to_update = Controller.query.filter_by(id=id).first()
        if is_there_an_object(controller_to_update):

            controller_to_update.name = args["name"],
            controller_to_update.description = args["description"],
            controller_to_update.pins_configuration = args["pins_configuration"]

            db.session.commit()
            return controller_to_update.toDict(), 201
        else:
            return {
                "message": "Obj not found!"
            }, 404


api.add_resource(CControllers, "/api/controllers/<int:id>/")

