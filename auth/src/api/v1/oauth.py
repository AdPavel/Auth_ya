from requests_oauthlib import OAuth2Session
from flask import request, redirect, session, Response
from flask import Blueprint
from utils.settings import settings
from database import db_social
from http import HTTPStatus
from api.v1.get_token import get_access_refresh_tokens


oauth = Blueprint('oauth', __name__, url_prefix='/oauth')


@oauth.route('/yandex')
def authorization():

    oauth_provider = OAuth2Session(settings.yandex_client_id, redirect_uri=settings.redirect_uri)
    authorization_url, state = oauth_provider.authorization_url(settings.yandex_authorization_base_url)

    session['oauth_state'] = state
    return redirect(authorization_url)


@oauth.route('/yandex/callback', methods=['GET'])
def callback():

    oauth_provider = OAuth2Session(settings.yandex_client_id, state=session['oauth_state'])
    oauth_provider.fetch_token(settings.yandex_token_url,
                               client_secret=settings.yandex_client_secret,
                               authorization_response=request.url)

    yandex_content = oauth_provider.get('https://login.yandex.ru/info',
                                        params={'format': 'json'}
                                        ).json()

    response = db_social.get_user_social_account_by_login(yandex_content, 'yandex')
    if response.success:
        return get_access_refresh_tokens(user=response.obj.user, user_agent=request.headers['user_agent'])
    return Response(response.message, status=HTTPStatus.UNAUTHORIZED)


