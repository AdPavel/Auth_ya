import backoff
from flask import Flask

from database.db import db, init_db
from database.db_models import User


@backoff.on_exception(
    wait_gen=backoff.expo, exception=Exception,
    max_tries=10
)
def get_app() -> Flask:
    app = Flask(__name__)
    init_db(app)
    app.app_context().push()
    db.create_all()

    return app


if __name__ == '__main__':
    app = get_app()
    app.run()
