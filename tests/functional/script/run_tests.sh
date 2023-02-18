#!/bin/sh

pip install --upgrade pip --default-timeout=100 future
pip install -r /functional/requirements.txt

echo "Waiting for ElasticSearch..."

python /functional/utils/wait_for_es.py

echo "ElasticSearch started"

echo "Waiting for Redis..."

python /functional/utils/wait_for_redis.py

echo "Redis started"

pytest /functional/src --disable-warnings --color=yes -vv