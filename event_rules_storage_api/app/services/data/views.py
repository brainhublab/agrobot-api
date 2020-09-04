from . import api
from flask import current_app as app
from ... import db
from ..utils import parser, auth_check
from flask_restful import Resource

parser_post = parser.copy()


class DataViews(Resource):
    @auth_check
    def get(self):
        pass
        # all_data = SData.query.order_by("date")
        # return [x.toDict() for x in all_data], 200


api.add_resource(DataViews, "/api/data/")


class DataTest(Resource):
    @auth_check
    def get(self, mac):
        pass
        # sensor_data = SData.query.filter_by(mac=mac)
        # return [x.toDict() for x in sensor_data], 200


api.add_resource(DataTest, "/api/data/<int:mac>/")
