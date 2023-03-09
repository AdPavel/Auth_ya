from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from utils.settings import settings

user = settings.postgres_user
password = settings.postgres_password
host = settings.postgres_host
port = settings.postgres_port
db_name = settings.postgres_db

SQLALCHEMY_DATABASE_URI = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'

db = SQLAlchemy()
migrate = Migrate()


def init_db(app: Flask) -> None:
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    db.init_app(app)
