import os
from datetime import timedelta
from http import HTTPStatus

import backoff
import click
import sentry_sdk
from flask import Flask, send_from_directory, request, json
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from redis_rate_limiter.rate_limiter import RateLimitExceeded
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import HTTPException

from api.v1.account import account
from api.v1.oauth import oauth
from api.v1.roles import roles
from database import db_role_actions
from database.db_models import User, Role, LogHistory
from database.db import db, init_db, migrate
from database.db_actions import create_user
from database.redis_db import redis_app
from utils.settings import settings

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    integrations=[
        FlaskIntegration(),
    ],
    traces_sample_rate=1.0
)


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
                    agent_port=settings.jaeger_port,
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

    if settings.jaeger_enable:
        get_tracer(app)

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    app.secret_key = os.urandom(24)

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(e):
        msg = {'status': HTTPStatus.TOO_MANY_REQUESTS, 'msg': "RateLimitExceeded", 'success': False}
        return msg

    @app.errorhandler(HTTPException)
    def handle_exception(e):

        response = e.get_response()
        response.data = json.dumps({
            'code': e.code,
            'name': e.name,
            'description': e.description,
        })
        response.content_type = 'application/json'
        return response

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

    app.run(debug=True, host='localhost', port=8001)
