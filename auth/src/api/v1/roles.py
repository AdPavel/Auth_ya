import uuid
from datetime import timedelta
from http import HTTPStatus

from flask import jsonify, Response, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from redis_rate_limiter.config import basic_config
from redis_rate_limiter.rate_limiter import RateLimiter

from database.db_models import Role, User
from database import db_role_actions
from utils.settings import settings


roles = Blueprint('roles', __name__, url_prefix='/roles')
basic_config(redis_url=f'redis://{settings.redis_host}:{settings.redis_port}/0')


@roles.route('/create', methods=['POST'])
@db_role_actions.role_required
@jwt_required()
@db_role_actions.admin_access
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def create_role(data):

    response = db_role_actions.create_role(data['name'])
    if response.success:
        return Response('Роль создана', status=HTTPStatus.CREATED)
    return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@roles.route('/delete/<uuid:role_id>', methods=['DELETE'])
@jwt_required()
@db_role_actions.admin_access
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def delete_role(role_id):
    if not role_id:
        return Response('Не указа id роли для удаления', status=HTTPStatus.BAD_REQUEST)

    response = db_role_actions.delete_role(role_id)
    if response.success:
        return Response('Роль удалена', status=HTTPStatus.OK)
    return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@roles.route('', methods=['GET'])
@jwt_required()
@db_role_actions.admin_access
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def get_all_roles():

    all_roles = Role.query.all()
    output = []

    for role in all_roles:
        role_data = {'id': role.id, 'name': role.name}
        output.append(role_data)

    return jsonify({'roles': output})


@roles.route('/change/<uuid:role_id>', methods=['PUT'])
@db_role_actions.role_required
@jwt_required()
@db_role_actions.admin_access
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def change_role(data, role_id):

    response = db_role_actions.update_role(data['name'], role_id)
    if response.success:
        return Response('Роль изменена', status=HTTPStatus.CREATED)
    return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@roles.route('/<uuid:user_id>', methods=['GET'])
@jwt_required()
@db_role_actions.admin_access
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def get_user_roles(user_id: uuid):
    if not user_id:
        Response('Не указан id пользователя', status=HTTPStatus.BAD_REQUEST)

    user = User.query.filter_by(id=user_id).one()
    output = [{'role': role.name} for role in user.role]
    return jsonify({f'{user.login}': output})


@roles.route('/<uuid:user_id>/create', methods=['POST'])
@db_role_actions.role_required
@jwt_required()
@db_role_actions.admin_access
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def set_user_role(data, user_id: uuid):
    role_name = data['name']
    response = db_role_actions.set_or_del_user_role(user_id, role_name)
    if response.success:
        return Response('Роль назначена', status=HTTPStatus.CREATED)
    return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@roles.route('/<uuid:user_id>/delete', methods=['DELETE'])
@jwt_required()
@db_role_actions.admin_access
@RateLimiter(limit=settings.rate_limit_request, period=timedelta(minutes=settings.rate_limit_time))
def delete_user_role(user_id: uuid):
    role_name = request.args.get('role_name')
    response = db_role_actions.set_or_del_user_role(user_id, role_name, is_delete=True)
    if response.success:
        return Response('Роль удалена', status=HTTPStatus.OK)
    return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@roles.route('/get_roles_by_token', methods=['GET'])
@jwt_required()
def get_roles_by_token():

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).one()
    if user:
        user_roles = [role.name for role in user.role]
    else:
        user_roles = ['unauthorized']

    return jsonify({'roles': user_roles})
