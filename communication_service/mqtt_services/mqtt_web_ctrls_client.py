import paho.mqtt.client as paho
import os
from time import sleep
import json


class MqttCtrlWebClient(object):
    def __init__(self, logger):
        """ basic topic """
        self.ui_ctrl_data = os.environ.get("UI_CONTROLLER_DATA")
        self.ui_ctrl_logs = os.environ.get("UI_CONTROLLER_LOGS")
        self.controller_data_receive = os.environ.get("CONTROLLER_DATA")
        self.controller_logs_receive = os.environ.get("CONTROLLER_LOGS")

        self.com_user = os.environ.get("COM_MQTT_USER")
        self.com_pwd = os.environ.get("COM_MQTT_PASSWORD")

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_webs_port = int(os.environ.get("BROKER_WEBSOCKET_PORT"))

        self.kill = False
        self.connect = False
        self.logger = logger
        
    """                              CALLBACKS                               """
    def on_connect(self, client, userdata, flags, rc):
        """ Create the required subscribers """
        client.subscribe(self.controller_data_receive + "#")
        client.subscribe(self.controller_logs_receive + "#")

        client.message_callback_add(self.controller_data_receive + "#",
                                    self.on_message_ctrl_data)
        client.message_callback_add(self.controller_logs_receive + "#",
                                    self.on_message_ctrls_log)

    def on_message_ctrl_data(self, client, userdata, msg):
        self._mqttPubMsg(client, self.ui_ctrl_data + msg.topic.split("/")[-1], msg.payload.decode())

    def on_message_ctrls_log(self, client, userdata, msg):
        self._mqttPubMsg(client, self.ui_ctrl_logs + msg.topic.split("/")[-1], msg.payload)

    def on_message(self, client, userdata, msg):
        self.logger.info("\n[???] [{0}], [{1}] - [{2}]\n".format(client._client_id, msg.topic, msg.payload))

    def on_log(self, client, userdata, level, buf):
        self.logger.info("\n[*] [{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

    def _broker_auth(self, client):
        client.username_pw_set(username=self.com_user, password=self.com_pwd)

    def on_disconnect(self, client, userdata, rc=0):
        client_id = client._client_id.decode()
        sub_topics = [self.controller_logs_receive + "#", self.controller_data_receive + "#"]

        for topic in sub_topics:
            client.unsubscribe(topic + client_id[1:])
        """ Disconnect controller client and remove from client references list"""
        client.disconnect()
        client.loop_stop()
        self.logger.info("\n[*] [DISCONNECT] [{0}]\n".format(client._client_id.decode()))

    """                            CLIENT CONFIGS                            """
    def bootstrap(self):
        mqtt_controller_cli = paho.Client(client_id="web_cli", clean_session=False,
                                          protocol=paho.MQTTv311, transport='websockets')
        self._broker_auth(mqtt_controller_cli)
        mqtt_controller_cli.on_connect = self.on_connect
        mqtt_controller_cli.on_message = self.on_message
        mqtt_controller_cli.on_log = self.on_log
        mqtt_controller_cli.on_disconnect = self.on_disconnect
        result_of_connection = mqtt_controller_cli.connect(self.broker_url, self.broker_webs_port, keepalive=120)
        if result_of_connection == 0:
            mqtt_controller_cli.loop_start()
        return mqtt_controller_cli

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
