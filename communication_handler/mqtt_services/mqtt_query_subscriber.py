import paho.mqtt.client as paho
import os
import socket
import ssl
from time import sleep
from random import uniform
import json
import sys
sys.path.insert(0, os.path.abspath('..'))
# import sys
from http_requests.requestсссs import post_sensor_raw_data

import logging
logging.basicConfig(level=logging.INFO)

auth_token = os.environ.get("TOKEN")
print(auth_token)

# Refactored original source - https://github.com/mariocannistra/python-paho-mqtt-for-aws-iot


class MqttClientSub(object):

    def __init__(self, listener=False, topic="default", broker_url="localhost", broker_port="1883"):
        self.connect = False
        self.listener = listener
        self.topic = topic
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.logger = logging.getLogger(repr(self))

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True

        if self.listener:
            self.mqttc.subscribe(self.topic)

        self.logger.debug("{0}".format(rc))

    def on_message(self, client, userdata, msg):
        mesg = json.loads(msg.payload)["message"]
        try:
            post_sensor_raw_data(auth_token, mesg["sensor_id"],
                                 mesg["title"], mesg["value"])
        except Exception as e:
            raise e

        # print(mesg)
        # print(mesg["title"])
        # print(mesg["sensor_id"])
        # print(mesg["value"])
        self.logger.info("{0}, {1} - {2}".format(userdata, msg.topic, msg.payload))

    def __on_log(self, client, userdata, level, buf):
        self.logger.debug("{0}, {1}, {2}, {3}".format(client, userdata, level, buf))

    def bootstrap_mqtt(self):

        self.mqttc = paho.Client()
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_log = self.__on_log

        # broker_url = os.environ.get("BROKER_HOST")
        # broker_port = os.environ.get("BROKER_PORT")
        # broker_url = "localhost"
        # broker_port = 1883

        # caPath = "./authority.pem" # Root certificate authority, comes from AWS with a long, long name
        # certPath = "./2bafa20887-certificate.pem.crt"
        # keyPath = "./2bafa20887-private.pem.key"
        #
        # self.mqttc.tls_set(caPath,
        #     certfile=certPath,
        #     keyfile=keyPath,
        #     cert_reqs=ssl.CERT_REQUIRED,
        #     tls_version=ssl.PROTOCOL_TLSv1_2,
        #     ciphers=None)

        result_of_connection = self.mqttc.connect(self.broker_url, self.broker_port, keepalive=120)

        if result_of_connection == 0:
            self.connect = True

        return self

    def start(self):
        self.mqttc.loop_start()

        while True:
            sleep(2)
            if self.connect == True:
                pass
                # self.mqttc.publish(self.topic, json.dumps({"message": "Hello COMP680"}), qos=1)
            else:
                self.logger.debug("Attempting to connect.")


    # PubSub(listener=True, topic="chat-evets").bootstrap_mqtt().start()

