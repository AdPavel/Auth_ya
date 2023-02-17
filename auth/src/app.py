import backoff
from flask import Flask
import click

from database.db import db, init_db
from database.db_actions import create_user
from database import db_role_actions
from database.db_models import User, Role, LogHistory
from flask_jwt_extended import JWTManager
from api.v1.roles import roles
from api.v1.account import account
from utils.settings import settings
from datetime import timedelta
from database.redis_db import redis_app


@backoff.on_exception(
    wait_gen=backoff.expo, exception=Exception,
    max_tries=10
)
def get_app() -> Flask:

    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = settings.secret_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=settings.access_token_expires_hours)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=settings.refresh_token_expires_days)

    # app.config['JWT_BLACKLIST_ENABLED'] = True # без этого тоже работает
    # app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access'] #, 'refresh'] - исключить из листа рефреш?

    jwt = JWTManager(app)

    init_db(app)
    app.app_context().push()
    db.create_all()
    db_role_actions.create_role('admin')

    app.register_blueprint(roles, url_prefix='/api/v1/roles')
    app.register_blueprint(account, url_prefix='/api/v1/account')

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload['jti']
        token_in_redis = redis_app.get(jti)
        return token_in_redis is not None

    @app.cli.command("create_superuser")
    @click.argument("login")
    @click.argument("password")
    def create_superuser(login, password):

        response = create_user(login, password)
        if response.success:
            superuser_role = Role.query.filter_by(name='admin').first()
            db_role_actions.set_role(response.obj, superuser_role)

    app.cli.add_command(create_superuser)

    return app


if __name__ == '__main__':
    app = get_app()
    app.run(debug=True,
            host='0.0.0.0',
            port=8001,
            )
