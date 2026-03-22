#!/bin/sh
# Runs inside the Mosquitto container: ensures users from setup-users.env exist in pwfile.
# Default credentials: /mosquitto/config/setup-users.env (override with MOSQUITTO_SETUP_USERS_ENV).

set -e
PWFILE="${MOSQUITTO_PWFILE:-/mosquitto/config/pwfile}"
CREDS="${MOSQUITTO_SETUP_USERS_ENV:-/mosquitto/config/setup-users.env}"

if [ ! -f "$CREDS" ]; then
  echo "setup-mqtt-users-inner: no credentials file at $CREDS, skipping" >&2
  exit 0
fi

touch "$PWFILE"
chown root:mosquitto "$PWFILE"
chmod 640 "$PWFILE"

added=0
skipped=0
while IFS= read -r raw || [ -n "$raw" ]; do
  line=$(printf '%s' "$raw" | tr -d '\r')
  case "$line" in
  '' | \#*) continue ;;
  esac
  case "$line" in
  *=*) ;;
  *)
    echo "Skipping line (expected username=password): $line" >&2
    continue
    ;;
  esac
  user=${line%%=*}
  pass=${line#*=}
  if [ -z "$user" ]; then
    echo "Invalid line (empty username): $line" >&2
    exit 1
  fi

  if awk -F: -v u="$user" '$1 == u { f = 1 } END { exit(f ? 0 : 1) }' "$PWFILE" 2>/dev/null; then
    echo "skip: user already exists: $user"
    skipped=$((skipped + 1))
    continue
  fi

  mosquitto_passwd -b "$PWFILE" "$user" "$pass"
  echo "added: $user"
  added=$((added + 1))
done <"$CREDS"

chown root:mosquitto "$PWFILE"
chmod 640 "$PWFILE"

echo "Done. added=$added skipped=$skipped"
