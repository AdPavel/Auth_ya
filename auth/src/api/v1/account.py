from datetime import timedelta
from http import HTTPStatus

from database.redis_db import redis_app
from flask import Blueprint, request, Response, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, \
    get_jwt
from redis_rate_limiter.config import basic_config
from redis_rate_limiter.rate_limiter import RateLimiter

from utils.settings import settings
from email_validator import validate_email, EmailNotValidError
from database import db_actions
from database import db_role_actions
from utils.token_generator import get_tokens


account = Blueprint('account', __name__, url_prefix='/account')
basic_config(redis_url=f'redis://{settings.redis_host}:{settings.redis_port}/0')


@account.route('/create_user', methods=['POST'])
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def create_user():

    """Регистрация нового пользователя"""

    data = request.get_json()
    login = data.get('email', None)
    password = data.get('password', None)
    try:
        validate_email(login, check_deliverability=False)
    except EmailNotValidError:
        return Response('You have to pass valid email and password', status=HTTPStatus.BAD_REQUEST)
    if not login or not password:
        return Response('You have to pass valid email and password', status=HTTPStatus.BAD_REQUEST)

    response = db_actions.create_user(login, password)
    if response.success:
        return Response('Successful operation', status=HTTPStatus.CREATED)
    return Response(response.message, status=HTTPStatus.CONFLICT)


@account.route('/login', methods=['POST'])
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def login():

    """Вход пользователя"""

    data = request.get_json()
    login = data.get('email', None)
    password = data.get('password', None)

    if not login or not password:
        return Response('you have to pass email ans password', status=HTTPStatus.BAD_REQUEST)

    response = db_actions.get_user(login, password)
    if response.success:
        db_actions.add_record_to_log_history(user=response.obj, user_agent=request.headers['user_agent'])
        return get_tokens(response.obj)
    return Response(response.message, status=HTTPStatus.UNAUTHORIZED)


@account.route('/change_login', methods=['PUT'])
@jwt_required()
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def change_login():

    """Изменение логина"""

    data = request.get_json()
    new_login = data.get('email', None)

    try:
        validate_email(new_login, check_deliverability=False)
    except EmailNotValidError:
        return Response('Email is not valid', status=HTTPStatus.BAD_REQUEST)

    user = db_actions.get_user_by_login(new_login)
    if user:
        return Response('User with this name already exists', status=HTTPStatus.CONFLICT)

    user_id = get_jwt_identity()

    current_user = db_actions.get_user_by_id(user_id)
    db_actions.change_user_login(user=current_user, login=new_login)

    return Response('Successful operation', status=HTTPStatus.OK)


@account.route('/change_password', methods=['PUT'])
@jwt_required()
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def change_password():

    """Изменение пароля"""

    data = request.get_json()
    new_password = data.get('password', None)

    user_id = get_jwt_identity()
    user = db_actions.get_user_by_id(user_id)

    db_actions.change_user_password(user, new_password)
    return Response('Successful operation', status=HTTPStatus.OK)


@account.route('/history', methods=['GET'])
@jwt_required()
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def get_log_history():

    """Получение истории входов пользователя"""

    user_id = get_jwt_identity()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    history = db_actions.get_user_log_history(user_id, page, per_page)
    return jsonify(history)


# работает для ACCESS и Refresh, отправляем по очереди
@account.route('/logout', methods=['DELETE'])
@jwt_required(verify_type=False)
def logout():

    """Выход пользователя"""

    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    redis_app.set(jti, '', ex=timedelta(days=settings.access_token_expires_hours))
    return Response(f"{ttype.capitalize()} token has been revoked", status=HTTPStatus.OK)


@account.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():

    """Обновление токена"""

    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token})


@account.route('', methods=['GET'])
@jwt_required()
@db_role_actions.admin_access
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def get_all_users():

    """Получение списка пользователей"""

    output = db_actions.get_users()

    return jsonify({'Users': output})
