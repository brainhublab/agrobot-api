import paho.mqtt.client as paho
import os
import logging
import json
from time import sleep
from flask import current_app as app
from ..en_de_crypter.en_de_crypter import EnDeCrypt


class MqttClientPub(object):
    def __init__(self, listener=False, data={}):
        self.data = data
        self.pub_to_com_service = app.config["LOCAL_API_TO_COM_SERVICE"]
        self.api_user = app.config["API_MQTT_USER"]
        self.api_pwd = app.config["API_MQTT_PASSWORD"]
        self.en_de_key = app.config["CRYPTOGRAPHY_KEY"]

        self.connect = False
        self.listener = listener

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))
        self.logger = self.__reg_logger()

    def __reg_logger(self):
        # create logger
        logger = logging.getLogger(repr(self))
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create handler to write error logs in file
        error_handler = logging.FileHandler('./logs/error_file.log')
        error_handler.setLevel(logging.ERROR)

        # create  handler to write warning logs in file
        warning_handler = logging.FileHandler('./logs/warning_file.log')
        warning_handler.setLevel(logging.WARNING)

        # create  handler to write critical logs in file
        critical_handler = logging.FileHandler('./logs/critical_file.log')
        critical_handler.setLevel(logging.CRITICAL)

        # create formatter for logger output
        formatter = logging.Formatter('\n[%(levelname)s] - %(asctime)s - %(name)s - %(message)s')

        # add formatter to handlers
        ch.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        warning_handler.setFormatter(formatter)
        critical_handler.setFormatter(formatter)

        # add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(error_handler)
        logger.addHandler(warning_handler)
        logger.addHandler(critical_handler)

        return logger

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True

        # if self.listener:
        #     self.mqttc.subscribe(self.sub_from_com_service)
        #     self.mqttc.message_callback_add(self.sub_from_com_service, self.on_message_from_com_service)
        self.logger.debug("\n{0}\n".format(rc))

    def on_message(self, client, userdata, msg):
        self.logger.info("\n{0}, {1} - {2}\n".format(userdata, msg.topic, msg.payload))

    def __on_log(self, client, userdata, level, buf):
        self.logger.debug("\n{0}, {1}, {2}, {3}\n".format(client, userdata, level, buf))

    def _broker_auth(self):
        self.mqttc.username_pw_set(username=self.api_user, password=self.api_pwd)

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
        self.mqttc.loop_start()
        while True:
            sleep(2)
            if self.connect is True:
                try:
                    data = json.dumps(self.data)
                    encrypt_data = EnDeCrypt(self.en_de_key, data).enCrypt()
                except Exception as e:
                    self.logger.critical("\n[!] [EN_DE_CRYPTER] Fail to encrypt new instruction data!\nerr: {}\n".format(e))
                    raise e

                try:
                    self.mqttc.publish(self.pub_to_com_service, encrypt_data, qos=1)
                    self.mqttc.loop_stop()
                    self.logger.info("\n[*] [-->] [API][CS] New Rule sended to Communication Service.\n")
                    break
                except Exception as e:
                    self.logger.critical("\n[!] [--] [API][CS] Fail to send new Rule to Communication Service!\nerr: {}\n".format(e))
                    raise e
            else:
                self.logger.debug("\n[!] [EH] [!] Attempting to connect!\n")

