import paho.mqtt.client as paho
import logging
logging.basicConfig(level=logging.INFO)


class MqttClientPub(object):

    def __init__(self, topic="default", broker_url="localhost", broker_port=1883, data={}):
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
        self.mqttc = paho.Client(protocol=paho.MQTTv311)
        self._broker_auth()
        self.mqttc.on_connect = self.__on_connect
        result_of_connection = self.mqttc.connect(self.broker_url, self.broker_port, keepalive=120)
        if result_of_connection == 0:
            self.connect = True
        return self

    def start(self):
        self.mqttc.loop_start()
        while True:

            if self.connect is True:
                self.mqttc.publish(self.topic, self.data, qos=2)
                self.mqttc.loop_stop()
                break

            else:
                self.logger.debug("Attempting to connect.")


# Example of usage
# Change values in need
log = "Some Errors"
MqttClientPub(topic="ctrl/MAC7ELEVEN/logs",
              broker_url="localhost", broker_port=1883, data=log).bootstrap_mqtt().start()
