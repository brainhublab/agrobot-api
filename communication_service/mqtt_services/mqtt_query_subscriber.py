import paho.mqtt.client as paho
import os
from time import sleep
import json
import sys
import logging
sys.path.insert(0, os.path.abspath('..'))
from http_requests.requestss import LocalServerRequests
from en_de_crypter.en_de_crypter import EnDeCrypt


class MqttClientSub(object):
    def __init__(self, listener=False):
        self.sub_from_ctrl_topic = os.environ.get("CONTROLLER_RAW_DATA_TO_COM_SERVICE")
        self.sub_from_event_handler_topic = os.environ.get("EVENT_HANDLER_INSTRUCTION_TO_COM_SERVICE")
        self.sub_from_api = os.environ.get("LOCAL_API_TO_COM_SERVICE")
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

        if self.listener:
            self.mqttc.subscribe(self.sub_from_ctrl_topic)
            self.mqttc.subscribe(self.sub_from_event_handler_topic)
            self.mqttc.subscribe(self.sub_from_api)

            self.mqttc.message_callback_add(self.sub_from_ctrl_topic, self.on_message_from_controller)
            self.mqttc.message_callback_add(self.sub_from_event_handler_topic, self.on_message_from_handler)
            self.mqttc.message_callback_add(self.sub_from_api, self.on_message_from_api)
        self.logger.debug("\n{0}\n".format(rc))

    def on_message_from_controller(self, client, userdata, msg):
        self.logger.info("\n[*] [<--] [CS][CO] New data from Controller.\n")
        try:
            decrypt_mesg = json.loads(EnDeCrypt(self.en_de_key, msg.payload).DeCrypt())
        except Exception as e:
            self.logger.critical("\n[!] [EN_DE_CRYPTER] Fail to decrypt data from Controller\nerr: {}\n".format(e))

        try:
            LocalServerRequests(self.auth_token, decrypt_mesg).post_sensor_raw_data()
            self.logger.info("\n[*] [-->] [CS][GA] New data sended to Global API\n")
        except Exception as e:
            self.logger.warning("\n[!] [--] [CS][GA] Fail send data to Global API\nerr: {}\n".format(e))

        try:
            self._mqttPubMsg(self.pub_to_event_handler_topic, msg.payload)
            self.logger.info("\n[*] [-->] [CS][CO] New data sended to Handler.\n")
        except Exception as e:
            self.logger.critical("\n[!][!] [--] [CS][CO] Fail send data to Handler.\nerr: {}\n".format(e))

    def on_message_from_handler(self, client, userdata, msg):
        """Just resent data from handler to controller"""
        try:
            self.logger.info("\n[*] [<--] [CS][EH] New instruction come from Handler\n")
            self._mqttPubMsg(self.pub_to_ctrl_topic, msg.payload)
            self.logger.info("\n[*] [-->] [CS][CO] New instruction sended to Controller\n")
        except Exception as e:
            self.logger.critical("\n[!][!] [--] [CS][CO] Fail send data to Controller.\nerr: {}\n".format(e))

    def on_message_from_api(self, client, userdata, msg):
        """ Resent ping message for new rule from API to controller """
        try:
            self.logger.info("\n[*] [<--] [CS][API] New message come from API\n")
            self._mqttPubMsg(self.pub_to_ctrl_topic, msg.payload)
            self.logger.info("\n[*] [-->] [CS][CO] New message sended to Controller\n")
        except Exception as e:
            self.logger.critical("\n[!][!] [--] [CS][CO] Fail send message to Controller.\nerr: {}\n".format(e))

    def on_message(self, client, userdata, msg):
        self.logger.info("\n{0}, {1} - {2}\n".format(userdata, msg.topic, msg.payload))

    def __on_log(self, client, userdata, level, buf):
        self.logger.debug("\n{0}, {1}, {2}, {3}\n".format(client, userdata, level, buf))

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
        self.logger.info("{0}".format("\n[*] [CS] [*] Query listener is Up!\n"))
        self.mqttc.loop_start()

        while True:
            sleep(2)
            if self.connect is True:
                pass
            else:
                self.logger.debug("\n[!] [CS] [!] Attempting to connect!\n")

    def _mqttPubMsg(self, topic, data):
        while True:
            sleep(2)
            if self.connect is True:
                try:
                    self.mqttc.publish(topic, data, qos=1)
                    break
                except Exception as e:
                    raise e
            else:
                self.logger.debug("\n[!] [EH] [!] Attempting to connect!\n")

