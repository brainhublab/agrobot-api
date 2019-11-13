import paho.mqtt.client as paho
import os
from time import sleep
import json
import sys
import logging
sys.path.insert(0, os.path.abspath('..'))
from http_requests.requestss import LocalServerRequests
from en_de_crypter.en_de_crypter import EnDeCrypt


class MqttClientSub(object):
    def __init__(self, listener=False):
        """ take the basic topic names from envoirnment file"""
        self.new_controller_receave = os.environ.get("CONTROLLER_RECEAVE_NEW_CONTROLLER")

        self.controller_configs_receave = os.environ.get("CONTROLLER_CONFIGS") + "/receave"
        self.controller_configs_sent = os.environ.get("CONTROLLER_CONFIGS") + "/sent"

        self.controller_data_receave = os.environ.get("CONTROLLER_DATA")
        self.controller_logs_receave = os.environ.get("CONTROLLER_LOGS")

        self.controller_rules_receave = os.environ.get("CONTROLLER_RULES") + "/receave"
        self.controller_rules_sent = os.environ.get("CONTROLLER_RULES") + "/sent"

        self.api_config_upgrade = os.environ.get("API_CONFIG_UPDATE")

        self.sub_from_event_handler_topic = os.environ.get("EVENT_HANDLER_INSTRUCTION_TO_COM_SERVICE")
        self.pub_to_event_handler_topic = os.environ.get("COM_SERVICE_RAW_DATA_TO_EVENT_HANDLER")

        self.eh_user = os.environ.get("COM_MQTT_USER")
        self.eh_pwd = os.environ.get("COM_MQTT_PASSWORD")
        self.en_de_key = os.environ.get("CRYPTOGRAPHY_KEY")
        self.ctrl_clients_refs = []

        self.connect = False
        self.listener = listener
        self.auth_token = os.environ.get("TOKEN")

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))
        self.logger = self.__reg_logger()

    def __reg_logger(self):
        # create logger
        logger = logging.getLogger(repr(self))
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create handler to write error logs in file
        error_handler = logging.FileHandler('./logs/error_file.log')
        error_handler.setLevel(logging.ERROR)

        # create  handler to write warning logs in file
        warning_handler = logging.FileHandler('./logs/warning_file.log')
        warning_handler.setLevel(logging.WARNING)

        # create  handler to write critical logs in file
        critical_handler = logging.FileHandler('./logs/critical_file.log')
        critical_handler.setLevel(logging.CRITICAL)

        # create formatter for logger output
        formatter = logging.Formatter('\n[%(levelname)s] - %(asctime)s - %(name)s - %(message)s')

        # add formatter to handlers
        ch.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        warning_handler.setFormatter(formatter)
        critical_handler.setFormatter(formatter)

        # add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(error_handler)
        logger.addHandler(warning_handler)
        logger.addHandler(critical_handler)

        return logger

    """     SUBSCRIBERS / CALLBACKS CONNECTION REGISTRY (every reconnection)    """

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True
        if self.listener:
            self.mqttc.subscribe(self.new_controller_receave)
            self.mqttc.subscribe(self.sub_from_event_handler_topic)

            self.mqttc.message_callback_add(self.new_controller_receave,
                                            self.on_message_from_new_controller_receave)
            self.mqttc.message_callback_add(self.sub_from_event_handler_topic,
                                            self.on_message_from_handler)
            av_controllers = LocalServerRequests().get_all_registered_controllers()
            for controller_data in av_controllers:
                client_id = controller_data["mac_addr"]
                ctrl_client = self.__bootstrap_mqtt_controller_client(client_id)
                self.ctrl_clients_refs.append(ctrl_client)
                if "sensors" in controller_data["pins_configuration"]:
                    sensors = controller_data["pins_configuration"]["sensors"]
                    try:
                        """ Connected new config subscribers """
                        for sensor in sensors:
                            log_sub = self.controller_logs_receave + "/" + client_id + "/" + sensor["id"]
                            data_sub = self.controller_data_receave + "/" + client_id + "/" + sensor["id"]

                            ctrl_client.subscribe(data_sub)
                            ctrl_client.subscribe(log_sub)

                            ctrl_client.message_callback_add(data_sub,
                                                             self.on_message_from_controller_data_receave)
                            ctrl_client.message_callback_add(log_sub,
                                                             self.on_message_from_controller_logs_receave)
                    except Exception as e:
                        self.logger.critical("\n[!][!] [--] [API_CONFIG_UPDATE][receave] \
                                             Fail to connect / disconnect subscriber.\nerr: {}\n".format(e))
                        self.logger.info("\n[!][!] [--] [API_CONFIG_UPDATE][receave] \
                                         Fail to connect / disconnect subscriber.\nerr: {}\n".format(e))
        self.logger.debug("\n{0}\n".format(rc))

    def __on_connect_controller_client(self, client, userdata, flags, rc):
        if self.listener:
            client_id = client._client_id.decode()

            """ Create tha required subscribers """
            client.subscribe(self.controller_configs_receave + "/" + client_id)
            client.subscribe(self.controller_rules_receave + "/" + client_id)
            client.subscribe(self.api_config_upgrade + "/" + client_id)

            client.message_callback_add(self.controller_configs_receave + "/" + client_id,
                                        self.on_message_from_controller_configs_receave)
            client.message_callback_add(self.controller_rules_receave + "/" + client_id,
                                        self.on_message_from_controller_rules_receave)
            client.message_callback_add(self.api_config_upgrade + "/" + client_id,
                                        self.on_message_from_api_config_upgrade)
        self.logger.debug("\n{0}\n".format(rc))

    """                              CALLBACKS                               """
    # CONTROLLER CONNECTION CALLBACKS
    def on_message(self, client, userdata, msg):
        self.logger.info("\n[???] [{0}], [{1}] - [{2}]\n".format(client._client_id, msg.topic, msg.payload))

    """ Function handling NEW CONTROLLER CONFIG
            - will create mqtt client for new controller
            - will create controller object in API
            - activate basic subscribers
    """
    def on_message_from_new_controller_receave(self, client, userdata, msg):
        print(dir(userdata))
        macAddr = msg.payload.decode()
        try:
            post_data = {}
            post_data["name"] = ""
            post_data["description"] = ""
            post_data["mac_addr"] = macAddr
            post_data["pins_configuration"] = {}
            new_controller = LocalServerRequests(data=post_data).post_new_controller()
        except Exception as e:
            self.logger.critical("\n[!][!] [--] [NEW_CONTROLLER_CONFIG] \
                                 Fail create new controller on API.\nerr: {}\n".format(e))
            self.logger.info("\n[!][!] [--] [NEW_CONTROLLER_CONFIG] \
                             Fail create new controller on API.\nerr: {}\n".format(e))

        if new_controller.status_code == 201:
            new_ctrl_client = self.__bootstrap_mqtt_controller_client(macAddr)
            self.ctrl_clients_refs.append(new_ctrl_client)

        else:
            self.logger.warning("\n[!][!] [--] [NEW_CONTROLLER_CONFIG] \
                                Fail to create new client for controller.\nstatus: {}\n".format(new_controller.status_code))
            self.logger.info("\n[!][!] [--] [NEW_CONTROLLER_CONFIG] \
                             Fail to create new client for controller.\nstatus: {}\n".format(new_controller.status_code))

    def on_message_from_api_config_upgrade(self, client, userdata, msg):
        client_id = client._client_id.decode()
        controller_data = json.loads(msg.payload.decode())
        sensors = controller_data["pins_configuration"]["sensors"]
        existed_subscribers = controller_data["subscribers"]
        new_subscribers = []

        try:
            if existed_subscribers:
                """ Disconnect old subscribers """
                for sub in existed_subscribers:
                    client.unsubscribe(sub)

            """ Connected new config subscribers """
            for sensor in sensors:
                log_sub = self.controller_logs_receave + "/" + client_id + "/" + sensor["id"]
                data_sub = self.controller_data_receave + "/" + client_id + "/" + sensor["id"]
                new_subscribers.append(log_sub)
                new_subscribers.append(data_sub)

                client.subscribe(data_sub)
                client.subscribe(log_sub)

                client.message_callback_add(data_sub,
                                            self.on_message_from_controller_data_receave)
                client.message_callback_add(log_sub,
                                            self.on_message_from_controller_logs_receave)
        except Exception as e:
            self.logger.critical("\n[!][!] [--] [API_CONFIG_UPDATE][receave] \
                                 Fail to connect / disconnect subscriber.\nerr: {}\n".format(e))
            self.logger.info("\n[!][!] [--] [API_CONFIG_UPDATE][receave] \
                             Fail to connect / disconnect subscriber.\nerr: {}\n".format(e))

        """ record new subscribers in db """
        try:
            update_subscribers = LocalServerRequests(mac_addr=client_id,
                                                     data={"subscribers": new_subscribers}).put_subscribers_by_mac()
        except Exception as e:
            self.logger.critical("\n[!][!] [--] [API_CONFIG_UPDATE][receave] \
                                 Fail put new subscribers to API.\nerr: {}\n".format(e))
            self.logger.info("\n[!][!] [--] [API_CONFIG_UPDATE][receave] \
                             Fail put new subscribers to API.\nerr: {}\n".format(e))

        if update_subscribers.status_code == 200:
            """ sent new configs to controller """
            try:
                self._mqttPubMsg(self.controller_configs_sent + "/" + client_id,
                                 json.dumps({"configs": controller_data}))
            except Exception as e:
                self.logger.critical("\n[!][!] [--] [API_CONFIG_UPDATE][receave] \
                                     Fail sent new config to Controller.\nerr: {}\n".format(e))
                self.logger.info("\n[!][!] [--] [API_CONFIG_UPDATE][receave] \
                                 Fail sent new config to Controller.\nerr: {}\n".format(e))
        # client.disconnect()
        # self.__bootstrap_mqtt_controller_client("MACcontrollerTest")

    def on_message_from_controller_configs_receave(self, client, userdata, msg):
        message = msg.payload.decode()
        pass
        # TODO: check what kind of message will come

    def on_message_from_controller_rules_receave(self, client, userdata, msg):
        message = msg.payload.decode()
        pass
        # TODO: check what kind of message will come

    def on_message_from_controller_data_receave(self, client, userdata, msg):
        print("Dataaaaaaaaaaaaa NEW")
        for client in self.ctrl_clients_refs:
            print(client._client_id.decode())
        # print(self.controllers_clients_refs)

    def on_message_from_controller_logs_receave(self, client, userdata, msg):
        print("New LOGGGGGGGGGGGGGGGGGGGGGG")

    # EVENT HANDLER CONNECTION CALLBACKS
    def on_message_from_handler(self, client, userdata, msg):
        """Just resent data from handler to controller"""
        try:
            self.logger.info("\n[*] [<--] [CS][EH] New instruction come from Handler\n")
            self._mqttPubMsg(self.pub_to_ctrl_topic, msg.payload)
            self.logger.info("\n[*] [-->] [CS][CO] New instruction sended to Controller\n")
        except Exception as e:
            self.logger.critical("\n[!][!] [--] [CS][CO] Fail send data to Controller.\nerr: {}\n".format(e))

    """                                UTILS                                 """

    def __on_log(self, client, userdata, level, buf):
        self.logger.info("\n[*][{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

    def _broker_auth(self, client):
        client.username_pw_set(username=self.eh_user, password=self.eh_pwd)

    def on_disconnect(client, userdata, rc=0):
        print("disconnect {} {}").format(client._client_id, userdata)

    """                            CLIENT CONFIGS                            """

    def __bootstrap_mqtt_controller_client(self, client_id):
        mqtt_controller_cli = paho.Client(client_id=client_id, clean_session=False)
        self._broker_auth(mqtt_controller_cli)
        mqtt_controller_cli.on_connect = self.__on_connect_controller_client
        mqtt_controller_cli.on_message = self.on_message
        mqtt_controller_cli.on_log = self.__on_log
        result_of_connection = mqtt_controller_cli.connect(self.broker_url, self.broker_port, keepalive=120)

        if result_of_connection == 0:
            mqtt_controller_cli.loop_start()
        return mqtt_controller_cli

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client("CommunicatonServiceClient")
        self._broker_auth(self.mqttc)
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_log = self.__on_log

        result_of_connection = self.mqttc.connect(self.broker_url, self.broker_port, keepalive=120)
        if result_of_connection == 0:
            self.connect = True

        return self

    def start(self):
        self.logger.info("{0}".format("\n[*] [CS] [*] Query listeners are Up!\n"))
        self.mqttc.loop_start()

        while True:
            sleep(2)
            if self.connect is True:
                pass
            else:
                self.logger.debug("\n[!] [CS] [!] Attempting to connect!\n")

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

