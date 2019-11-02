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

LOCAL_API_TO_COM_SERVICE = os.environ.get("LOCAL_API_TO_COM_SERVICE")
CRYPTOGRAPHY_KEY = os.environ.get("CRYPTOGRAPHY_KEY")

API_MQTT_USER = os.environ.get("API_MQTT_USER")
API_MQTT_PASSWORD = os.environ.get("API_MQTT_PASSWORD")

TOKEN = os.environ.get("TOKEN")
# SQLALCHEMY_DATABASE_URI = "postgresql://testadmin:testtest@db/testdb"

# TOKEN = "fe742bcb7bfa0c3ff680be5f84118321c2d2088b"
SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(POSTGRES_USER,
                                                            POSTGRES_PASSWORD,
                                                            POSTGRES_HOST,
                                                            POSTGRES_DB)

