from requests_oauthlib import OAuth2Session
from flask import request, redirect, session, Response
from flask import Blueprint
from utils.settings import settings
from database import db_social_actions, db_actions
from http import HTTPStatus
from utils.token_generator import get_tokens


oauth = Blueprint('oauth', __name__, url_prefix='/oauth')

social_services = {
    'google': {
        'client_id': settings.google_client_id,
        'scope': settings.google_scope,
        'redirect_uri': settings.redirect_uri + 'google/callback',
        'callback_redirect_uri': settings.redirect_uri + 'google/callback',
        'authorization_base_url': settings.google_authorization_base_url,
        'token_url': settings.google_token_url,
        'client_secret': settings.google_client_secret,
        'info_url': settings.google_info_url,
        'email_field': 'email'
    },
    'yandex': {
        'client_id': settings.yandex_client_id,
        'scope': None,
        'redirect_uri': settings.redirect_uri + 'yandex/callback',
        'callback_redirect_uri': None,
        'authorization_base_url': settings.yandex_authorization_base_url,
        'token_url': settings.yandex_token_url,
        'client_secret': settings.yandex_client_secret,
        'info_url': settings.yandex_info_url,
        'email_field': 'default_email'
    }
}


@oauth.route('/<provider>')
def authorization(provider):

    oauth_provider = OAuth2Session(
        client_id=social_services[provider]['client_id'],
        scope=social_services[provider]['scope'],
        redirect_uri=social_services[provider]['redirect_uri']
    )
    authorization_url, state = oauth_provider.authorization_url(
        social_services[provider]['authorization_base_url']
    )

    session['oauth_state'] = state
    return redirect(authorization_url)


@oauth.route('/<provider>/callback', methods=['GET'])
def authorization_callback(provider):

    oauth_provider = OAuth2Session(
        client_id=social_services[provider]['client_id'],
        redirect_uri=social_services[provider]['redirect_uri'],
        state=session['oauth_state']
    )
    oauth_provider.fetch_token(
        token_url=social_services[provider]['token_url'],
        client_secret=social_services[provider]['client_secret'],
        authorization_response=request.url
    )
    content = oauth_provider.get(
        url=social_services[provider]['info_url'],
        params={'format': 'json'}
    ).json()
    print(content)

    response = db_social_actions.get_account_by_login(
        email=content[social_services[provider]['email_field']],
        user_id=content['id'],
        provider=provider
    )
    if response.success:
        print(response)
        db_actions.add_record_to_log_history(user=response.obj.user, user_agent=request.headers['user_agent'])
        return get_tokens(response.obj.user)
    return Response(response.message, status=HTTPStatus.UNAUTHORIZED)
