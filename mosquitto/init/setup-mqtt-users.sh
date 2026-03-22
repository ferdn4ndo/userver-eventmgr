#!/usr/bin/env bash
# Ensures MQTT users from setup-users.env exist in the pwfile (via in-container script).
#
# Usage: ./setup-mqtt-users.sh
# Credentials: mosquitto/config/setup-users.env (path inside the container: /mosquitto/config/setup-users.env)

set -euo pipefail

CONTAINER="${MOSQUITTO_CONTAINER:-userver-mosquitto}"

if ! docker inspect "$CONTAINER" &>/dev/null; then
  echo "Docker container not found: $CONTAINER" >&2
  exit 1
fi

docker exec "$CONTAINER" /mosquitto/init/setup-mqtt-users-inner.sh
