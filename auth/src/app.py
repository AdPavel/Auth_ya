import backoff
from flask import Flask
import click
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import db, init_db
from database.db_models import User, Role, LogHistory, UserRole


def create_admin_role():
    admin = Role(name='admin')
    db.session.add(admin)
    db.session.commit()


@backoff.on_exception(
    wait_gen=backoff.expo, exception=Exception,
    max_tries=10
)
def get_app() -> Flask:
    app = Flask(__name__)
    init_db(app)
    app.app_context().push()
    db.create_all()
    create_admin_role()

    @app.cli.command("create_superuser")
    @click.argument("login")
    @click.argument("password")
    def create_superuser(login, password):

        hashed_password = generate_password_hash(password, method='sha256')
        superuser = User(login=login, password=hashed_password)
        db.session.add(superuser)
        db.session.commit()

        superuser_role = Role.query.filter_by(name='admin').first()
        user_role = UserRole(user_id=superuser.id, role_id=superuser_role.id)
        db.session.add(user_role)
        db.session.commit()

    app.cli.add_command(create_superuser)
    return app


if __name__ == '__main__':
    app = get_app()
    app.run()
