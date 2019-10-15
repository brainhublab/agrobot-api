from mqtt_services.mqtt_query_subscriber import MqttClientSub

mqttRawDataSub = MqttClientSub
mqttRawDataSub(listener=True).bootstrap_mqtt().start()

