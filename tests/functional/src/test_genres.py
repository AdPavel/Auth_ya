import pytest
import uuid
import json
from http import HTTPStatus

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': '/genres/640d1ac4-0f5a-465b-a75c-45941d28198b'},
            {'status': HTTPStatus.OK, 'length': 3}
        ),
        (
            {'query': '/genres/640d1ac4-0f5a-465b-a75c-45941d281900'},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_genres_detail(make_request, query_data, expected_answer):
    response = await make_request(endpoint=query_data['query'])
    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']


@pytest.mark.asyncio
async def test_genres_list(make_request):
    response = await make_request(endpoint='/genres/', params={'size': 50, 'page': 1})
    assert response['status'] == HTTPStatus.OK
    assert len(response['body']) == 50


@pytest.mark.asyncio
async def test_bad_request_genre(es_client):

    genre_id = uuid.uuid4()
    data = {'id': genre_id, 'name': 'Test', 'desc': 'wrong_field'}

    try:
        await es_client.create('genres', genre_id, data)
    except:
        assert HTTPStatus.BAD_REQUEST

