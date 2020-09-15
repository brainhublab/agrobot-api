import os

SECRET_KEY = 'p9Bv<3Eid9%$i01'

# """ Use pymysql instead MySQLdb, because MySQLdb is not supported by Python3 """
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://local_admin:12345678@localhost/local_db'

HOST = "http://localhost:8081/"

POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")

BROKER_HOST = os.environ.get("BROKER_HOST")
BROKER_PORT = os.environ.get("BROKER_PORT")

CTRL_CONF_UPDATE = os.environ.get("CTRL_CONF_UPDATE")
API_OBJ_DELETE = os.environ.get("API_OBJ_DELETE")

API_MQTT_USER = os.environ.get("API_MQTT_USER")
API_MQTT_PASSWORD = os.environ.get("API_MQTT_PASSWORD")

TOKEN = os.environ.get("TOKEN")

SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(POSTGRES_USER,
                                                            POSTGRES_PASSWORD,
                                                            POSTGRES_HOST,
                                                            POSTGRES_DB)
