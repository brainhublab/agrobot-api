#!/bin/sh

flask db upgrade

if [ "$API_ENV" = "production" ]; then
    echo Production env
    nginx -g 'daemon off;' &
    uwsgi -s /tmp/agrobot_api.sock --manage-script-name --mount /agrobot_api=run:app --master --processes 4
else
    echo Developement env
    env LC_ALL=C.UTF-8 LANG=C.UTF-8 FLASK_CONFIG=production FLASK_APP=run.py
    flask run --host=0.0.0.0
fi
