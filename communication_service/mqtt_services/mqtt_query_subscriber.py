import paho.mqtt.client as paho
import signal
import os
from time import sleep
import json
import sys
import logging
sys.path.insert(0, os.path.abspath('..'))
from http_requests.requestss import LocalServerRequests


class MqttClientSub(object):
    def __init__(self, listener=False):
        """ take the basic topic names from envoirnment file"""
        self.communicaton_service_client_id = os.environ.get("COMMUNICATION_SERVICE_CLIENT_ID")
        self.new_controller_receive = os.environ.get("RECEIVE_NEW_CONTROLLER")

        self.controller_configs_receive = os.environ.get("CONTROLLER_CONFIGS") + "/receive"
        self.controller_configs_send = os.environ.get("CONTROLLER_CONFIGS") + "/send"

        self.controller_data_receive = os.environ.get("CONTROLLER_DATA")
        self.controller_logs_receive = os.environ.get("CONTROLLER_LOGS")

        self.controller_rules_receive = os.environ.get("CONTROLLER_RULES") + "/receive"
        self.controller_rules_send = os.environ.get("CONTROLLER_RULES") + "/send"

        self.api_config_update = os.environ.get("API_CONFIG_UPDATE")
        self.api_new_rule = os.environ.get("API_NEW_RULE")
        self.api_obj_delete = os.environ.get("API_OBJ_DELETE")

        self.event_handler_data = os.environ.get("EVENT_HANDLER_DATA")
        self.event_handler_rule = os.environ.get("EVENT_HANDLER_RULE")

        self.ui_new_controller_received = os.environ.get("UI_NEW_CONTROLLER_RECEIVED")
        self.ui_ctrl_data = os.environ.get("UI_CONTROLLER_DATA")
        self.ui_ctrl_logs = os.environ.get("UI_CONTROLLER_LOGS")

        self.com_user = os.environ.get("COM_MQTT_USER")
        self.com_pwd = os.environ.get("COM_MQTT_PASSWORD")

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))

        self.kill = False
        self.ctrl_clients_refs = []

        self.connect = False
        self.listener = listener
        self.logger = self.__reg_logger()

    def __reg_logger(self):
        # create logger
        logger = logging.getLogger("simple_example")
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create handler to write error logs in file
        os.makedirs(os.path.dirname('./logs/communication_service.log'), exist_ok=True)
        log_reg = logging.FileHandler('./logs/communication_service.log', mode="w", encoding=None, delay=False)
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
            self.mqttc.subscribe(self.new_controller_receive)
            self.mqttc.message_callback_add(self.new_controller_receive,
                                            self.on_message_from_new_controller_receive)
            while True:
                try:
                    av_controllers_responce = LocalServerRequests().get_all_registered_controllers()
                except Exception as e:
                    self.logger.info("\n[!][!] [Request error] [Retraing after 1s]\nerr: {}\n".format(e))
                    continue

                if av_controllers_responce.status_code == 200:
                    av_controllers = json.loads(av_controllers_responce.content)
                    break
                else:
                    sleep(1)
                    self.logger.info("\n[!][!] [Request error] [Retraing after 1s]\n")

            for controller_data in av_controllers:
                client_id = controller_data["mac_addr"]
                self.__bootstrap_mqtt_controller_client(client_id)
                websocket_cli = self.__bootstrap_mqtt_over_websocket_ctrl_cli("w" + client_id)
                """ send message with new controller data to UI mqtt client """
                self._mqttPubMsg(websocket_cli, self.ui_new_controller_received, json.dumps(controller_data))
        self.logger.debug("\n{0}\n".format(rc))

    def __on_connect_controller_client(self, client, userdata, flags, rc):
        if self.listener:
            """ client_id is MAC address of controller/sensor """
            client_id = client._client_id.decode()

            """ Create the required subscribers """
            client.subscribe(self.controller_configs_receive + "/" + client_id)
            client.subscribe(self.controller_rules_receive + "/" + client_id)
            client.subscribe(self.api_config_update + "/" + client_id)
            client.subscribe(self.api_obj_delete + "/" + client_id)
            client.subscribe(self.event_handler_rule + "/" + client_id)
            client.subscribe(self.controller_logs_receive + "/" + client_id)
            client.subscribe(self.controller_data_receive + "/" + client_id)

            client.message_callback_add(self.controller_configs_receive + "/" + client_id,
                                        self.on_message_from_controller_configs_receive)
            client.message_callback_add(self.controller_rules_receive + "/" + client_id,
                                        self.on_message_from_controller_rules_receive)
            client.message_callback_add(self.api_config_update + "/" + client_id,
                                        self.on_message_from_api_config_update)
            client.message_callback_add(self.api_obj_delete + "/" + client_id,
                                        self.on_message_from_api_obj_delete)
            client.message_callback_add(self.event_handler_rule + "/" + client_id,
                                        self.on_message_from_event_handler_rule)
            client.message_callback_add(self.controller_data_receive + "/" + client_id,
                                        self.on_message_from_controller_data_receive)
            client.message_callback_add(self.controller_logs_receive + "/" + client_id,
                                        self.on_message_from_controller_logs_receive)
        self.logger.debug("\n{0}\n".format(rc))

    def __on_connect_ctrl_cli_for_web(self, client, userdata, flags, rc):
        if self.listener:
            """ client_id is MAC address of controller/sensor """
            client_id = client._client_id.decode()

            """ Create the required subscribers """
            client.subscribe(self.controller_logs_receive + "/" + client_id[1:])
            client.subscribe(self.controller_data_receive + "/" + client_id[1:])
            client.subscribe(self.api_obj_delete + "/" + client_id[1:])

            client.message_callback_add(self.controller_logs_receive + "/" + client_id[1:],
                                        self.on_message_ctrl_log_websocket_cli)
            client.message_callback_add(self.controller_data_receive + "/" + client_id[1:],
                                        self.on_message_ctrl_data_websocket_cli)
            client.message_callback_add(self.api_obj_delete + "/" + client_id[1:],
                                        self.on_message_obj_del_websocket_cli)
        self.logger.debug("\n{0}\n".format(rc))

    """                              CALLBACKS                               """
    # CONTROLLER CONNECTION CALLBACKS
    def on_message(self, client, userdata, msg):
        self.logger.info("\n[???] [{0}], [{1}] - [{2}]\n".format(client._client_id, msg.topic, msg.payload))

    def on_message_from_new_controller_receive(self, client, userdata, msg):
        """ Function handling new controller registration
                - create mqtt client for new controller
                - create controller object in API
        """
        macAddr = msg.payload.decode()
        try:
            post_data = {}
            post_data["name"] = ""
            post_data["description"] = ""
            post_data["mac_addr"] = macAddr
            post_data["configuration"] = {}
            new_controller = LocalServerRequests(data=post_data).post_new_controller()

            if new_controller.status_code == 201:
                self.__bootstrap_mqtt_controller_client(macAddr)
                websocket_cli = self.__bootstrap_mqtt_over_websocket_ctrl_cli("w" + macAddr)
                """ send message with new controller data to UI mqtt client """
                self._mqttPubMsg(websocket_cli, self.ui_new_controller_received, new_controller.content)

        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [NEW_CONTROLLER_CONFIG] "
                                  "Fail to create new controller\nerr: {}\n").format(e))

    def on_message_from_api_config_update(self, client, userdata, msg):
        """ Function handling message from API for updated configs
                - publish new configs
        """
        client_id = client._client_id.decode()
        data = json.loads(msg.payload.decode())

        try:
            self._mqttPubMsg(client,
                             self.controller_configs_send + "/" + client_id,
                             json.dumps({"configs": data}))
        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [API_CONFIG_UPDATE][receive] "
                                  "Fail send new config to Controller.\nerr: {}\n").format(e))

    def on_message_from_api_obj_delete(self, client, userdata, msg):
        """ Function handling API message for deleted object
                - disconnect all clients and subscribers related with object
        """
        client_id = client._client_id.decode()
        try:
            sub_topics = [self.controller_configs_receive, self.controller_rules_receive,
                          self.api_config_update, self.api_obj_delete, self.event_handler_rule]
            for topic in sub_topics:
                client.unsubscribe(topic + "/" + client_id)

            """ Disconnect controller client and remove from client references list """
            if client in self.ctrl_clients_refs:
                self.ctrl_clients_refs.remove(client)
            client.disconnect()
            client.loop_stop()
        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [DELETE CONTROLLER] "
                                  "Fail to disconnect client and subscribers.\nerr: {}\n").format(e))

    def on_message_from_controller_configs_receive(self, client, userdata, msg):
        message = msg.payload.decode()
        pass
        # TODO: check what kind of message will come

    def on_message_from_controller_rules_receive(self, client, userdata, msg):
        message = msg.payload.decode()
        pass
        # TODO: check what kind of message will come

    def on_message_from_controller_data_receive(self, client, userdata, msg):
        try:
            msg.payload
            equipped_msg = msg.payload.decode() + " [COMMUNICATION_SERVICE] " + client._client_id.decode()
            self._mqttPubMsg(client, self.event_handler_data, equipped_msg)
        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [CONTROLLER_DATA_receive][PUB] "
                                 "Fail send data to event_handler.\nerr: {}\n").format(e))

    def on_message_from_controller_logs_receive(self, client, userdata, msg):
        self.logger.warning("\n[!][*] [{0}] [CONTROLLER LOG] [{1}]".format(client._client_id.decode(), msg.payload.decode()))

    # EVENT HANDLER CONNECTION CALLBACKS
    def on_message_from_event_handler_rule(self, client, userdata, msg):
        try:
            equipped_topic = self.controller_rules_send + "/" + client._client_id.decode()
            equipped_msg = msg.payload.decode() + " [COMMUNICATION_SERVICE]" + " " + client._client_id.decode()
            self._mqttPubMsg(client, equipped_topic, equipped_msg)
        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [EVENT_HANDLER_RULE][PUB] "
                                  "Fail send new rule to Controller.\nerr: {}\n").format(e))

    # WEBSOCKET CLIENT CALLBACKS
    def on_message_ctrl_data_websocket_cli(self, client, userdata, msg):
        try:
            self._mqttPubMsg(client, self.ui_ctrl_data, msg.payload.decode())
        except Exception as e:
            self.logger.critical(("Fail send new data to UI.\nerr: {}\n").format(e))

    def on_message_ctrl_log_websocket_cli(self, client, userdata, msg):
        try:
            self._mqttPubMsg(client, self.ui_ctrl_logs + client._client_id.decode()[1:], msg.payload.decode())
        except Exception as e:
            self.logger.critical(("Fail send new log to UI.\nerr: {}\n").format(e))

    def on_message_obj_del_websocket_cli(self, client, userdata, msg):
        """ Function handling API message for deleted object
                - disconnect all websocket clients and subscribers
        """
        client_id = client._client_id.decode()
        try:

            sub_topics = [self.controller_logs_receive, self.controller_data_receive,
                          self.api_obj_delete]
            for topic in sub_topics:
                client.unsubscribe(topic + "/" + client_id[1:])

            """ Disconnect controller client and remove from client references list"""
            if client in self.ctrl_clients_refs:
                self.ctrl_clients_refs.remove(client)
            client.disconnect()
            client.loop_stop()

        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [DELETE CONTROLLER] "
                                  "Fail to disconnect client and subscribers.\nerr: {}\n").format(e))

    """                                UTILS                                 """
    def __on_log(self, client, userdata, level, buf):
        self.logger.info("\n[*] [{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

    def _broker_auth(self, client):
        client.username_pw_set(username=self.com_user, password=self.com_pwd)

    def on_disconnect(self, client, userdata, rc=0):
        self.logger.info("\n[*] [DISCONNECT] [{0}]\n".format(client._client_id.decode()))

    """                            CLIENT CONFIGS                            """
    def __bootstrap_mqtt_controller_client(self, client_id):
        mqtt_controller_cli = paho.Client(client_id=client_id, clean_session=False, protocol=paho.MQTTv311)
        self._broker_auth(mqtt_controller_cli)
        mqtt_controller_cli.on_connect = self.__on_connect_controller_client
        mqtt_controller_cli.on_message = self.on_message
        mqtt_controller_cli.on_log = self.__on_log
        mqtt_controller_cli.on_disconnect = self.on_disconnect
        result_of_connection = mqtt_controller_cli.connect(self.broker_url, self.broker_port, keepalive=120)
        self.ctrl_clients_refs.append(mqtt_controller_cli)
        if result_of_connection == 0:
            mqtt_controller_cli.loop_start()
        return mqtt_controller_cli

    def __bootstrap_mqtt_over_websocket_ctrl_cli(self, client_id):
        mqtt_controller_cli = paho.Client(client_id=client_id, clean_session=False,
                                          protocol=paho.MQTTv311, transport='websockets')
        self._broker_auth(mqtt_controller_cli)
        mqtt_controller_cli.on_connect = self.__on_connect_ctrl_cli_for_web
        mqtt_controller_cli.on_message = self.on_message
        mqtt_controller_cli.on_log = self.__on_log
        mqtt_controller_cli.on_disconnect = self.on_disconnect
        result_of_connection = mqtt_controller_cli.connect(self.broker_url, 9001, keepalive=120)
        self.ctrl_clients_refs.append(mqtt_controller_cli)
        if result_of_connection == 0:
            mqtt_controller_cli.loop_start()
        return mqtt_controller_cli

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client(self.communicaton_service_client_id, protocol=paho.MQTTv311)
        self._broker_auth(self.mqttc)
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_log = self.__on_log
        self.mqttc.on_disconnect = self.on_disconnect

        result_of_connection = self.mqttc.connect(self.broker_url, self.broker_port)
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
        else:
            for client in self.ctrl_clients_refs:
                client.loop_stop()

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
