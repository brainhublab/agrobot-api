#!/bin/ash

set -e

if ( [ -z "${CONTROLLER_MQTT_USER}" ] || [ -z "${CONTROLLER_MQTT_PASSWORD}" ] || [ -z "${COM_MQTT_USER}" ] || [ -z "${COM_MQTT_PASSWORD}" ] || [ -z "${EH_MQTT_USER}" ] || [ -z "${EH_MQTT_PASSWORD}" ] ); then
  echo "Missing user(s) or password(s) not defined"
  exit 1
fi

# create mosquitto passwordfile
touch passwordfile
mosquitto_passwd -b passwordfile $CONTROLLER_MQTT_USER $CONTROLLER_MQTT_PASSWORD
echo "=======>> CONTROLLER_MQTT_USER CONTROLLER_MQTT_PASSWORD defined"
mosquitto_passwd -b passwordfile $COM_MQTT_USER $COM_MQTT_PASSWORD
echo "=======>> COM_MQTT_USER COM_MQTT_PASSWORD defined"
mosquitto_passwd -b passwordfile $EH_MQTT_USER $EH_MQTT_PASSWORD
echo "=======>> EH_MQTT_USER EH_MQTT_PASSWORD defined"

exec "$@"

