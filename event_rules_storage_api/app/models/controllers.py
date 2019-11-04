from app import db
from flask_sqlalchemy import inspect
import datetime
from sqlalchemy.sql import func


class Controller(db.Model):
    __tablename__ = "controllers"

    id = db.Column(db.Integer, primary_key=True)
    mac_addr = db.Column(db.Text(), unique=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text())
    pins_configuration = db.Column(db.JSON)

    created_on = db.Column(db.DateTime, default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    # created_on = db.Column(db.DateTime, server_default=db.func.now())
    # updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def toDict(self):
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        data["created_on"] = data["created_on"].strftime("%Y-%m-%d %H:%M")
        if data["updated_on"]:
            data["updated_on"] = data["updated_on"].strftime("%Y-%m-%d %H:%M")
        return data

