import paho.mqtt.client as paho
import os
from time import sleep
import json
import sys
import logging
sys.path.insert(0, os.path.abspath('..'))
from http_requests.requestss import LocalServerRequests
from en_de_crypter.en_de_crypter import EnDeCrypt

logging.basicConfig(level=logging.INFO)


class MqttClientSub(object):
    def __init__(self, listener=False):
        self.sub_from_ctrl_topic = os.environ.get("CONTROLLER_RAW_DATA_TO_COM_SERVICE")
        self.sub_from_event_handler_topic = os.environ.get("EVENT_HANDLER_INSTRUCTION_TO_COM_SERVICE")
        self.pub_to_event_handler_topic = os.environ.get("COM_SERVICE_RAW_DATA_TO_EVENT_HANDLER")
        self.pub_to_ctrl_topic = os.environ.get("COM_SERVICE_INSTRUCTIONS_TO_CONTROLLER")
        self.eh_user = os.environ.get("COM_MQTT_USER")
        self.eh_pwd = os.environ.get("COM_MQTT_PASSWORD")
        self.en_de_key = os.environ.get("CRYPTOGRAPHY_KEY")

        self.connect = False
        self.listener = listener

        self.auth_token = os.environ.get("TOKEN")

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))
        self.logger = logging.getLogger(repr(self))

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True

        if self.listener:
            self.mqttc.subscribe(self.sub_from_ctrl_topic)
            self.mqttc.subscribe(self.sub_from_event_handler_topic)
            self.mqttc.message_callback_add(self.sub_from_ctrl_topic, self.on_message_from_controller)
            self.mqttc.message_callback_add(self.sub_from_event_handler_topic, self.on_message_from_handler)
        self.logger.debug("{0}".format(rc))

    def on_message_from_controller(self, client, userdata, msg):
        print("[*] [<--] [CS][CO] New data from Controller.\n")
        decrypt_mesg = json.loads(EnDeCrypt(self.en_de_key, msg.payload).DeCrypt())
        try:
            print("[*] [-->] [CS][GA] New data sended to Global API\n")
            LocalServerRequests(self.auth_token, decrypt_mesg).post_sensor_raw_data()
        except Exception as e:
            raise e
        try:
            print("[*] [-->] [CS][CO] New data sended to Handler.\n")
            self._mqttPubMsg(self.pub_to_event_handler_topic, msg.payload)
        except Exception as e:
            raise e

    def on_message_from_handler(self, client, userdata, msg):
        """Just resent data from handler to controller"""
        try:
            print("[*] [<--] [CS][EH] New instruction come from Handler\n")
            print("[*] [-->] [CS][CO] New instruction sended to Controller\n")

            self._mqttPubMsg(self.pub_to_ctrl_topic, msg.payload)
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

        result_of_connection = self.mqttc.connect(self.broker_url, self.broker_port, keepalive=120)
        if result_of_connection == 0:
            self.connect = True

        return self

    def start(self):
        self.logger.info("{0}".format("[*] [CS] [*] Query listener is Up!\n"))
        self.mqttc.loop_start()

        while True:
            sleep(2)
            if self.connect is True:
                pass
            else:
                self.logger.debug("[!] [CS] [!] Attempting to connect!\n")

    def _mqttPubMsg(self, topic, data):
        while True:
            sleep(2)
            if self.connect is True:
                self.mqttc.publish(topic, data, qos=1)
                break
            else:
                self.logger.debug("[!] [EH] [!] Attempting to connect!\n")

