from . import api
from flask import current_app as app
from ... import db
from ...models.controllers import Controller
from ..utils import parser, is_there_an_object, auth_check

from flask_restful import Resource
from ..mqtt_client.mqtt_client_publisher import MqttClientPub
import json

# Parse arguments from requests
# official documentation: https://flask-restful.readthedocs.io/en/0.3.5/reqparse.html

parser_post = parser.copy()
parser_post.add_argument("name",
                         required=True,
                         location="json",
                         type=str,
                         help="Name field cannot be blank ")
parser_post.add_argument("mac_addr",
                         required=True,
                         location="json",
                         type=str,
                         help="MAC address field cannot be blank ")
parser_post.add_argument("description",
                         required=True,
                         location="json",
                         type=str,
                         help="Description field cannot be blank ")
parser_post.add_argument("pins_configuration", required=True,
                         location="json",
                         type=dict,
                         help="pins_configuration dict is required!")

parser_put = parser.copy()
parser_put.add_argument("name",
                        required=True,
                        location="json",
                        type=str,
                        help="Name field cannot be blank ")
parser_put.add_argument("description",
                        required=True,
                        location="json",
                        type=str,
                        help="Description field cannot be blank ")
parser_put.add_argument("pins_configuration", required=True,
                        location="json",
                        type=dict,
                        help="pins_configuration dict is required!")

parser_put_subs = parser.copy()
parser_put_subs.add_argument("subscribers",
                             required=True,
                             location="json",
                             type=list,
                             help="subscribers cannot be empty list")


class ControllerAuth(Resource):
    @auth_check
    def put(self, mac_addr):
        args = parser_put_subs.parse_args()
        controller = Controller.query.filter_by(mac_addr=mac_addr).first()
        if not controller:
            return {
                "message": "Controller not found!"
            }, 404

        controller.subscribers = args["subscribers"]
        db.session.commit()
        return controller.toDict(), 200


api.add_resource(ControllerAuth, "/api/controllers/subscribers/<mac_addr>/")


class Controllers(Resource):
    @auth_check
    def get(self):
        all_controllers = Controller.query.order_by("updated_on")
        return [x.toDict() for x in all_controllers], 200

    @auth_check
    def post(self):
        args = parser_post.parse_args()
        exist_controller = Controller.query.filter_by(mac_addr=args["mac_addr"]).first()
        if exist_controller is not None:
            return {
                "message": "Controller already exist!"
            }, 409

        new_controller = Controller(
            name=args["name"],
            mac_addr=args["mac_addr"],
            description=args["description"],
            pins_configuration=args["pins_configuration"],
            subscribers=[]
        )
        db.session.add(new_controller)

        db.session.commit()
        print("++++++++++++++++++++++++++++++==")
        print("New controller was born")
        return new_controller.toDict(), 201


api.add_resource(Controllers, "/api/controllers/")


class CControllers(Resource):
    @auth_check
    def get(self, id):
        controller = Controller.query.filter_by(id=id).first()
        if is_there_an_object(controller):
            return controller.toDict(), 200
        else:
            return {
                "message": "Obj not found!"
            }, 404

    @auth_check
    def put(self, id):
        args = parser_put.parse_args()
        controller_to_update = Controller.query.filter_by(id=id).first()
        if is_there_an_object(controller_to_update):
            controller_to_update.name = args["name"],
            controller_to_update.description = args["description"],
            controller_to_update.pins_configuration = args["pins_configuration"]
            db.session.commit()
            new_data = controller_to_update.toDict()
            try:
                topic = app.config["API_CONFIG_UPDATE"] + "/" + new_data["mac_addr"]
                MqttClientPub().bootstrap_mqtt().pub(topic, json.dumps(new_data))
            except Exception as e:
                print(e)
            return new_data, 200
        else:
            return {
                "message": "Obj not found!"
            }, 404

    @auth_check
    def delete(self, id):
        controller = Controller.query.filter_by(id=id).first()
        if controller:
            """ Send delete instruction to communication service """

            data = controller.toDict()
            data_to_send = {"subscribers": data["subscribers"],
                            "mac_addr": data["mac_addr"]
                            }
            try:
                topic = app.config["API_OBJ_DELETE"] + "/" + data_to_send["mac_addr"]
                MqttClientPub().bootstrap_mqtt().pub(topic, json.dumps(data_to_send))
            except Exception as e:
                print(e)

            """ Remove controller from db """
            db.session.delete(controller)
            db.session.commit()
            return {"message": "ok"}, 200
        else:
            return {"message": "Not Found"}, 404


api.add_resource(CControllers, "/api/controllers/<int:id>/")
