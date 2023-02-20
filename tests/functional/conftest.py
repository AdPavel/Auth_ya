import os
import sys

import pytest

sys.path.append(os.path.dirname(__file__) + '/..')
from app import get_app
from utils.settings import settings
from database.db_models import User, Role, LogHistory
from database.db import db
from database import db_actions


@pytest.fixture()
def app():
    app = get_app()
    yield app


@pytest.fixture()
def app_with_db(app):

    user = settings.postgres_user
    password = settings.postgres_password
    host = settings.postgres_host
    port = settings.postgres_port
    db_name = settings.postgres_db

    app.config.update({
        'SQLALCHEMY_DATABASE_URI': f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    })
    app.config.update({
        'TESTING': True,
    })
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    db.init_app(app)
    app.app_context().push()
    db.drop_all()
    db.create_all()

    yield app
    db.session.remove()


@pytest.fixture()
def create_user():
    response = db_actions.create_user('test', 'test')
    user = response.obj
    return user


@pytest.fixture()
def client_with_db(app_with_db, create_user):
    return app_with_db.test_client()
