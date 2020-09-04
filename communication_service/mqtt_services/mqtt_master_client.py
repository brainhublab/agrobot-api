import paho.mqtt.client as paho
import signal
import os
from time import sleep
import json
import sys
sys.path.insert(0, os.path.abspath('..'))
from http_requests.requestss import LocalServerRequests
from .logger import reg_logger
from .mqtt_ctrls_client import MqttCtrlClient
from .mqtt_data_manager import MqttDataManager
from .mqtt_web_ctrls_client import MqttCtrlWebClient

ctrl_cli = MqttCtrlClient
web_cli = MqttCtrlWebClient
data_mngr = MqttDataManager


class MqttMasterClient(object):
    def __init__(self, listener=False):
        """ take the basic topic names from envoirnment file"""
        self.communicaton_service_client_id = os.environ.get("COMMUNICATION_SERVICE_CLIENT_ID")
        self.new_ctrl_receive = os.environ.get("RECEIVE_NEW_CONTROLLER")
        self.ui_new_ctlr_received = os.environ.get("UI_NEW_CONTROLLER_RECEIVED")
        self.api_obj_delete = os.environ.get("API_OBJ_DELETE")

        self.com_user = os.environ.get("COM_MQTT_USER")
        self.com_pwd = os.environ.get("COM_MQTT_PASSWORD")

        self.broker_url = os.environ.get("BROKER_HOST")
        self.broker_port = int(os.environ.get("BROKER_PORT"))

        self.connect = False
        self.kill = False
        self.listener = listener
        self.logger = reg_logger()
        self.ctrl_clients_refs = []

    def get_av_ctrl(self):
        responce = LocalServerRequests().get_all_registered_controllers()
        if responce.status_code == 200:
            return json.loads(responce.content)
        else:
            self.logger.info("\n[!][!] [Request error] [Retraing after 1s]\n")
            sleep(1)
            self.get_av_ctrl()

    """     SUBSCRIBERS / CALLBACKS CONNECTIONS AND CLIENTS REGISTRY (every reconnection)    """
    def on_connect(self, client, userdata, flags, rc):
        self.connect = True
        if self.listener:
            self.mqttc.subscribe(self.new_ctrl_receive)
            self.mqttc.message_callback_add(self.new_ctrl_receive,
                                            self.on_message_from_new_ctrl_receive)

            self.web_client = web_cli(self.logger).bootstrap()
            self.data_manager = data_mngr(self.logger).bootstrap()

            self.ctrl_clients_refs.append(self.web_client)
            self.ctrl_clients_refs.append(self.data_manager)

            av_controllers = self.get_av_ctrl()
            for controller_data in av_controllers:
                client_id = controller_data["mac_addr"]
                ctrl_client = ctrl_cli(self.ctrl_clients_refs, self.logger).bootstrap(client_id)
                self.ctrl_clients_refs.append(ctrl_client)

                """ send message with new controller data to UI mqtt client """
                self._mqttPubMsg(self.web_client, self.ui_new_ctlr_received, json.dumps({"ima": "ima"}))

    """                              CALLBACKS                               """
    # CONTROLLER CONNECTION CALLBACKS
    def on_message(self, client, userdata, msg):
        self.logger.info("\n[???] [{0}], [{1}] - [{2}]\n".format(client._client_id, msg.topic, msg.payload))

    def on_message_from_new_ctrl_receive(self, client, userdata, msg):
        """ Function handling new controller registration
                - create mqtt ctrl client
                - create mqtt ctrl client over websocket (UI purpose)
                - create controller object in API
        """
        client_id = msg.payload.decode()
        post_data = {}
        post_data["name"] = ""
        post_data["description"] = ""
        post_data["mac_addr"] = client_id
        post_data["graph"] = {}
        post_data["esp_config"] = {}
        new_controller = LocalServerRequests(data=post_data).post_new_controller()

        if new_controller.status_code == 201:
            n_ctrl_cli = ctrl_cli(self.ctrl_clients_refs, self.logger).bootstrap(client_id)
            self.ctrl_clients_refs.append(n_ctrl_cli)

            """ send message with new controller data to UI mqtt client """
            self._mqttPubMsg(self.web_client, self.ui_new_ctlr_received, json.dumps({"ima": "ima"}))
        else:
            self.logger.warning("\n[!][*] [{0}] [Api] [{1}]".format(client._client_id.decode(),
                                                                    new_controller.status_code == 201))
    """                                UTILS                                 """
    def on_log(self, client, userdata, level, buf):
        self.logger.info("\n[*] [{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

    def _broker_auth(self, client):
        client.username_pw_set(username=self.com_user, password=self.com_pwd)

    def on_disconnect(self, client, userdata, rc=0):
        self.logger.info("\n[*] [DISCONNECT] [{0}]\n".format(client._client_id.decode()))

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client(self.communicaton_service_client_id, protocol=paho.MQTTv311)
        self._broker_auth(self.mqttc)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_log = self.on_log
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
            for cli in self.ctrl_clients_refs:
                cli.disconnect()
                cli.loop_stop()
            self.mqttc.disconnect()
            self.mqttc.loop_stop()

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
