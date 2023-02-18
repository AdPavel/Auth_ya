import backoff
from redis import Redis
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import settings


@backoff.on_exception(
    wait_gen=backoff.expo, exception=Exception
)
def wait_for_redis():
    redis_client = Redis(
        host=settings.redis_host, port=settings.redis_port,
        decode_responses=True
    )
    ping = redis_client.ping()
    if ping:
        return ping
    raise Exception


if __name__ == '__main__':
    wait_for_redis()
