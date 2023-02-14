from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask import Blueprint

from database.db import db
from database.db_models import Role

roles = Blueprint('roles', __name__, url_prefix='/roles')


@roles.route('/create', methods=['POST'])
def create_role(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    data = request.get_json()
    new_role = Role(name=data['name'])
    db.session.add(new_role)
    db.session.commit()

    return jsonify({'message': 'New role created!'})
