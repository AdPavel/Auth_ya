from typing import Union

from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from .db import db
from .db_models import User, Role, SocialAccount
from database import db_actions


class ActionResponse(BaseModel):
    success: bool
    obj: Union[None, User, Role, SocialAccount]
    message: Union[None, str]

    class Config:
        arbitrary_types_allowed = True


def get_account_by_login(email: str, user_id: str, provider: str = '') -> ActionResponse:
    user = db_actions.get_user_by_login(email)
    user_social_account = SocialAccount.query.filter_by(user=user).first()
    if not user or not user_social_account:
        response = create_account(email, user_id, provider)
        user_social_account = response.obj
    return ActionResponse(
        success=True,
        obj=user_social_account,
        message=None
    )


def create_account(email: str, user_id: str, provider: str) -> ActionResponse:
    response = db_actions.create_user(email)
    user_social_account = SocialAccount(
        user_id=response.obj.id,
        user=response.obj,
        social_id=user_id,
        social_name=provider
    )

    try:
        db.session.add(user_social_account)
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Error with social account'
        )

    return ActionResponse(
        success=True,
        obj=user_social_account,
        message=None
    )
