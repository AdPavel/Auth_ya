#!/bin/sh

flask db upgrade
gunicorn --bind 0.0.0.0:8001 wsgi_app:app