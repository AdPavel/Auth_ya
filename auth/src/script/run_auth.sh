#!/bin/sh

flask db upgrade
gunicorn --worker-class=gevent --worker-connections=1000 --workers=3 --bind 0.0.0.0:8001 wsgi_app:app