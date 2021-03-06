#!/bin/ash

set -e

if ( [ -z "${CONTROLLER_MQTT_USER}" ] || [ -z "${CONTROLLER_MQTT_PASSWORD}" ] ); then
  echo "Missing Controller user or password not defined"
  exit 1
fi
if ( [ -z "${COM_MQTT_USER}" ] || [ -z "${COM_MQTT_PASSWORD}" ] ); then
  echo "Missing Communication service user or password not defined"
  exit 1
fi
if ( [ -z "${API_MQTT_USER}" ] || [ -z "${API_MQTT_PASSWORD}" ] ); then
  echo "Missing API user or password not defined"
  exit 1
fi
if ( [ -z "${UI_MQTT_USER}" ] || [ -z "${UI_MQTT_PASSWORD}" ] ); then
  echo "Missing UI user or password not defined"
  exit 1
fi

# create mosquitto passwordfile
touch passwordfile
mosquitto_passwd -b passwordfile $CONTROLLER_MQTT_USER $CONTROLLER_MQTT_PASSWORD
echo "=======>> CONTROLLER_MQTT_USER CONTROLLER_MQTT_PASSWORD defined"
mosquitto_passwd -b passwordfile $COM_MQTT_USER $COM_MQTT_PASSWORD
echo "=======>> COM_MQTT_USER COM_MQTT_PASSWORD defined"
mosquitto_passwd -b passwordfile $API_MQTT_USER $API_MQTT_PASSWORD
echo "=======>> API_MQTT_USER API_MQTT_PASSWORD defined"
mosquitto_passwd -b passwordfile $UI_MQTT_USER $UI_MQTT_PASSWORD
echo "=======>> UI_MQTT_USER UI_MQTT_PASSWORD defined"

exec "$@"
