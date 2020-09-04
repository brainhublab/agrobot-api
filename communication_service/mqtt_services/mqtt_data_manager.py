import paho.mqtt.client as paho
import os, sys
from time import sleep
sys.path.insert(0, os.path.abspath('..'))
from .db_manager import DBmanager

db_manager = DBmanager


class MqttDataManager(object):
    def __init__(self, logger):
        """ basic topic """
        self.controller_data_receive = os.environ.get("CONTROLLER_DATA")

        self.com_user = os.environ.get("COM_MQTT_USER")
        self.com_pwd = os.environ.get("COM_MQTT_PASSWORD")

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))

        self.kill = False
        self.connect = False
        self.logger = logger

    """                              CALLBACKS                               """
    def on_connect(self, client, userdata, flags, rc):

        """ Create the required subscribers """
        client.subscribe(self.controller_data_receive + "#")

        client.message_callback_add(self.controller_data_receive + "#",
                                    self.on_message_ctrl_data)
        self.db_mngr = db_manager()
        self.db_mngr.connect()

    def on_message_ctrl_data(self, client, userdata, msg):
        mac = msg.topic.split("/")[-1]
        self.db_mngr.feed_or_create(mac, mac, 11)

    def on_message(self, client, userdata, msg):
        self.logger.info("\n[???] [{0}], [{1}] - [{2}]\n".format(client._client_id, msg.topic, msg.payload))

    def on_log(self, client, userdata, level, buf):
        self.logger.info("\n[*] [{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

    def _broker_auth(self, client):
        client.username_pw_set(username=self.com_user, password=self.com_pwd)

    def on_disconnect(self, client, userdata, rc=0):
        client.unsubscribe(self.controller_data_receive + "#")
        """ Disconnect controller client and remove from client references list"""
        client.disconnect()
        client.loop_stop()
        self.logger.info("\n[*] [DISCONNECT] [{0}]\n".format(client._client_id.decode()))

    """                            CLIENT CONFIGS                            """
    def bootstrap(self):
        mqtt_controller_cli = paho.Client(client_id="data_manager", clean_session=False,
                                          protocol=paho.MQTTv311)
        self._broker_auth(mqtt_controller_cli)
        mqtt_controller_cli.on_connect = self.on_connect
        mqtt_controller_cli.on_message = self.on_message
        mqtt_controller_cli.on_log = self.on_log
        mqtt_controller_cli.on_disconnect = self.on_disconnect
        result_of_connection = mqtt_controller_cli.connect(self.broker_url, self.broker_port, keepalive=120)
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
