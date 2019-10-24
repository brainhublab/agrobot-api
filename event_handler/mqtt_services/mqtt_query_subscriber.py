import paho.mqtt.client as paho
from .mqtt_query_publisher import MqttClientPub
import os
import socket
import ssl
from time import sleep
from random import uniform
import json
import sys
import logging
sys.path.insert(0, os.path.abspath('..'))
from configure_instructions_engine.conf_engine import CongfGenerator

logging.basicConfig(level=logging.INFO)


class MqttClientSub(object):
    def __init__(self, listener=False):

        self.sub_from_com_service = os.environ.get("COM_SERVICE_RAW_DATA_TO_EVENT_HANDLER")
        self.pub_to_com_service = os.environ.get("EVENT_HANDLER_INSTRUCTION_TO_COM_SERVICE")
        self.eh_user = os.environ.get("EH_MQTT_USER")
        self.eh_pwd = os.environ.get("EH_MQTT_PASSWORD")

        self.connect = False
        self.listener = listener

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))
        self.logger = logging.getLogger(repr(self))

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True

        if self.listener:
            self.mqttc.subscribe(self.sub_from_com_service)
            self.mqttc.message_callback_add(self.sub_from_com_service, self.on_message_from_com_service)
        self.logger.debug("{0}".format(rc))

    def on_message_from_com_service(self, client, userdata, msg):
        print("[*][EH][CS] New data from communication service")

        mesg = json.loads(msg.payload)["message"]
        print(mesg)
        try:
            print("[*][EH] create new instruction with new data.")
            response = CongfGenerator(data=mesg, token=mesg["token"]).create_instruction()
        except Exception as e:
            raise e

        try:
            print("[*][EH][CS] New instruction sended to communication service")
            print(response)
            MqttClientPub(topic=self.pub_to_com_service,
                          broker_url=self.broker_url,
                          broker_port=self.broker_port, data=response).bootstrap_mqtt().start()
        except Exception as e:
            raise e

    def on_message(self, client, userdata, msg):
        self.logger.info("{0}, {1} - {2}".format(userdata, msg.topic, msg.payload))

    def __on_log(self, client, userdata, level, buf):
        self.logger.debug("{0}, {1}, {2}, {3}".format(client, userdata, level, buf))

    def _broker_auth(self):
        self.mqttc.username_pw_set(username=self.eh_user, password=self.eh_pwd)

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client()
        self._broker_auth()
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
        self.logger.info("{0}".format("[*][EH][*]  Query listener is Up!"))
        self.mqttc.loop_start()

        while True:
            sleep(2)
            if self.connect == True:
                pass
            else:
                self.logger.debug("[!][EH] Attempting to connect.")

