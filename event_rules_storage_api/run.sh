#!/bin/sh

env LC_ALL=C.UTF-8 LANG=C.UTF-8 FLASK_CONFIG=production FLASK_APP=run.py

flask db upgrade

flask run --host=0.0.0.0
