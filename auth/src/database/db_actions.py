from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel
from typing import Union
from datetime import datetime

from database.db import db
from database.db_models import User, Role, LogHistory


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


def get_user_by_login(login: str) -> Union[None, User]:
    user = User.query.filter_by(login=login).first()
    return user


def get_user_by_id(id: UUID) -> Union[None, User]:
    user = User.query.filter_by(id=id).first()
    return user


def change_user_login(user: User, login: str):
    user.login = login
    db.session.commit()


def change_user_password(user: User, password: str):
    user.password = generate_password_hash(password, method='sha256')
    db.session.commit()


def get_user(login: str, password: str) -> ActionResponse:
    user = get_user_by_login(login)
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


def get_user_log_history(user_id: UUID) -> list:
    log_history = (LogHistory.query
                             .filter_by(user_id=user_id)
                             .order_by(LogHistory.login_time.desc())
                             .limit(10))
    result = [
        {
            'id': log.id,
            'user_agent': log.user_agent,
            'login_date': log.login_time
        } for log in log_history
    ]
    return result


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


def get_users():
    all_users = User.query.all()
    output = []

    for user in all_users:
        user_data = {'id': user.id, 'login': user.login}
        output.append(user_data)

    return output
