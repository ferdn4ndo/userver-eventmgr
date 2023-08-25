#!/bin/bash

if [ "${ENV_MODE}" == "prod" ]
then
  echo "Starting in production mode..."

  gunicorn --access-logfile /code/logs/access.log --worker-tmp-dir /dev/shm --workers ${GUVICORN_WORKERS} --bind 0.0.0.0:5000 filemgr.wsgi
else
  echo "Starting in development mode..."

  python manage.py runserver 0.0.0.0:5000
fi
