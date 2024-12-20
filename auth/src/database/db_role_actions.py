from functools import wraps
from http import HTTPStatus
from typing import Union

from sqlalchemy.dialects.postgresql import UUID
from flask import request, Response
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from flask_jwt_extended import get_jwt_identity

from .db import db
from .db_models import User, Role
from database.db_actions import get_user_by_id



def role_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json()
        role = data.get('name', None) or data.get('id', None)

        if not role:
            return Response('Role name or role id is not specified', status=HTTPStatus.BAD_REQUEST)

        return f(data, *args, **kwargs)
    return decorated


def admin_access(f):
    @wraps(f)
    def decorate(*args, **kwargs):
        user_id = get_jwt_identity()
        admin = get_role_by_name('admin')
        user = get_user_by_id(user_id)
        if admin not in user.role:
            return Response('Admin role is required', status=HTTPStatus.FORBIDDEN)
        return f(*args, **kwargs)
    return decorate


def get_role_by_name(role_name: str):
    role = Role.query.filter_by(name=role_name).first()
    return role


def get_role_by_id(_id: UUID):
    role = Role.query.filter_by(id=_id).first()
    return role


class ActionResponse(BaseModel):
    success: bool
    obj: Union[None, User, Role]
    message: Union[None, str]

    class Config:
        arbitrary_types_allowed = True


def set_or_del_user_role(user_id: UUID, role_name: str, is_delete=False) -> ActionResponse:

    if not user_id:
        return ActionResponse(
            success=False,
            obj=None,
            message='User id is not specified'
        )

    user = get_user_by_id(user_id)
    role = get_role_by_name(role_name)
    if not user or not role:
        return ActionResponse(
            success=False,
            obj=None,
            message='No such user or role'
        )

    if not is_delete:
        if role in user.role:
            error_msg = 'The user already has this role'
            return ActionResponse(success=False, obj=None, message=error_msg)
        else:
            user.role.append(role)
            error_msg = 'Failed to add role to user'
    else:
        if role not in user.role:
            error_msg = 'User does not have this role'
            return ActionResponse(success=False, obj=None, message=error_msg)
        else:
            user.role.remove(role)
            error_msg = 'Failed to delete user role'

    try:
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message=error_msg
        )

    return ActionResponse(
        success=True,
        obj=user,
        message=None
    )


def create_role(name: str):
    role_name = get_role_by_name(name)
    if role_name:
        return ActionResponse(
            success=False,
            obj=None,
            message='Role already exists'
        )
    role = Role(name=name)
    try:
        db.session.add(role)
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Role error'
        )

    return ActionResponse(
        success=True,
        obj=role,
        message=None
    )


def delete_role(_id: UUID):
    role_for_delete = get_role_by_id(_id)
    if not role_for_delete:
        return ActionResponse(
            success=False,
            obj=None,
            message='Role not found'
        )
    try:
        db.session.delete(role_for_delete)
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Failed to remove role'
        )

    return ActionResponse(
        success=True,
        obj=role_for_delete,
        message=None
    )


def update_role(new_name: str, _id: UUID):
    role_for_update = get_role_by_id(_id)
    if not role_for_update:
        return ActionResponse(
            success=False,
            obj=None,
            message='Role not found'
        )
    if role_for_update.name == new_name:
        return ActionResponse(
            success=False,
            obj=None,
            message='Role already exists'
        )
    role_for_update.name = new_name
    try:
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Failed to rename role'
        )

    return ActionResponse(
        success=True,
        obj=role_for_update,
        message=None
    )
