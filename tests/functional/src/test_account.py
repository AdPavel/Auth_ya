from http import HTTPStatus


def test_create_user(client_with_db):
    response = client_with_db.post(
        '/api/v1/account/create_user',
        json={"login": "test", "password": "password"}
    )
    assert response.status_code == HTTPStatus.CREATED
