from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
import datetime
from functools import wraps
from flask import Blueprint

from database.db import db
from database.db_models import Role

roles = Blueprint('roles', __name__, url_prefix='/roles')


@roles.route('/create', methods=['POST'])
def create_role():
    # if not current_user.admin:
    #     return jsonify({'message': 'Cannot perform that function!'})

    data = request.get_json()
    role_name = data['name']
    name = Role.query.filter_by(name=role_name).first()
    if name:
        return jsonify({'message': 'This role is exist!'})

    new_role = Role(name=role_name)
    db.session.add(new_role)
    db.session.commit()

    return jsonify({'message': f'New role - "{role_name}" created!'})


@roles.route('/delete', methods=['DELETE'])
def delete_role():
    data = request.get_json()
    role_for_delete = Role.query.filter_by(id=data['id']).first()

    if not delete_role:
        return jsonify({'message': 'No role found!'})

    db.session.delete(role_for_delete)
    db.session.commit()

    return jsonify({'message': 'Role deleted!'})


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
