from flask import request, session
from flask import Blueprint

from interfaces.providers import get_provider

oauth = Blueprint('oauth', __name__, url_prefix='/oauth')


@oauth.route('/<provider>')
def authorization(provider):

    """Вход пользователя через социальные сети"""

    provider_init = get_provider(provider)()
    return provider_init.authorization()


@oauth.route('/<provider>/callback', methods=['GET'])
def authorization_callback(provider):

    """Колбэк для провайдеров социальных сетей"""

    provider_init = get_provider(provider)()
    return provider_init.callback(oauth_state=session['oauth_state'], request=request)
