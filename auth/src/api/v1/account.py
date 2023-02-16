from datetime import timedelta
from http import HTTPStatus

from database import db_actions
from database.redis_db import redis_app
from flask import Blueprint, request, Response, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti, jwt_required, get_jwt_identity
from utils.settings import settings

account = Blueprint('account', __name__, url_prefix='/account')


@account.route('/create_user', methods=['POST'])
def create_user():

    data = request.get_json()
    login = data.get('login', None)
    password = data.get('password', None)

    if not login or not password:
        return Response('You have to pass login ans password', status=HTTPStatus.BAD_REQUEST)

    response = db_actions.create_user(login, password)
    if response.success:
        return Response('Successful operation', status=HTTPStatus.CREATED)
    else:
        return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@account.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    login = data.get('login', None)
    password = data.get('password', None)

    if not login or not password:
        return Response('you have to pass login ans password', status=HTTPStatus.BAD_REQUEST)

    response = db_actions.get_user(login, password)
    if response.success:

        user = response.obj
        user_agent = request.headers['user_agent']
        db_actions.add_record_to_log_history(user, user_agent)

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)
        key = get_jti(refresh_token)
        redis_app.set(key, str(user.id), ex=timedelta(days=settings.refresh_token_expires_days))

        return jsonify(
            access_token=access_token,
            refresh_token=refresh_token
        )
    else:
        return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@account.route('/change_login', methods=['PUT'])
@jwt_required()
def change_login():

    data = request.get_json()
    new_login = data.get('login', None)

    user = db_actions.get_user_by_login(new_login)
    if user:
        return Response('Пользователь с таким именем уже существует', status=HTTPStatus.BAD_REQUEST)

    user_id = get_jwt_identity()

    current_user = db_actions.get_user_by_id(user_id)
    db_actions.change_user_login(user=current_user, login=new_login)

    return Response('Successful operation', status=HTTPStatus.OK)


@account.route('/change_password', methods=['PUT'])
@jwt_required()
def change_password():

    data = request.get_json()
    new_password = data.get('password', None)

    user_id = get_jwt_identity()
    user = db_actions.get_user_by_id(user_id)

    db_actions.change_user_password(user, new_password)
    return Response('Successful operation', status=HTTPStatus.OK)


@account.route('/history', methods=['GET'])
@jwt_required()
def get_log_history():
    user_id = get_jwt_identity()
    history = db_actions.get_user_log_history(user_id)
    return jsonify(history)
