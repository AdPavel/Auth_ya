from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import BaseModel
from typing import Union
from datetime import datetime
from utils.password_generator import get_random_password
from user_agents import parse

from database.db import db
from database.db_models import User, Role, LogHistory


class ActionResponse(BaseModel):
    success: bool
    obj: Union[None, User, Role, LogHistory]
    message: Union[None, str]

    class Config:
        arbitrary_types_allowed = True


def get_user_device_type(user_agent: str) -> str:
    device_type = parse(user_agent)
    if device_type.is_pc:
        return 'pc'
    elif device_type.is_mobile:
        return 'mobile'
    elif device_type.is_tablet:
        return 'tablet'
    elif device_type.is_bot:
        return 'bot'

    return 'smart'


def add_record_to_log_history(user: User, user_agent: str):
    entry = LogHistory(
        user_id=user.id,
        user_agent=user_agent,
        login_time=datetime.now(),
        user_device_type=get_user_device_type(user_agent)
    )
    db.session.add(entry)
    db.session.commit()


def create_user(login: str, password: str = '') -> ActionResponse:
    user = get_user_by_login(login)
    if user:
        return ActionResponse(
            success=False,
            obj=None,
            message='User with this login already exists')

    if not password:
        password = get_random_password()
    hashed_password = generate_password_hash(password, method='sha256')
    user = User(login=login, password=hashed_password)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Error of creating user'
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
    if user and check_password_hash(user.password, password):
        return ActionResponse(
            success=True,
            obj=user,
            message=None
        )
    else:
        return ActionResponse(
            success=False,
            obj=None,
            message='Wrong login or password'
        )


def get_user_log_history(user_id: UUID, page: int, per_page: int) -> list:
    log_history = (LogHistory.query
                             .filter_by(user_id=user_id)
                             .order_by(LogHistory.login_time.desc())
                             .paginate(page=page, per_page=per_page))
    result = [
        {
            'id': log.id,
            'user_agent': log.user_agent,
            'login_date': log.login_time,
            'user_device': log.user_device_type,
            'page': page
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
