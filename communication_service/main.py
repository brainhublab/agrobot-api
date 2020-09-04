from mqtt_services.mqtt_master_client import MqttMasterClient

mqttMaster = MqttMasterClient
mqttMaster(listener=True).bootstrap_mqtt().start()
