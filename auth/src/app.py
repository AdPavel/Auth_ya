from flask import Flask
from database.db import init_db


app = Flask(__name__)
init_db(app)


@app.route('/hello-world')
def hello_world():
    return 'Hello, World!'
