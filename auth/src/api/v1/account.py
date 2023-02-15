from flask import Blueprint, request, Response
from http import HTTPStatus

from database import db_actions

account = Blueprint('account', __name__, url_prefix='/account')


@account.route('/create_user', methods=['POST'])
def create_user():

    data = request.get_json()
    login = data.get('login', None)
    password = data.get('password', None)

    if not login or not password:
        return Response('you have to pass login ans password', status=HTTPStatus.BAD_REQUEST)

    response = db_actions.create_user(login, password)
    if response.success:
        return Response('success', status=HTTPStatus.CREATED)
    else:
        return Response(response.message, status=HTTPStatus.BAD_REQUEST)


