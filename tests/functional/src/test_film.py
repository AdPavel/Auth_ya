import pytest
import json
from http import HTTPStatus
import uuid


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': '/films/647d1ac4-0f5a-465b-a75c-45941d28198b'},
                {'status': HTTPStatus.OK, 'length': 8}
        ),
        (
                {'query': '/films/647d1ac4-0f5a-465b-a75c-45941d281999'},
                {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_get_film_by_id(make_request, query_data: dict, expected_answer: dict):
    response = await make_request(endpoint=query_data['query'])
    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']


@pytest.mark.asyncio
async def test_get_films(make_request):
    response = await make_request(endpoint='/films/', params={'sort': 'imdb_rating', 'size': 50, 'page': 1})
    assert response['status'] == HTTPStatus.OK
    assert len(response['body']) == 50


@pytest.mark.asyncio
async def test_get_sort_films(make_request):
    response_desc_sorting = await make_request(endpoint='/films/',
                                               params={'sort': '-imdb_rating', 'size': 50, 'page': 1})
    response_asc_sorting = await make_request(endpoint='/films/',
                                               params={'sort': 'imdb_rating', 'size': 50, 'page': 1})
    response_wrong_sorting_field = await make_request(endpoint='/films/',
                                               params={'sort': 'title', 'size': 50, 'page': 1})

    assert response_wrong_sorting_field['status'] == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response_asc_sorting['status'] == HTTPStatus.OK
    assert response_desc_sorting['status'] == HTTPStatus.OK
    assert response_asc_sorting['body'][0]['imdb_rating'] != response_desc_sorting['body'][0]['imdb_rating']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'The Star'},
                {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
                {'query': 'Mashed potato'},
                {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_film_search(make_request, query_data: dict, expected_answer: dict):
    response = await make_request(endpoint='/films/search', params=query_data)
    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']


@pytest.mark.asyncio
async def test_cache_film(make_request, es_client, redis_client):

    film_id = '647d1ac4-0f5a-465b-a75c-45941d28198b'
    response_before_delete = await make_request(endpoint=f'/films/{film_id}')
    assert response_before_delete['status'] == HTTPStatus.OK

    await es_client.delete('movies', film_id)

    cache_key = f'movies:api.v1.films:film_details:{film_id}'
    redis_data = await redis_client.get(cache_key)

    response_after_delete = await make_request(f'/films/{film_id}/')
    assert json.loads(redis_data) == response_before_delete['body']
    assert response_after_delete['status'] == HTTPStatus.OK
    assert response_before_delete['body'] == response_after_delete['body']


@pytest.mark.asyncio
async def test_bad_request_film(es_client):

    film_id = uuid.uuid4()
    data = {'id': film_id, 'name': 'Test', 'role': 'wrong field'}

    try:
        await es_client.create('movies', film_id, data)
    except:
        assert HTTPStatus.BAD_REQUEST