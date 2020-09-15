# import json
# from sqlalchemy.ext import mutable
# from app import db
#
#
# class JsonEncodedDict(db.TypeDecorator):
#     """Enables JSON storage by encoding and decoding on the fly."""
#     impl = db.Text
#
#     def process_bind_param(self, value, dialect):
#         if value is None:
#             return '{}'
#         else:
#             return json.dumps(value)
#
#     def process_result_value(self, value, dialect):
#         if value is None:
#             return {}
#         else:
#             return json.loads(value)
#
#
# mutable.MutableDict.associate_with(JsonEncodedDict)
#
