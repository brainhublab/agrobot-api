import paho.mqtt.client as paho
import os, sys
from time import sleep
import json
sys.path.insert(0, os.path.abspath('..'))
from .ctrl_types_shema import types
from .db_manager import DBmanager

db_manager = DBmanager


class MqttCtrlClient(object):
    def __init__(self, ctrl_clients_refs, logger):
        """ take the basic topic names from envoirnment file"""
        self.ctrl_data_out = os.environ.get("CTRL_DATA_OUT")
        self.ctrl_logs = os.environ.get("CTRL_LOGS")
        self.ctrl_health = os.environ.get("CTRL_HEALTH")

        self.api_obj_delete = os.environ.get("API_OBJ_DELETE")

        self.com_user = os.environ.get("COM_MQTT_USER")
        self.com_pwd = os.environ.get("COM_MQTT_PASSWORD")

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))

        self.ctrl_clients_refs = ctrl_clients_refs
        self.logger = logger

    """     SUBSCRIBERS / CALLBACKS CONNECTION REGISTRY (every reconnection)    """
    def on_connect(self, client, userdata, flags, rc):
        """ client_id is MAC address of controller/sensor """
        client_id = client._client_id.decode()
        self.db_mngr = db_manager()
        self.db_mngr.connect()

        """ Create the required subscribers """
        client.subscribe(self.api_obj_delete + client_id)
        client.subscribe(self.ctrl_data_out.format(client_id) + "#")
        client.subscribe(self.ctrl_logs.format(client_id))
        client.subscribe(self.ctrl_health.format(client_id))

        client.message_callback_add(self.api_obj_delete + client_id,
                                    self.on_disconnect)
        client.message_callback_add(self.ctrl_data_out.format(client_id) + "#",
                                    self.on_message_from_ctrl_data_out)
        client.message_callback_add(self.ctrl_logs.format(client_id),
                                    self.on_message_from_ctrl_logs)
        client.message_callback_add(self.ctrl_health.format(client_id),
                                    self.on_message_from_ctrl_health)

    """                              CALLBACKS                               """
    def on_messagee(self, client, userdata, msg):
        self.logger.info("\n[???] [{0}], [{1}] - [{2}]\n".format(client._client_id, msg.topic, msg.payload))

    def on_message_from_ctrl_data_out(self, client, userdata, msg):
        # Store data in db
        mac = client._client_id.decode()
        message = msg.payload.decode()
        self.db_mngr.feed_or_create(mac, mac, int(message))

    def on_message_from_ctrl_logs(self, client, userdata, msg):
        self.logger.warning("\n[!][*] [{0}] [CONTROLLER LOG] [{1}]".format(client._client_id.decode(), msg.payload.decode()))

    def on_message_from_ctrl_health(self, client, userdata, msg):
        # TODO: store the data from healthcheck
        print(msg.payload.decode())

    def on_logg(self, client, userdata, level, buf):
        self.logger.info("\n[*] [{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

    def _broker_auth(self, client):
        client.username_pw_set(username=self.com_user, password=self.com_pwd)

    def on_disconnect(self, client, userdata, rc=0):
        self.db_mngr.disconnect()
        client_id = client._client_id.decode()
        sub_topics = [self.api_obj_delete, self.ctrl_data_out.format(client_id) + "#",
                      self.ctrl_logs.format(client_id), self.ctrl_health.format(client_id)]
        for topic in sub_topics:
            client.unsubscribe(topic)

        if client in self.ctrl_clients_refs:
            self.ctrl_clients_refs.remove(client)
        client.disconnect()
        client.loop_stop()
        self.logger.info("\n[*] [DISCONNECT] [{0}]\n".format(client_id))

    """                            CLIENT CONFIGS                            """
    def bootstrap(self, client_id):
        mqtt_controller_cli = paho.Client(client_id=client_id, protocol=paho.MQTTv311)
        self._broker_auth(mqtt_controller_cli)
        mqtt_controller_cli.on_connect = self.on_connect
        mqtt_controller_cli.on_message = self.on_messagee
        mqtt_controller_cli.on_log = self.on_logg
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
