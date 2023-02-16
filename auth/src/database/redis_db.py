import redis

from utils.settings import settings

host = settings.redis_host
port = settings.redis_port

redis_app = redis.Redis(host=host, port=port, db=0)
