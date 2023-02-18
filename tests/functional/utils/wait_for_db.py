import backoff
import psycopg2
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import settings


@backoff.on_exception(
    wait_gen=backoff.expo, exception=Exception
)
def wait_for_postgres():
    client = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )
    status = client.status
    if status == psycopg2.extensions.STATUS_READY:
        return status
    raise Exception


if __name__ == '__main__':
    wait_for_postgres()
