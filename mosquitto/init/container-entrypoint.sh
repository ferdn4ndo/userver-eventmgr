#!/bin/sh
# Runs user setup (if credentials file is present), then the image entrypoint + mosquitto.

set -e
PWFILE=/mosquitto/config/pwfile
if [ -f /mosquitto/config/setup-users.env ]; then
  /mosquitto/init/setup-mqtt-users-inner.sh
elif [ ! -f "$PWFILE" ] || [ ! -s "$PWFILE" ]; then
  MOSQUITTO_USERNAME=${MOSQUITTO_USERNAME:-mqtt}
  MOSQUITTO_PASSWORD=${MOSQUITTO_PASSWORD:-password}
  mosquitto_passwd -c -b "$PWFILE" "$MOSQUITTO_USERNAME" "$MOSQUITTO_PASSWORD"
  chown root:mosquitto "$PWFILE"
  chmod 640 "$PWFILE"
fi
exec /docker-entrypoint.sh "$@"
