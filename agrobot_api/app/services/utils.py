from flask_restful import reqparse
from functools import wraps
from flask import current_app as app

parser = reqparse.RequestParser()
parser.add_argument("Authorization",
                    location="headers", required=True)


def auth_check(funk):
    @wraps(funk)
    def duth_dec(*args, **kwargs):
        env_token = app.config["TOKEN"]
        args = parser.parse_args()
        try:
            token = args["Authorization"].split()[-1]
        except Exception as e:
            return {"message": e}, 401
        if env_token != token:
            return None, 403
            # return {"message": "Bad Token provided!"}, 403
        return funk(*args, **kwargs)
    return duth_dec


def is_there_an_object(obj):
    if obj is None:
        return False
    else:
        return True
