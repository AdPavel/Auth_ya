import backoff
from flask import Flask, send_from_directory, request
import click
import os
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

from database.db import db, init_db, migrate
from database.db_actions import create_user
from database import db_role_actions
from database.db_models import User, Role, LogHistory

from api.v1.roles import roles
from api.v1.account import account
from api.v1.oauth import oauth
from utils.settings import settings
from datetime import timedelta
from database.redis_db import redis_app


def get_tracer(app):

    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')

    def configure_tracer() -> None:
        resource = Resource(attributes={
            SERVICE_NAME: 'auth'
        })
        trace.set_tracer_provider(TracerProvider(resource=resource))
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(
                JaegerExporter(
                    agent_host_name=settings.jaeger_host,
                    agent_port=6831,
                )
            )
        )
        if settings.jaeger_enable_console_trace:
            trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    configure_tracer()
    FlaskInstrumentor().instrument_app(app)


@backoff.on_exception(
    wait_gen=backoff.expo, exception=Exception,
    max_tries=10
)
def get_app() -> Flask:

    app = Flask(__name__)

    get_tracer(app)

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)

    app.config['JWT_SECRET_KEY'] = settings.secret_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=settings.access_token_expires_hours)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=settings.refresh_token_expires_days)

    jwt = JWTManager(app)

    swagger_url = '/apidocs/'
    api_url = '/static/openapi.yml'
    swagger_blueprint = get_swaggerui_blueprint(swagger_url, api_url)

    app.register_blueprint(swagger_blueprint)
    app.register_blueprint(roles, url_prefix='/api/v1/roles')
    app.register_blueprint(account, url_prefix='/api/v1/account')
    app.register_blueprint(oauth, url_prefix='/api/v1/oauth')

    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(_jwt_header, jwt_payload: dict):
        jti = jwt_payload['jti']
        token_in_redis = redis_app.get(jti)
        return token_in_redis is not None

    @app.cli.command("create_superuser")
    @click.argument("login")
    @click.argument("password")
    def create_superuser(login, password):

        response = create_user(login, password)
        if response.success:
            db_role_actions.create_role('admin')
            db_role_actions.set_or_del_user_role(response.obj.id, 'admin')

    app.cli.add_command(create_superuser)

    return app


def app_with_db() -> Flask:
    app = get_app()
    init_db(app)
    migrate.init_app(app, db)
    return app


app = app_with_db()

if __name__ == '__main__':
    db_role_actions.create_role('admin')

    app.secret_key = os.urandom(24)
    app.run(debug=True, host='localhost', port=8001)
