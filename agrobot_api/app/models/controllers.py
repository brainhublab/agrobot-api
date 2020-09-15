from app import db
from flask_sqlalchemy import inspect
import datetime
from sqlalchemy.sql import func
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy_utils.types.choice import Choice


class Controller(db.Model):
    __tablename__ = "controllers"
    mcuTypes = [
        (u'waterLevel', u'Water level'),
        (u'lightControl', u'Light control')
    ]

    id = db.Column(db.Integer, primary_key=True)
    mcuType = db.Column(ChoiceType(mcuTypes))
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    macAddr = db.Column(db.Text(), unique=True)
    isConfigured = db.Column(db.Boolean, default=False)
    graph = db.Column(db.JSON)
    esp_config = db.Column(db.JSON)
    selfCheck = db.Column(db.Boolean, default=False)

    created_on = db.Column(db.DateTime, default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    def toDict(self):
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        if isinstance(data["mcuType"], Choice):
            data["mcuType"] = data["mcuType"].code
        data["created_on"] = data["created_on"].strftime("%Y-%m-%d %H:%M")
        if data["updated_on"]:
            data["updated_on"] = data["updated_on"].strftime("%Y-%m-%d %H:%M")
        return data
