from . import api
# If we do something with db data we need to import SQLalchemy oblect (db for example)
# and also to import all models that we will use in our view (for example model "example1")
from ... import db
from ...models.rules import Rule
from ...models.controllers import Controller
from ..utils import parser, is_there_an_object

from flask_restful import Resource


# Parse arguments from requests
# official documentation: https://flask-restful.readthedocs.io/en/0.3.5/reqparse.html
parser_get = parser.copy()
parser_get.add_argument("controller_id",
                        required=False,
                        type=int,
                        location="args",
                        help="Unknowed argument!")

parser_post = parser.copy()
parser_post.add_argument("controller_id", required=True,
                         location="json",
                         type=int,
                         help="Controller ID cannot be blank ")
parser_post.add_argument("rule_shema", required=True,
                         location="json",
                         type=dict,
                         help="Rull dict is required!")

parser_put = parser.copy()
parser_put.add_argument("rule_shema", required=True,
                        location="json",
                        type=dict,
                        help="Rull dict is required!")


class Rules(Resource):
    # Get request
    def get(self):
        args = parser_get.parse_args()
        if args["controller_id"] is not None:
            controller_rules = Rule.query.filter_by(controller_id=args["controller_id"]).order_by("updated_on")
            return [x.toDict() for x in controller_rules], 200
        else:
            all_rules = Rule.query.order_by("updated_on")
            return [x.toDict() for x in all_rules], 200

    # post request
    def post(self):
        args = parser_post.parse_args()
        fk_controller = Controller.query.filter_by(id=args["controller_id"]).first()
        if is_there_an_object(fk_controller):
            new_rule = Rule(
                controller_id=args["controller_id"],
                rule_shema=args["rule_shema"]
            )

            db.session.add(new_rule)
            db.session.commit()
            return new_rule.toDict(), 201
        else:
            return {
                "message": "Controller Obj not found!"
            }, 404


api.add_resource(Rules, "/api/rules/")


class CRule(Resource):

    # GET request
    def get(self, id):
        rule = Rule.query.filter_by(id=id).first()
        if is_there_an_object(rule):
            return rule.toDict(), 200
        else:
            return {
                "message": "Obj not found!"
            }, 404

    # put request
    def put(self, id):
        args = parser_put.parse_args()
        rule_to_update = Rule.query.filter_by(id=id).first()
        if is_there_an_object(rule_to_update):
            rule_to_update.rule_shema = args["rule_shema"],
            db.session.commit()
            return rule_to_update.toDict(), 201
        else:
            return {
                "message": "Obj not found!"
            }, 404


api.add_resource(CRule, "/api/rules/<int:id>/")

