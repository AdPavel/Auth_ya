from gevent import monkey

monkey.patch_all()

from app import get_app

app = get_app()
