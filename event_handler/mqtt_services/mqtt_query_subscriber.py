import paho.mqtt.client as paho
import signal
import os
from time import sleep
import sys
import logging
sys.path.insert(0, os.path.abspath('..'))
from configure_instructions_engine.conf_engine import InstructionGenerator


class MqttClientSub(object):
    def __init__(self, listener=False):
        """ take the basic topic names from envoirnment file"""
        self.event_handler_client_id = os.environ.get("EVENT_HANDLER_CLIENT_ID")

        self.event_handler_data = os.environ.get("EVENT_HANDLER_DATA")
        self.event_handler_rule = os.environ.get("EVENT_HANDLER_RULE")

        self.eh_user = os.environ.get("EH_MQTT_USER")
        self.eh_pwd = os.environ.get("EH_MQTT_PASSWORD")

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))

        self.kill = False
        self.connect = False
        self.listener = listener
        self.logger = self.__reg_logger()

    def __reg_logger(self):
        # create logger
        logger = logging.getLogger(repr(self))
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create handler to write error logs in file
        os.makedirs(os.path.dirname("./logs/event_handler.log"), exist_ok=True)
        log_reg = logging.FileHandler("./logs/event_handler.log", mode="w", encoding=None, delay=False)
        log_reg.setLevel(logging.DEBUG)

        # create formatter for logger output
        formatter = logging.Formatter('\n[%(levelname)s] - %(asctime)s - %(name)s - %(message)s')

        # add formatter to handlers
        ch.setFormatter(formatter)
        log_reg.setFormatter(formatter)

        # add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(log_reg)
        return logger

    """     SUBSCRIBERS / CALLBACKS CONNECTION REGISTRY (every reconnection)    """
    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True
        if self.listener:
            self.mqttc.subscribe(self.event_handler_data)

            self.mqttc.message_callback_add(self.event_handler_data,
                                            self.on_message_from_event_handler_data)
        self.logger.debug("\n{0}\n".format(rc))

    """                              CALLBACKS                               """
    """ All function names are created from two parts
    'on_message_from' - show action type,
    second part - show name of topic variable """
    # CONTROLLER CONNECTION CALLBACKS
    def on_message(self, client, userdata, msg):
        self.logger.info("\n[???] [{0}], [{1}] - [{2}]\n".format(client._client_id, msg.topic, msg.payload))

    def on_message_from_event_handler_data(self, client, userdata, msg):
        ctrl_client_id = msg.payload.decode().split(" ")[-1]
        data = " ".join(msg.payload.decode().split(" ")[0:-1]) + " [EVENT HANDLER]"

        # TODO: Make instruction with new data
        # InstructionGenerator

        equipped_topic = self.event_handler_rule + "/" + ctrl_client_id
        try:
            self._mqttPubMsg(client, equipped_topic, data)
        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [EVENT_HANDLER_RULE] [PUB] "
                                  "Fail sent new config to Communication service's ctrl client.\nerr: {}\n").format(e))

    """                                UTILS                                 """
    def __on_log(self, client, userdata, level, buf):
        self.logger.info("\n[*][{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

    def _broker_auth(self, client):
        client.username_pw_set(username=self.eh_user, password=self.eh_pwd)

    def on_disconnect(self, client, userdata, rc=0):
        self.logger.info("\n[*] [DISCONNECT] [{0}]\n".format(client._client_id.decode()))

    """                            CLIENT CONFIGS                            """

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client(self.event_handler_client_id)
        self._broker_auth(self.mqttc)
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_log = self.__on_log
        self.mqttc.on_disconnect = self.on_disconnect

        result_of_connection = self.mqttc.connect(self.broker_url, self.broker_port, keepalive=120)
        if result_of_connection == 0:
            self.connect = True

        return self

    def seppuku(self, signum, frame):
        self.kill = True

    def start(self):
        self.logger.info("{0}".format("\n[*] [Query listeners are Up!]\n"))
        signal.signal(signal.SIGINT, self.seppuku)
        signal.signal(signal.SIGTERM, self.seppuku)

        while not self.kill:
            self.mqttc.loop()

    def _mqttPubMsg(self, client, topic, data):
        while True:
            sleep(2)
            try:
                client.publish(topic, data, qos=1)
                break
            except Exception as e:
                raise e
                continue
            else:
                self.logger.debug("\n[!] Attempting to connect!\n")
