from http import HTTPStatus
import pytest
from database.db_actions import get_user_by_login
from database import db_role_actions
from flask_jwt_extended import create_access_token


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'data': {'name': 'user'}},
            {'status': HTTPStatus.CREATED}
        ),
        (
            {'data': {'name': 'test_role'}},
            {'status': HTTPStatus.BAD_REQUEST}
        ),
    ]
)
def test_create_role(client_with_db, create_user_admin, create_role, query_data: dict, expected_answer: dict):
    user = get_user_by_login('admin_test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.post(
        '/api/v1/roles',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == expected_answer['status']

    response = client_with_db.post(
        '/api/v1/roles',
        headers={
            'Authorization': 'Bearer ' + '123'
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.post(
        '/api/v1/roles',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_role(client_with_db, create_user_admin, create_role):
    role = db_role_actions.get_role_by_name('test_role')
    response = client_with_db.delete(
        f'/api/v1/roles/{role.id}',
        headers={
            'Authorization': 'Bearer ' + '123'
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    role = db_role_actions.get_role_by_name('test_role')
    response = client_with_db.delete(
        f'/api/v1/roles/{role.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    user = get_user_by_login('admin_test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.delete(
        '/api/v1/roles/6c62b72f-fb6f-49c8-b9f6-96180d239c10',
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    user = get_user_by_login('admin_test')
    access_token = create_access_token(identity=user.id)
    role = db_role_actions.get_role_by_name('test_role')
    response = client_with_db.delete(
        f'/api/v1/roles/{role.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    )

    assert response.status_code == HTTPStatus.OK


def test_change_role(client_with_db, create_user_admin, create_role):
    role = db_role_actions.get_role_by_name('test_role')
    query_data = {'data': {'name': 'new_role'}}
    response = client_with_db.put(
        f'/api/v1/roles/{role.id}',
        headers={
            'Authorization': 'Bearer ' + '123'
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    role = db_role_actions.get_role_by_name('test_role')
    query_data = {'data': {'name': 'new_role'}}
    response = client_with_db.put(
        f'/api/v1/roles/{role.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    user = get_user_by_login('admin_test')
    access_token = create_access_token(identity=user.id)
    role = db_role_actions.get_role_by_name('test_role')
    query_data = {'data': {'name': 'test_role'}}
    response = client_with_db.put(
        f'/api/v1/roles/{role.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    user = get_user_by_login('admin_test')
    access_token = create_access_token(identity=user.id)
    role = db_role_actions.get_role_by_name('test_role')
    query_data = {'data': {'name': 'new_role'}}
    response = client_with_db.put(
        f'/api/v1/roles/{role.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.CREATED


def test_get_all_roles(client_with_db, create_user_admin, create_role):
    response = client_with_db.get(
        '/api/v1/roles',
        headers={
            'Authorization': 'Bearer ' + '123'
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.get(
        '/api/v1/roles',
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    user = get_user_by_login('admin_test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.get(
        '/api/v1/roles',
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    )

    assert response.status_code == HTTPStatus.OK


def test_get_user_roles(client_with_db, create_user_admin, create_role):
    user = get_user_by_login('test')
    response = client_with_db.get(
        f'/api/v1/roles/user/{user.id}',
        headers={
            'Authorization': 'Bearer ' + '123'
        }
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.get(
        f'/api/v1/roles/user/{user.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    user = get_user_by_login('admin_test')
    access_token = create_access_token(identity=user.id)
    response = client_with_db.get(
        f'/api/v1/roles/user/{user.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    )

    assert response.status_code == HTTPStatus.OK


def test_set_user_roles(client_with_db, create_user_admin, create_role):
    user = get_user_by_login('test')
    role = db_role_actions.get_role_by_name('test_role')
    query_data = {'data': {'name': role.name}}
    response = client_with_db.post(
        f'/api/v1/roles/user/{user.id}',
        headers={
            'Authorization': 'Bearer ' + '123'
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    role = db_role_actions.get_role_by_name('test_role')
    query_data = {'data': {'name': role.name}}
    response = client_with_db.post(
        f'/api/v1/roles//user{user.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    user = get_user_by_login('admin_test')
    access_token = create_access_token(identity=user.id)
    role = db_role_actions.get_role_by_name('test_role')
    query_data = {'data': {'name': role.name}}
    response = client_with_db.post(
        f'/api/v1/roles/user/{user.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )
    #
    assert response.status_code == HTTPStatus.CREATED


def test_delete_user_roles(client_with_db, create_user_admin, create_role):
    user = get_user_by_login('test')
    role = db_role_actions.get_role_by_name('test_role')
    query_data = {'data': {'name': role.name}}
    response = client_with_db.delete(
        f'/api/v1/roles/user/{user.id}',
        headers={
            'Authorization': 'Bearer ' + '123'
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    user = get_user_by_login('test')
    access_token = create_access_token(identity=user.id)
    role = db_role_actions.get_role_by_name('test_role')
    query_data = {'data': {'name': role.name}}
    response = client_with_db.delete(
        f'/api/v1/roles/user/{user.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    user = get_user_by_login('admin_test')
    access_token = create_access_token(identity=user.id)
    role = db_role_actions.get_role_by_name('admin')
    query_data = {'data': {'name': role.name}}
    response = client_with_db.delete(
        f'/api/v1/roles/user/{user.id}',
        headers={
            'Authorization': 'Bearer ' + access_token
        },
        json=query_data['data']
    )

    assert response.status_code == HTTPStatus.OK
