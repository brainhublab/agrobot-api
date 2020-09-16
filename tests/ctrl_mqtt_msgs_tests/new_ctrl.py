import paho.mqtt.client as paho
from time import sleep
import json
import logging
logging.basicConfig(level=logging.INFO)


# Refactored original source - https://github.com/mariocannistra/python-paho-mqtt-for-aws-iot

class MqttClientPub(object):

    def __init__(self, topic="ControllerConfigs/auth", broker_url="localhost", broker_port=1883, data={}):
        # use mosquitto user password from environment
        self.ctrl_user = "miagiContr"
        self.ctrl_pwd = "1"

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
        self.mqttc.username_pw_set(username=self.ctrl_user, password=self.ctrl_pwd)

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client("ASd")
        self._broker_auth()
        self.mqttc.on_connect = self.__on_connect

        result_of_connection = self.mqttc.connect(self.broker_url, self.broker_port, keepalive=120)
        if result_of_connection == 0:
            self.connect = True
        return self

    def start(self):
        self.mqttc.loop_start()
        print(self.topic)
        self._mqttPubMsg(self.topic, self.data,)
        self.mqttc.disconnect()
        self.mqttc.loop_stop()

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


# Example of usage
# Change values in need
data = {"mac_addr": "MAC7ELEVEN",
        "mcu_type": "lightControl",  # 'mcu_type' need to exist in choices on api- available: (waterLevel, lightControl)
        "title": "First Water Level Ever"}
MqttClientPub(topic="ctrl/auth",
              broker_url="localhost", broker_port=1883, data=json.dumps(data)).bootstrap_mqtt().start()
