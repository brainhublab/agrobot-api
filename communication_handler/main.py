import os
# from mqtt_services.mqtt_query_publisher import MqttClientPub
# import sys
# from os.path import dirname, abspath
# sys.path.insert(0, abspath(dirname(__file__)))

from mqtt_services.mqtt_query_subscriber import MqttClientSub


BROKER_HOST = os.environ.get("BROKER_HOST")
print(BROKER_HOST)
BROKER_PORT = int(os.environ.get("BROKER_PORT"))
RAW_DATA_MQTT_TOPIC = os.environ.get("RAW_DATA_MQTT_TOPIC")
HANDLER_DATA_MQTT_TOPIC = os.environ.get("HANDLER_DATA_MQTT_TOPIC")


mqttRawDataSub = MqttClientSub
mqttRawDataSub(listener=True,
               topic=RAW_DATA_MQTT_TOPIC,
               broker_url=BROKER_HOST,
               broker_port=BROKER_PORT).bootstrap_mqtt().start()

print("ok")

