from sqlalchemy.dialects.postgresql import UUID
from flask import request, Response
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Union
from flask_jwt_extended import get_jwt_identity

from .db import db
from .db_models import User, Role
from functools import wraps
from http import HTTPStatus


def role_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json()
        role_name = data.get('name', None)

        if not role_name:
            return Response('Не указана роль', status=HTTPStatus.BAD_REQUEST)

        return f(role_name, *args, **kwargs)
    return decorated


def admin_access(f):
    @wraps(f)
    def decorate(*args, **kwargs):
        user_id = get_jwt_identity()
        admin = Role.query.filter_by(name='admin').first()
        user = User.query.filter_by(id=user_id).first()
        if admin not in user.role:
            return Response('Необходима роль admin', status=HTTPStatus.FORBIDDEN)
        return f(*args, **kwargs)
    return decorate


class ActionResponse(BaseModel):
    success: bool
    obj: Union[None, User, Role]
    message: Union[None, str]

    class Config:
        arbitrary_types_allowed = True


def set_or_del_user_role(user_id, role_name, is_delete=False) -> ActionResponse:

    if not user_id:
        return ActionResponse(
            success=False,
            obj=None,
            message='Не указан id пользователя'
        )

    user = User.query.filter_by(id=user_id).one()
    role = Role.query.filter_by(name=role_name).one()
    if not user or not role:
        return ActionResponse(
            success=False,
            obj=None,
            message='Нет такого пользователя или роли'
        )

    if not is_delete:
        if role in user.role:
            error_msg = 'У пользователя уже установлена такая роль'
            return ActionResponse(success=False, obj=None, message=error_msg)
        else:
            user.role.append(role)
            error_msg = 'Не удалось добавить роль пользователю'
    else:
        if role not in user.role:
            error_msg = 'У пользователя нет такой роли'
            return ActionResponse(success=False, obj=None, message=error_msg)
        else:
            user.role.remove(role)
            error_msg = 'Не удалось удалить роль пользователю'

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


def set_role(user: User, role: Role) -> ActionResponse:
    user.role.append(role)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Не удалось добавить роль пользователю'
        )

    return ActionResponse(
        success=True,
        obj=user,
        message=None
    )


def create_role(name: str):
    role_name = Role.query.filter_by(name=name).first()
    if role_name:
        return ActionResponse(
            success=False,
            obj=None,
            message='Роль уже существует'
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
    role_for_delete = Role.query.filter_by(id=_id).first()
    if not role_for_delete:
        return ActionResponse(
            success=False,
            obj=None,
            message='Не найдена роль'
        )
    try:
        db.session.delete(role_for_delete)
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Не удалось удалить роль'
        )

    return ActionResponse(
        success=True,
        obj=role_for_delete,
        message=None
    )


def update_role(new_name: str, _id: UUID):
    role_for_update = Role.query.filter_by(id=_id).first()
    if not role_for_update:
        return ActionResponse(
            success=False,
            obj=None,
            message='Не найдена роль'
        )
    role_for_update.name = new_name
    try:
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Не удалось переименовать роль'
        )

    return ActionResponse(
        success=True,
        obj=role_for_update,
        message=None
    )