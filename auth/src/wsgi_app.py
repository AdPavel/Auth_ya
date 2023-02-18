from gevent import monkey

monkey.patch_all()

from app import app_with_db

app = app_with_db()
