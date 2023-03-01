from requests_oauthlib import OAuth2Session
from flask import request, redirect, session, Response
from flask import Blueprint
from utils.settings import settings
from database import db_social_actions, db_actions
from http import HTTPStatus
from utils.token_generator import get_tokens


oauth = Blueprint('oauth', __name__, url_prefix='/oauth')


@oauth.route('/yandex')
def authorization():

    oauth_provider = OAuth2Session(client_id=settings.yandex_client_id, redirect_uri=settings.redirect_uri)
    authorization_url, state = oauth_provider.authorization_url(settings.yandex_authorization_base_url)

    session['oauth_state'] = state
    return redirect(authorization_url)


@oauth.route('/google')
def google_authorization():

    oauth_provider = OAuth2Session(
        client_id=settings.google_client_id,
        scope=settings.google_scope,
        redirect_uri=settings.google_redirect_uri
    )
    authorization_url, state = oauth_provider.authorization_url(
        settings.google_authorization_base_url,
        prompt='select_account'
    )

    session['oauth_state'] = state
    return redirect(authorization_url)


@oauth.route('/google/callback', methods=['GET'])
def google_callback():

    oauth_provider = OAuth2Session(
        client_id=settings.google_client_id,
        redirect_uri='http://localhost:8001/api/v1/oauth/google/callback',
        state=session['oauth_state']
    )
    oauth_provider.fetch_token(
        token_url=settings.google_token_url,
        client_secret=settings.google_client_secret,
        authorization_response=request.url
    )
    content = oauth_provider.get(
        url=settings.google_info_url,
        params={'format': 'json'}
    ).json()

    response = db_social_actions.get_account_by_login(
        email=content['email'],
        user_id=content['id'],
        provider='google'
    )
    if response.success:
        db_actions.add_record_to_log_history(user=response.obj.user, user_agent=request.headers['user_agent'])
        return get_tokens(response.obj.user)
    return Response(response.message, status=HTTPStatus.UNAUTHORIZED)


@oauth.route('/yandex/callback', methods=['GET'])
def callback():

    oauth_provider = OAuth2Session(client_id=settings.yandex_client_id, state=session['oauth_state'])
    oauth_provider.fetch_token(
        token_url=settings.yandex_token_url,
        client_secret=settings.yandex_client_secret,
        authorization_response=request.url
    )
    content = oauth_provider.get(
        url=settings.yandex_info_url,
        params={'format': 'json'}
    ).json()

    response = db_social_actions.get_account_by_login(
        email=content['default_email'],
        user_id=content['id'],
        provider='yandex'
    )
    if response.success:
        db_actions.add_record_to_log_history(user=response.obj.user, user_agent=request.headers['user_agent'])
        return get_tokens(response.obj.user)
    return Response(response.message, status=HTTPStatus.UNAUTHORIZED)
