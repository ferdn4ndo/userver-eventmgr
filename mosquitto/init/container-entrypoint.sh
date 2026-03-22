#!/bin/sh
# Runs user setup (if credentials file is present), then the image entrypoint + mosquitto.

set -e
if [ -f /mosquitto/config/setup-users.env ]; then
  /mosquitto/init/setup-mqtt-users-inner.sh
fi
exec /docker-entrypoint.sh "$@"
