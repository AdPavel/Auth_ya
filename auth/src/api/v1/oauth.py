from http import HTTPStatus

from flask import request, session, Response, Blueprint
from interfaces.providers import get_provider


oauth = Blueprint('oauth', __name__, url_prefix='/oauth')


@oauth.route('/<provider>')
def authorization(provider):

    """Вход пользователя через социальные сети"""

    provider = get_provider(provider)
    if provider:
        provider_init = provider()
        return provider_init.authorization()
    return Response("Provider doesn't exist", status=HTTPStatus.BAD_REQUEST)


@oauth.route('/<provider>/callback', methods=['GET'])
def authorization_callback(provider):

    """Колбэк для провайдеров социальных сетей"""

    provider_init = get_provider(provider)()
    return provider_init.callback(oauth_state=session['oauth_state'], request=request)
