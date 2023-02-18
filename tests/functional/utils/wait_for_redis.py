import time
from redis import Redis
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import settings


if __name__ == '__main__':
    redis_client = Redis(
        host=settings.redis_host, port=settings.redis_port,
        decode_responses=True
    )
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
