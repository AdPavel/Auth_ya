#!/bin/sh

pip install --upgrade pip --default-timeout=100 future
pip install -r /functional/requirements.txt

echo "Waiting for Postgres..."

python /functional/utils/wait_for_db.py

echo "Postgres started"

echo "Waiting for Redis..."

python /functional/utils/wait_for_redis.py

echo "Redis started"

pytest /functional/src --disable-warnings --color=yes -vv