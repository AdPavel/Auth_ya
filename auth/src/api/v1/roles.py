from flask import jsonify, Response
from http import HTTPStatus
from flask import Blueprint

from database.db_models import Role, User
from database import db_role_actions


roles = Blueprint('roles', __name__, url_prefix='/roles')


@roles.route('/create', methods=['POST'])
@db_role_actions.role_required
def create_role(role_name):

    response = db_role_actions.create_role(role_name)
    if response.success:
        return Response('Роль создана', status=HTTPStatus.CREATED)
    else:
        return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@roles.route('/delete/<uuid:role_id>', methods=['DELETE'])
def delete_role(role_id):
    if not role_id:
        return Response('Не указа id роли для удаления', status=HTTPStatus.BAD_REQUEST)

    response = db_role_actions.delete_role(role_id)
    if response.success:
        return Response('Роль удалена', status=HTTPStatus.OK)
    else:
        return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@roles.route('', methods=['GET'])
def get_all_roles():

    all_roles = Role.query.all()
    output = []

    for role in all_roles:
        role_data = {}
        role_data['id'] = role.id
        role_data['name'] = role.name
        output.append(role_data)

    return jsonify({'roles': output})


@roles.route('/change/<uuid:role_id>', methods=['PUT'])
@db_role_actions.role_required
def change_role(new_name, role_id):

    response = db_role_actions.update_role(new_name, role_id)
    if response.success:
        return Response('Роль изменена', status=HTTPStatus.CREATED)
    else:
        return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@roles.route('/<uuid:user_id>', methods=['GET'])
def get_user_roles(user_id):
    if not user_id:
        Response('Не указан id пользователя', status=HTTPStatus.BAD_REQUEST)

    user = User.query.filter_by(id=user_id).one()
    output = [{'role': role.name} for role in user.role]
    return jsonify({f'{user.login}': output})


@roles.route('/<uuid:user_id>/create', methods=['POST'])
@db_role_actions.role_required
def set_user_role(role_name, user_id):

    response = db_role_actions.set_or_del_user_role(user_id, role_name)
    if response.success:
        return Response('Роль назначена', status=HTTPStatus.CREATED)
    else:
        return Response(response.message, status=HTTPStatus.BAD_REQUEST)


@roles.route('/<uuid:user_id>/delete', methods=['DELETE'])
@db_role_actions.role_required
def delete_user_role(role_name, user_id):

    response = db_role_actions.set_or_del_user_role(user_id, role_name, is_delete=True)
    if response.success:
        return Response('Роль удалена', status=HTTPStatus.OK)
    else:
        return Response(response.message, status=HTTPStatus.BAD_REQUEST)