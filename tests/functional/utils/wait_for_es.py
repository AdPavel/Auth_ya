import time
from elasticsearch import Elasticsearch
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import settings


if __name__ == '__main__':
    es_client = Elasticsearch(
        hosts=f'http://{settings.els_host}:{settings.els_port}',
        validate_cert=False, use_ssl=False
    )
    while True:
        if es_client.ping():
            es_client.close()
            break
        time.sleep(1)
