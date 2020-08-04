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
                ctrl_client = self.__bootstrap_mqtt_controller_client(client_id)
                if "sensors" in controller_data["pins_configuration"]:
                    sensors = controller_data["pins_configuration"]["sensors"]
                    try:
                        """ Connected new config subscribers """
                        for sensor in sensors:
                            log_sub = self.controller_logs_receive + "/" + client_id + "/" + sensor["id"]
                            data_sub = self.controller_data_receive + "/" + client_id + "/" + sensor["id"]

                            ctrl_client.subscribe(data_sub)
                            ctrl_client.subscribe(log_sub)

                            ctrl_client.message_callback_add(data_sub,
                                                             self.on_message_from_controller_data_receive)
                            ctrl_client.message_callback_add(log_sub,
                                                             self.on_message_from_controller_logs_receive)
                    except Exception as e:
                        self.logger.critical(("\n[!][!] [--] [START LOADS FAIL]"
                                              "Fail to connect / disconnect subscriber.\nerr: {}\n").format(e))
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
        self.logger.debug("\n{0}\n".format(rc))

    """                              CALLBACKS                               """
    """ All function names are created from two parts:
            'on_message_from' - show action type,
            second part - show name of topic variable """
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
            post_data["pins_configuration"] = {}
            new_controller = LocalServerRequests(data=post_data).post_new_controller()
        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [NEW_CONTROLLER_CONFIG] "
                                  "Fail create new controller on API.\nerr: {}\n").format(e))

        if new_controller.status_code == 201:
            """ send message to UI mqtt client with data of new controller """
            self._mqttPubMsg(client, self.ui_new_controller_received, new_controller.content)
            self.__bootstrap_mqtt_controller_client(macAddr)
        else:
            self.logger.warning(("\n[!][!] [--] [NEW_CONTROLLER_CONFIG] "
                                 "Fail to create new client for controller. "
                                 "API status: {}\n").format(new_controller.status_code))

    def on_message_from_api_config_update(self, client, userdata, msg):
        """ Function handling message from API for updated configs
                - create new subscribers and kill old
                - update controller object's subscribers topics in API (put req)
                - publish new configs
        """
        client_id = client._client_id.decode()
        data = json.loads(msg.payload.decode())
        existed_subscribers = data["subscribers"]
        sensors = data["pins_configuration"]["sensors"]
        new_subscribers = []

        try:
            if existed_subscribers:
                """ Disconnect old subscribers """
                for sub in existed_subscribers:
                    client.unsubscribe(sub)

            """ Connected new config subscribers """
            for sensor in sensors:
                log_sub = self.controller_logs_receive + "/" + client_id + "/" + sensor["id"]
                data_sub = self.controller_data_receive + "/" + client_id + "/" + sensor["id"]
                new_subscribers.append(log_sub)
                new_subscribers.append(data_sub)

                client.subscribe(data_sub)
                client.subscribe(log_sub)

                client.message_callback_add(data_sub,
                                            self.on_message_from_controller_data_receive)
                client.message_callback_add(log_sub,
                                            self.on_message_from_controller_logs_receive)
        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [API_CONFIG_UPDATE] "
                                  "Fail to connect / disconnect subscriber.\nerr: {}\n").format(e))

        while True:
            try:
                """ Update subscribers in db """
                update_subscribers = LocalServerRequests(mac_addr=client_id,
                                                         data={"subscribers": new_subscribers}).put_subscribers_by_mac()
            except Exception as e:
                self.logger.info("\n[!][!] [Request error] [Retraing after 1s]\nerr: {}\n".format(e))
                continue

            if update_subscribers.status_code == 200:
                """ send new configs to controller """
                try:
                    self._mqttPubMsg(client,
                                     self.controller_configs_send + "/" + client_id,
                                     json.dumps({"configs": data}))
                except Exception as e:
                    self.logger.critical(("\n[!][!] [--] [API_CONFIG_UPDATE][receive] "
                                          "Fail send new config to Controller.\nerr: {}\n").format(e))
                break
            else:
                sleep(1)

    def on_message_from_api_obj_delete(self, client, userdata, msg):
        """ Function handling message from API for updated configs
                - disconnect all client subscribers
                - disconnect client
        """
        client_id = client._client_id.decode()
        data = json.loads(msg.payload.decode())
        existed_subscribers = data["subscribers"]
        try:
            if existed_subscribers:
                """ Disconnect old subscribers """
                for sub in existed_subscribers:
                    client.unsubscribe(sub)
        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [API_OBJ_DELTE] "
                                  "Fail to  disconnect subscriber.\nerr: {}\n").format(e))

        try:
            self._mqttPubMsg(client,
                             self.controller_configs_send + "/" + client_id,
                             json.dumps({"configs": data}))
            """ Disconnect all subscribers on this client """
            if existed_subscribers:
                for sub in existed_subscribers:
                    client.unsubscribe(sub)
            client.unsubscribe(self.controller_configs_receive + "/" + client_id)
            client.unsubscribe(self.controller_rules_receive + "/" + client_id)
            client.unsubscribe(self.api_config_update + "/" + client_id)
            client.unsubscribe(self.api_obj_delete + "/" + client_id)
            client.unsubscribe(self.event_handler_rule + "/" + client_id)

            """ Disconnect controller client and remove from client references list"""
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
        message = msg.payload.decode() + " [COMMUNICATION_SERVICE]"
        try:
            equipped_topic = self.controller_rules_send + "/" + client._client_id.decode()
            equipped_msg = msg.payload.decode() + " [COMMUNICATION_SERVICE]" + " " + client._client_id.decode()
            self._mqttPubMsg(client, equipped_topic, equipped_msg)
        except Exception as e:
            self.logger.critical(("\n[!][!] [--] [EVENT_HANDLER_RULE][PUB] "
                                  "Fail send new rule to Controller.\nerr: {}\n").format(e))

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
