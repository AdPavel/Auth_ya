from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Union

from .db import db
from .db_models import User, Role, SocialAccount
from database import db_actions


class ActionResponse(BaseModel):
    success: bool
    obj: Union[None, User, Role, SocialAccount]
    message: Union[None, str]

    class Config:
        arbitrary_types_allowed = True


def get_user_social_account_by_login(content: dict, provider: str = '') -> ActionResponse:
    user = db_actions.get_user_by_login(content['default_email'])
    user_social_account = SocialAccount.query.filter_by(user=user).first()
    if not user or not user_social_account:
        response = create_social_account(content, provider)
        # if response
        user_social_account = response.obj
    return ActionResponse(
        success=True,
        obj=user_social_account,
        message=None
    )


def create_social_account(content: dict, provider: str) -> ActionResponse:
    response = db_actions.create_user(content['default_email'])
    user_social_account = SocialAccount(
        user_id=response.obj.id,
        user=response.obj,
        social_id=content['id'],
        social_name=provider
    )

    try:
        db.session.add(user_social_account)
        db.session.commit()
    except IntegrityError:
        return ActionResponse(
            success=False,
            obj=None,
            message='Error of social account'
        )

    return ActionResponse(
        success=True,
        obj=user_social_account,
        message=None
    )

