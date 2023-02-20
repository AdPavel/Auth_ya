from http import HTTPStatus
import pytest
from database.db_actions import get_user_by_login
from flask_jwt_extended import create_access_token, create_refresh_token


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'data': {'login': 'test', 'password': 'password'}},
            {'status': HTTPStatus.CONFLICT}
        ),
        (
            {'data': {'login': 'test_1', 'password': 'password'}},
            {'status': HTTPStatus.CREATED}
        ),
    ]
)
def test_create_user(client_with_db, query_data: dict, expected_answer: dict):
    response = client_with_db.post(
        '/api/v1/account/create_user',
        json=query_data['data']
    )
    assert response.status_code == expected_answer['status']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'data': {'login': 'test', 'password': 'test'}},
            {'status': HTTPStatus.OK}
        ),
        (
            {'data': {'login': 'test_1', 'password': 'test'}},
            {'status': HTTPStatus.UNAUTHORIZED}
        ),
        (
            {'data': {'login': 'test', 'password': 'password'}},
            {'status': HTTPStatus.UNAUTHORIZED}
        ),
    ]
)
def test_login(client_with_db, query_data: dict, expected_answer: dict):
    response = client_with_db.post(
        '/api/v1/account/login',
        json=query_data['data']
    )
    assert response.status_code == expected_answer['status']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'data': {'login': 'test_3'}},
            {'status': HTTPStatus.OK}
        ),
        (
            {'data': {'login': 'test'}},
            {'status': HTTPStatus.CONFLICT}
        )
    ]
)
def test_change_login(client_with_db, query_data: dict, expected_answer: dict):
    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.put(
        '/api/v1/account/change_login',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == expected_answer['status']

    response = client_with_db.put(
        '/api/v1/account/change_login',
        headers={
            'Authorization': 'Bearer ' + '123'
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'data': {'password': 'test'}},
            {'status': HTTPStatus.OK}
        )
    ]
)
def test_change_password(client_with_db, query_data: dict, expected_answer: dict):
    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.put(
        '/api/v1/account/change_password',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == expected_answer['status']

    response = client_with_db.put(
        '/api/v1/account/change_password',
        headers={
            'Authorization': 'Bearer ' + '123'
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_get_log_history(client_with_db):
    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.get(
        '/api/v1/account/history',
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    )

    assert response.status_code == HTTPStatus.OK

    response = client_with_db.get(
        '/api/v1/account/history',
        headers={
            'Authorization': 'Bearer ' + '123'
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_logout(client_with_db):
    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    response = client_with_db.delete(
        '/api/v1/account/logout',
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    )

    assert response.status_code == HTTPStatus.OK

    response = client_with_db.delete(
        '/api/v1/account/logout',
        headers={
            'Authorization': 'Bearer ' + refresh_token
        }
    )

    assert response.status_code == HTTPStatus.OK

    response = client_with_db.delete(
        '/api/v1/account/logout',
        headers={
            'Authorization': 'Bearer ' + '123'
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_refresh(client_with_db):
    user = get_user_by_login('test')
    refresh_token = create_refresh_token(identity=user.id)
    response = client_with_db.post(
        '/api/v1/account/refresh',
        headers={
            'Authorization': 'Bearer ' + refresh_token
        }
    )

    assert response.status_code == HTTPStatus.OK

    response = client_with_db.post(
        '/api/v1/account/refresh',
        headers={
            'Authorization': 'Bearer ' + '123'
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
