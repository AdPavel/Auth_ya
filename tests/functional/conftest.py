import asyncio
from redis import asyncio as rasyncio
import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from .settings import settings

pytest_plugins = 'plugins.createdata_fixtures'


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    es_url = 'http://{host}:{port}'.format(
        host=settings.els_host,
        port=settings.els_port
    )
    # !!! Обязательно заменить hosts, сейчас для теста
    # client = AsyncElasticsearch(hosts=f'http://localhost:9200')
    client = AsyncElasticsearch(hosts=es_url)
    yield client
    await client.close()


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    redis_url = 'redis://{host}:{port}'.format(
        host=settings.redis_host,
        port=settings.redis_port
    )
    client = await rasyncio.from_url(redis_url, encoding='utf8', decode_responses=True)
    # !!! Обязательно заменить hosts, сейчас для теста
    # client = rasyncio.from_url('redis://localhost:6379', encoding='utf8', decode_responses=True)
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
def make_request(session):
    async def inner(endpoint: str, params: dict = {}) -> dict:

        url = settings.test_service_url + '/api/v1' + endpoint

        async with session.get(url=url, params=params) as response:
            response = {
                'body': await response.json(),
                'headers': response.headers,
                'status': response.status,
            }
            return response

    return inner
