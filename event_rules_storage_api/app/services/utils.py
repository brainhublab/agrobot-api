from flask_restful import reqparse

parser = reqparse.RequestParser()
# parser.add_argument("Authorization",
                    # location="headers", required=True)


def is_there_an_object(obj):
    if obj is None:
        return False
    else:
        return True

