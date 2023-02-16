import backoff
from flask import Flask
import click

from database.db import db, init_db
from database.db_actions import create_user, set_role, create_role
from database.db_models import User, Role, LogHistory
from flask_jwt_extended import JWTManager
from api.v1.roles import roles
from api.v1.account import account
from utils.settings import settings
from datetime import timedelta


@backoff.on_exception(
    wait_gen=backoff.expo, exception=Exception,
    max_tries=10
)
def get_app() -> Flask:

    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = settings.secret_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=settings.access_token_expires_hours)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=settings.refresh_token_expires_days)

    jwt_manager = JWTManager(app)

    init_db(app)
    app.app_context().push()
    db.create_all()
    create_role('admin')

    app.register_blueprint(roles, url_prefix='/api/v1/roles')
    app.register_blueprint(account, url_prefix='/api/v1/account')

    @app.cli.command("create_superuser")
    @click.argument("login")
    @click.argument("password")
    def create_superuser(login, password):

        response = create_user(login, password)
        if response.success:
            superuser_role = Role.query.filter_by(name='admin').first()
            set_role(response.obj, superuser_role)#(response.obj.id, superuser_role.id)

    app.cli.add_command(create_superuser)

    return app


if __name__ == '__main__':
    app = get_app()
    app.run(debug=True,
            host='0.0.0.0',
            port=8001,
            )
