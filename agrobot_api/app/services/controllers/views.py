from . import api
from flask import current_app as app
from ... import db
from ...models.controllers import Controller
from ..utils import parser, is_there_an_object, auth_check
from .ctrl_types import ctrlTypes
from flask_restful import Resource
from ..mqtt_client.mqtt_client_publisher import MqttClientPub
import json

# Parse arguments from requests
# official documentation: https://flask-restful.readthedocs.io/en/latest/reqparse.html

parser_post = parser.copy()
parser_post.add_argument("mcuType",
                         required=True,
                         location="json",
                         type=str,
                         help="Mcu type field cannot be blank")
parser_post.add_argument("title",
                         required=False,
                         location="json",
                         type=str,
                         help="title field cannot be blank")
parser_post.add_argument("macAddr",
                         required=True,
                         location="json",
                         type=str,
                         help="MAC address field cannot be blank")


parser_put = parser.copy()
parser_put.add_argument("title",
                        required=False,
                        location="json",
                        type=str,
                        help="title field cannot be blank")
parser_put.add_argument("description",
                        required=False,
                        location="json",
                        type=str,
                        help="description field cannot be blank")
parser_put.add_argument("isConfigured",
                        required=False,
                        location="json",
                        type=bool,
                        help="isConfigured field cannot be blank")
parser_put.add_argument("graph",
                        required=False,
                        location="json",
                        type=dict,
                        help="graph field cannot be blank")
parser_put.add_argument("esp_config",
                        required=False,
                        location="json",
                        type=dict,
                        help="esp_config field cannot be blank")
parser_put.add_argument("selfCheck",
                        required=False,
                        location="json",
                        type=bool,
                        help="selfCheck field cannot be blank")


class Controllers(Resource):
    @auth_check
    def get(self):
        all_controllers = Controller.query.order_by("updated_on")
        return [x.toDict() for x in all_controllers], 200

    @auth_check
    def post(self):
        args = parser_post.parse_args()
        exist_controller = Controller.query.filter_by(macAddr=args["macAddr"]).first()
        if exist_controller is not None:
            return {
                "message": "Controller already exist!"
            }, 409

        esp_config = ctrlTypes().mcuClasses[args["mcuType"]].gen_ctrl_config(args["macAddr"])
        # esp_config = gen_ctrl_config(args["mcuType"], args["macAddr"])
        new_controller = Controller(
            mcuType=args["mcuType"],
            title=args["title"],
            description=args["mcuType"],
            macAddr=args["macAddr"],
            isConfigured=False,
            graph={},
            esp_config=esp_config,
            selfCheck=False,
        )
        db.session.add(new_controller)
        db.session.commit()
        print("++++++++++++++++++++++++++++++==")
        print("New controller was born")
        ctrl_conf_update_topic = app.config["CTRL_CONF_UPDATE"]
        new_ctrl_info = new_controller.toDict()
        MqttClientPub().bootstrap_mqtt().pub(ctrl_conf_update_topic.format(new_ctrl_info["macAddr"]),
                                             json.dumps(new_ctrl_info["esp_config"]))
        return new_ctrl_info, 201


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
            if args["title"] is not None:
                controller_to_update.title = args["title"]
            if args["description"] is not None:
                controller_to_update.description = args["description"]
            if args["isConfigured"] is not None:
                controller_to_update.isConfigured = args["isConfigured"]
            if args["graph"] is not None:
                controller_to_update.graph = args["graph"]
            if args["esp_config"] is not None:
                controller_to_update.esp_config = args["esp_config"]
            if args["selfCheck"] is not None:
                controller_to_update.selfCheck = args["selfCheck"]
            db.session.commit()
            new_data = controller_to_update.toDict()

            ctrl_conf_update_topic = app.config["CTRL_CONF_UPDATE"]
            MqttClientPub().bootstrap_mqtt().pub(ctrl_conf_update_topic.format(new_data["macAddr"]),
                                                 json.dumps(new_data["esp_config"]))
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
            topic = app.config["API_OBJ_DELETE"] + data["macAddr"]
            MqttClientPub().bootstrap_mqtt().pub(topic, json.dumps({"mac_addr": data["macAddr"]}))

            """ Remove controller from db """
            db.session.delete(controller)
            db.session.commit()
            return {"message": "ok"}, 200
        else:
            return {"message": "Not Found"}, 404


api.add_resource(CControllers, "/api/controllers/<int:id>/")


class MqttMasterGet(Resource):
    @auth_check
    def get(self, mac):
        controller = Controller.query.filter_by(macAddr=mac).first()
        if is_there_an_object(controller):
            ctrl_info = controller.toDict()
            ctrl_conf_update_topic = app.config["CTRL_CONF_UPDATE"]
            MqttClientPub().bootstrap_mqtt().pub(ctrl_conf_update_topic.format(ctrl_info["macAddr"]),
                                                 json.dumps(ctrl_info["esp_config"]))
            return {"message": "ok"}, 200
        else:
            return {
                "message": "Obj not found!"
            }, 404


api.add_resource(MqttMasterGet, "/api/controllers/conf/<string:mac>/")
