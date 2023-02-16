from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel
from typing import Union
from datetime import datetime

from database.db import db
from database.db_models import User, Role, users_roles, LogHistory


class ActionResponse(BaseModel):
    success: bool
    obj: Union[None, User, Role, LogHistory]
    message: Union[None, str]

    class Config:
        arbitrary_types_allowed = True


def add_record_to_log_history(user: User, user_agent: str):
    entry = LogHistory(
        user_id=user.id,
        user_agent=user_agent,
        login_time=datetime.now()
    )
    db.session.add(entry)
    db.session.commit()


def create_user(login: str, password: str) -> ActionResponse:
    hashed_password = generate_password_hash(password, method='sha256')
    user = User(login=login, password=hashed_password)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Пользователь с таким login уже существует'
        )

    return ActionResponse(
        success=True,
        obj=user,
        message=None
    )


def get_user(login: str, password: str) -> ActionResponse:
    user = User.query.filter_by(login=login).first()
    if not user:
        return ActionResponse(
            success=False,
            obj=None,
            message='Пользователь не найден'
        )
    if check_password_hash(user.password, password):
        return ActionResponse(
            success=True,
            obj=user,
            message='{"token": "token"}'
        )
    else:
        return ActionResponse(
            success=False,
            obj=None,
            message='Неправильный пароль'
        )


def set_role(user, superuser_role) -> ActionResponse:
    # user_role = users_roles(user_id=user_id, role_id=role_id)
    user.role.append(superuser_role)
    db.session.add(user)
    db.session.commit()

    return ActionResponse(
        success=True,
        obj=user_role,
        message=None
    )
# def set_role(user_id: UUID, role_id: UUID) -> ActionResponse:
#     user_role = users_roles(user_id=user_id, role_id=role_id)
#     db.session.add(user_role)
#     db.session.commit()
#
#     return ActionResponse(
#         success=True,
#         obj=user_role,
#         message=None
#     )


def create_role(name: str):
    role = Role(name=name)
    try:
        db.session.add(role)
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Роль с таким именем уже существует'
        )

    return ActionResponse(
        success=True,
        obj=role,
        message=None
    )
