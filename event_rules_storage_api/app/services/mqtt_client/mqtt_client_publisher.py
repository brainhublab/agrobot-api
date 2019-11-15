import paho.mqtt.client as paho
import logging
from time import sleep
from flask import current_app as app


class MqttClientPub(object):
    def __init__(self, listener=False):
        self.api_user = app.config["API_MQTT_USER"]
        self.api_pwd = app.config["API_MQTT_PASSWORD"]
        self.connect = False
        self.listener = listener

        self.broker_url = app.config["BROKER_HOST"]
        self.broker_port = int(app.config["BROKER_PORT"])
        self.logger = self.__reg_logger()

    def __reg_logger(self):
        # create logger
        logger = logging.getLogger(repr(self))
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create handler to write error logs in file
        log_reg = logging.FileHandler('./logs/api_mqtt_client_service.log')
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

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True
        self.logger.debug("\n{0}\n".format(rc))

    def on_message(self, client, userdata, msg):
        self.logger.info("\n{0}, {1} - {2}\n".format(userdata, msg.topic, msg.payload))
        pass

    def __on_log(self, client, userdata, level, buf):
        self.logger.info("\n[*][{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

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

    def pubUpdatedConfigs(self, topic, data):
        self.mqttc.loop_start()
        while True:
            print("")
            sleep(2)
            if self.connect is True:
                try:
                    self.mqttc.publish(topic, data, qos=1)
                    self.mqttc.loop_stop()
                    break
                except Exception as e:
                    raise e
            else:
                self.logger.debug("\n[!] [EH] [!] Attempting to connect!!\n")
