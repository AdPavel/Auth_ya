from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from database.db_models import User


def get_tokens(user: User):

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token
    )
