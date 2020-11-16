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
from .mqtt_web_ctrls_client import MqttCtrlWebClient

ctrl_cli = MqttCtrlClient
web_cli = MqttCtrlWebClient


class MqttMasterClient(object):
    def __init__(self, listener=False):
        """ take the basic topic names from envoirnment file"""
        self.mqtt_master_cli_id = os.environ.get("MQTT_MASTER_CLI_ID")
        self.ctrl_auth = os.environ.get("CTRL_AUTH")
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

    # ***                            SUBSCRIBERS                             ***
    def on_connect(self, client, userdata, flags, rc):
        self.connect = True
        if self.listener:
            self.mqttc.subscribe(self.ctrl_auth)
            self.mqttc.message_callback_add(self.ctrl_auth,
                                            self.on_message_from_ctrl_auth)

            self.web_client = web_cli(self.logger).bootstrap()
            self.ctrl_clients_refs.append(self.web_client)

            av_controllers = self.get_av_ctrl()
            for controller_data in av_controllers:
                client_id = controller_data["macAddr"]
                ctrl_client = ctrl_cli(self.ctrl_clients_refs, self.logger).bootstrap(client_id)
                self.ctrl_clients_refs.append(ctrl_client)

                # send message with new controller data to UI mqtt client
                self._mqttPubMsg(self.web_client, "ui/" + self.ctrl_auth, json.dumps({"ima": "ima"}))

    # ***                              CALLBACKS                               ***
    def on_message(self, client, userdata, msg):
        self.logger.info("\n[???] [{0}], [{1}] - [{2}]\n".format(client._client_id, msg.topic, msg.payload))

    def on_message_from_ctrl_auth(self, client, userdata, msg):
        """ Function handling new controller registration
                - create mqtt ctrl client
                - create mqtt ctrl client over websocket (UI purpose)
                - create controller object in API
        """
        ctrl_data = json.loads(msg.payload.decode())
        client_id = ctrl_data["mac_addr"]
        mcu_type = ctrl_data["mcu_type"]
        title = ctrl_data["title"]

        post_data = {"mcuType": mcu_type,
                     "title": title,
                     "macAddr": client_id}

        new_controller = LocalServerRequests(data=post_data).post_new_controller()
        if new_controller.status_code == 201:
            n_ctrl_cli = ctrl_cli(self.ctrl_clients_refs, self.logger).bootstrap(client_id)
            self.ctrl_clients_refs.append(n_ctrl_cli)

            # send message with new controller data to UI mqtt client
            self._mqttPubMsg(self.web_client, "ui/" + msg.topic, json.dumps({"ima": "ima"}))
        elif new_controller.status_code == 409:
            # in case controller exist in DB
            # this function will exec get request witch will trigger
            # api to send configs to controller via mqtt
            LocalServerRequests(mac_addr=client_id).send_conf_trigger()
        else:
            self.logger.warning("\n[!][*] [{0}] [Api] [{1}]".format(client._client_id.decode(),
                                                                    new_controller.status_code == 201))
    # ***                                UTILS                                 ***

    def on_log(self, client, userdata, level, buf):
        self.logger.info("\n[*] [{0}] [{1}] [{2}]\n".format(client._client_id.decode(), level, buf))

    def _broker_auth(self, client):
        client.username_pw_set(username=self.com_user, password=self.com_pwd)

    def on_disconnect(self, client, userdata, rc=0):
        self.logger.info("\n[*] [DISCONNECT] [{0}]\n".format(client._client_id.decode()))

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client(self.mqtt_master_cli_id, protocol=paho.MQTTv311)
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
