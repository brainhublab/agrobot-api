import paho.mqtt.client as paho
import os
from time import sleep
import json


class MqttCtrlClient(object):
    def __init__(self, ctrl_clients_refs, logger):
        """ take the basic topic names from envoirnment file"""
        self.communicaton_service_client_id = os.environ.get("COMMUNICATION_SERVICE_CLIENT_ID")

        self.controller_configs_receive = os.environ.get("CONTROLLER_CONFIGS") + "receive/"
        self.controller_configs_send = os.environ.get("CONTROLLER_CONFIGS") + "send/"

        self.controller_data_receive = os.environ.get("CONTROLLER_DATA")
        self.controller_logs_receive = os.environ.get("CONTROLLER_LOGS")

        self.controller_rules_receive = os.environ.get("CONTROLLER_RULES") + "receive/"
        self.controller_rules_send = os.environ.get("CONTROLLER_RULES") + "send/"

        self.api_config_update = os.environ.get("API_CONFIG_UPDATE")
        self.api_new_rule = os.environ.get("API_NEW_RULE")
        self.api_obj_delete = os.environ.get("API_OBJ_DELETE")

        self.event_handler_data = os.environ.get("EVENT_HANDLER_DATA")
        self.event_handler_rule = os.environ.get("EVENT_HANDLER_RULE")

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

        """ Create the required subscribers """
        client.subscribe(self.controller_configs_receive + client_id)
        client.subscribe(self.controller_rules_receive + client_id)
        client.subscribe(self.api_config_update + client_id)
        client.subscribe(self.api_obj_delete + client_id)
        client.subscribe(self.event_handler_rule + client_id)
        client.subscribe(self.controller_logs_receive + client_id)
        client.subscribe(self.controller_data_receive + client_id)

        client.message_callback_add(self.controller_configs_receive + client_id,
                                    self.on_message_from_controller_configs_receive)
        client.message_callback_add(self.controller_rules_receive + client_id,
                                    self.on_message_from_controller_rules_receive)
        client.message_callback_add(self.api_config_update + client_id,
                                    self.on_message_from_api_config_update)
        client.message_callback_add(self.api_obj_delete + client_id,
                                    self.on_disconnect)
        client.message_callback_add(self.event_handler_rule + client_id,
                                    self.on_message_from_event_handler_rule)
        client.message_callback_add(self.controller_data_receive + client_id,
                                    self.on_message_from_controller_data_receive)
        client.message_callback_add(self.controller_logs_receive + client_id,
                                    self.on_message_from_controller_logs_receive)

    """                              CALLBACKS                               """
    # CONTROLLER CONNECTION CALLBACKS
    def on_messagee(self, client, userdata, msg):
        self.logger.info("\n[???] [{0}], [{1}] - [{2}]\n".format(client._client_id, msg.topic, msg.payload))

    def on_message_from_api_config_update(self, client, userdata, msg):
        """ Function handling message from API for updated configs
                - publish new configs
        """
        client_id = client._client_id.decode()
        data = json.loads(msg.payload.decode())
        self._mqttPubMsg(client,
                         self.controller_configs_send + client_id,
                         json.dumps({"configs": data}))

    def on_message_from_controller_configs_receive(self, client, userdata, msg):
        pass
        # message = msg.payload.decode()
        # TODO: check what kind of message will come

    def on_message_from_controller_rules_receive(self, client, userdata, msg):
        pass
        # message = msg.payload.decode()
        # TODO: check what kind of message will come

    def on_message_from_controller_data_receive(self, client, userdata, msg):
        # tests
        equipped_msg = msg.payload.decode() + " [COMMUNICATION_SERVICE] " + client._client_id.decode()
        self._mqttPubMsg(client, self.event_handler_data, equipped_msg)

    def on_message_from_controller_logs_receive(self, client, userdata, msg):
        self.logger.warning("\n[!][*] [{0}] [CONTROLLER LOG] [{1}]".format(client._client_id.decode(), msg.payload.decode()))

    # EVENT HANDLER CONNECTION CALLBACKS
    def on_message_from_event_handler_rule(self, client, userdata, msg):
        # tests
        equipped_topic = self.controller_rules_send + client._client_id.decode()
        equipped_msg = msg.payload.decode() + " [COMMUNICATION_SERVICE]" + " " + client._client_id.decode()
        self._mqttPubMsg(client, equipped_topic, equipped_msg)

    def on_logg(self, client, userdata, level, buf):
        self.logger.info("\n[*] [{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

    def _broker_auth(self, client):
        client.username_pw_set(username=self.com_user, password=self.com_pwd)

    def on_disconnect(self, client, userdata, rc=0):
        client_id = client._client_id.decode()
        sub_topics = [self.controller_configs_receive, self.controller_rules_receive,
                      self.api_config_update, self.api_obj_delete, self.event_handler_rule,
                      self.controller_logs_receive, self.controller_data_receive]
        for topic in sub_topics:
            client.unsubscribe(topic + client_id)

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
