from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from pydantic import BaseModel

from .db import db
from .db_models import User, Role, UserRole


class ActionResponse(BaseModel):
    success: bool
    obj: None | User | Role | UserRole
    message: None | str

    class Config:
        arbitrary_types_allowed = True


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


def set_role(user_id: UUID, role_id: UUID) -> ActionResponse:
    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.session.add(user_role)
    db.session.commit()

    return ActionResponse(
        success=True,
        obj=user_role,
        message=None
    )


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
