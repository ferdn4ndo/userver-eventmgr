#!/bin/bash

echo "Checking if userver-filemgr database exists (DB_NAME: ${POSTGRES_DB})"
PGPASSWORD=${POSTGRES_ROOT_PASS} psql -h "${POSTGRES_HOST}" -U "${POSTGRES_ROOT_USER}" -p "${POSTGRES_PORT}" <<EOF
  SELECT 'CREATE DATABASE ${POSTGRES_DB}'
  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}')\gexec

  GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO public;

  SELECT 'CREATE USER ${POSTGRES_USER}'
  WHERE NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${POSTGRES_USER}')\gexec
  ALTER USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASS}';

  REVOKE ALL PRIVILEGES ON DATABASE postgres FROM ${POSTGRES_USER};
  ALTER USER ${POSTGRES_USER} CREATEDB;
  GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};
\gexec
EOF

echo "Creating migrations"
python manage.py makemigrations

echo "Migrating..."
python manage.py migrate

echo "Adding fixtures..."
python manage.py loaddata /code/core/fixtures/mime_types.yaml

echo "Creating local test storage folder"
mkdir -p "${LOCAL_TEST_STORAGE_ROOT}"

echo "Creating auth system..."
system_resp=$(
    curl -sS -X POST "${USERVER_AUTH_HOST}/auth/system" \
        -H "Authorization: Token ${USERVER_AUTH_SYSTEM_CREATION_TOKEN}" \
        -H "Content-Type: application/json" \
        --data @- <<END
{
  "name": "${USERVER_AUTH_SYSTEM_NAME}",
  "token": "${USERVER_AUTH_SYSTEM_TOKEN}"
}
END
)
echo "System response:"
echo "${system_resp}"

echo "Creating auth user (register)..."
reg_resp=$(
    curl -sS -X POST "${USERVER_AUTH_HOST}/auth/register" \
        -H "Content-Type: application/json" \
        --data @- <<END
{
  "username": "${USERVER_AUTH_USER}",
  "system_name": "${USERVER_AUTH_SYSTEM_NAME}",
  "system_token": "${USERVER_AUTH_SYSTEM_TOKEN}",
  "password": "${USERVER_AUTH_PASSWORD}",
  "is_admin": true
}
END
)

echo "Register response:"
echo "${reg_resp}"

echo "Checking auth of created user (login)..."
login_resp=$(
    curl -sS -X POST "${USERVER_AUTH_HOST}/auth/login" \
        -H "Content-Type: application/json" \
        --data @- <<END
{
  "username": "${USERVER_AUTH_USER}",
  "system_name": "${USERVER_AUTH_SYSTEM_NAME}",
  "system_token": "${USERVER_AUTH_SYSTEM_TOKEN}",
  "password": "${USERVER_AUTH_PASSWORD}"
}
END
)
echo "Login response:"
echo "${login_resp}"

echo "===== SETUP COMPLETED! ====="
exit 0
