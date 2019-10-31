import paho.mqtt.client as paho
import os
from time import sleep
import json
import sys
import logging
sys.path.insert(0, os.path.abspath('..'))
from configure_instructions_engine.conf_engine import InstructionGenerator
from en_de_crypter.en_de_crypter import EnDeCrypt

# logging.basicConfig(level=logging.INFO)


class MqttClientSub(object):
    def __init__(self, listener=False):

        self.sub_from_com_service = os.environ.get("COM_SERVICE_RAW_DATA_TO_EVENT_HANDLER")
        self.pub_to_com_service = os.environ.get("EVENT_HANDLER_INSTRUCTION_TO_COM_SERVICE")
        self.eh_user = os.environ.get("EH_MQTT_USER")
        self.eh_pwd = os.environ.get("EH_MQTT_PASSWORD")
        self.en_de_key = os.environ.get("CRYPTOGRAPHY_KEY")

        self.connect = False
        self.listener = listener

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))
        self.logger = self.__reg_logger()
        # self.logger = logging.getLogger(repr(self))

    def __reg_logger(self):
        # create logger
        logger = logging.getLogger(repr(self))
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        error_handler = logging.FileHandler('./logs/error_file.log')
        error_handler.setLevel(logging.ERROR)

        warning_handler = logging.FileHandler('./logs/warning_file.log')
        warning_handler.setLevel(logging.WARNING)

        critical_handler = logging.FileHandler('./logs/critical_file.log')
        critical_handler.setLevel(logging.CRITICAL)

        # create formatter
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
            self.mqttc.subscribe(self.sub_from_com_service)
            self.mqttc.message_callback_add(self.sub_from_com_service, self.on_message_from_com_service)
        self.logger.debug("\n{0}\n".format(rc))

    def on_message_from_com_service(self, client, userdata, msg):
        self.logger.info("\n[*] [<--] [EH][CS] New data from Communication Service.\n")
        try:
            decrypt_msg = json.loads(EnDeCrypt(self.en_de_key, msg.payload).DeCrypt())
        except Exception as e:
            self.logger.critical("\n[!] [EN_DE_CRYPTER] Fail to decrypt data from Communication Service!\nerr: {}\n".format(e))

        try:
            self.logger.info("\n[*] [++] [EH] create new instruction with new data.\n")
            instruction = InstructionGenerator(data=decrypt_msg, token=decrypt_msg["token"]).create_instruction()
        except Exception as e:
            self.logger.critical("\n[!] [INSTRUCTION GENERATOR] Fail to create new instruction!s\nerr: {}\n".format(e))

        try:
            instruction = json.dumps(instruction)
            encrypt_msg = EnDeCrypt(self.en_de_key, instruction).enCrypt()
        except Exception as e:
            self.logger.critical("\n[!] [EN_DE_CRYPTER] Fail to encrypt new instruction data!\nerr: {}\n".format(e))

        try:
            self.logger.info("\n[*] [-->] [EH][CS] New instruction sended to Communication Service.\n")
            self._mqttPubMsg(self.pub_to_com_service, encrypt_msg)
        except Exception as e:
            self.logger.critical("\n[!] [EN_DE_CRYPTER] Fail to send new instruction to Communication Service!\nerr: {}\n".format(e))

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
        self.logger.info("{0}".format("\n[*] [EH] [*]  Query listener is Up!\n"))
        self.mqttc.loop_start()

        while True:
            sleep(2)
            if self.connect is True:
                pass
            else:
                self.logger.debug("\n[!] [EH] [!] Attempting to connect!\n")

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

