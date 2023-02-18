import json
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from utils.es_helper import prepare_for_es_insert

from testdata.data import films_data, persons_data, genres_data


async def create_data(es_client: AsyncElasticsearch, index: str, data: list[dict]):

    els_schema_path = f'/functional/testdata/indexes/{index}.json'
    # Для локального запуска
    # els_schema_path = f'../testdata/indexes/{index}.json'
    if not await es_client.indices.exists(index):
        with open(els_schema_path, 'r') as file:
            schema = json.load(file)
        await es_client.indices.create(index=index, body=schema)
    await es_client.indices.refresh(index=index)
    response = await es_client.bulk(index=index, body=prepare_for_es_insert(data, index), refresh=True)
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')


@pytest_asyncio.fixture(scope='session', autouse=True)
async def create_films(es_client):
    await create_data(es_client=es_client, index='movies', data=films_data.data)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def create_persons(es_client):
    await create_data(es_client=es_client, index='persons', data=persons_data.data)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def create_genres(es_client):
    await create_data(es_client=es_client, index='genres', data=genres_data.data)