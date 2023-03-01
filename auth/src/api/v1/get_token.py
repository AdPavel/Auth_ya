from flask import  jsonify
from database import db_actions
from flask_jwt_extended import create_access_token, create_refresh_token


def get_access_refresh_tokens(user, user_agent):
    db_actions.add_record_to_log_history(user, user_agent)

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token
    )
