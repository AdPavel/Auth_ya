from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ..utils.settings import settings


user = settings.postgres_user
password = settings.postgres_password
host = settings.postgres_host
db_name = settings.postgres_db

db = SQLAlchemy()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}/{db_name}'
    db.init_app(app)
