import paho.mqtt.client as paho
import os
import socket
import ssl
from time import sleep
from random import uniform
import json

import logging
logging.basicConfig(level=logging.INFO)


class MqttClientPub(object):

    def __init__(self, topic="default", broker_url="localhost", broker_port=1883, data=""):
        self.eh_user = os.environ.get("EH_MQTT_USER")
        self.eh_pwd = os.environ.get("EH_MQTT_PASSWORD")

        self.connect = False
        self.topic = topic
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.data = data
        self.logger = logging.getLogger(repr(self))

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True
        self.logger.debug("{0}".format(rc))

    def _broker_auth(self):
        self.mqttc.username_pw_set(username=self.eh_user, password=self.eh_pwd)

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client()
        self._broker_auth()
        self.mqttc.on_connect = self.__on_connect

        result_of_connection = self.mqttc.connect(self.broker_url, self.broker_port, keepalive=120)
        if result_of_connection == 0:
            self.connect = True
        return self

    def start(self):
        self.mqttc.loop_start()

        while True:
            sleep(2)
            if self.connect == True:
                self.mqttc.publish(self.topic, self.data, qos=1)
                self.mqttc.loop_stop()
                break

            else:
                self.logger.debug("Attempting to connect.")

