from http import HTTPStatus

from requests_oauthlib import OAuth2Session
from flask import session, redirect, Response

from database import db_social_actions, db_actions
from utils.settings import settings
from utils.token_generator import get_tokens


class MainProvider:

    def authorization(self):
        oauth_provider = OAuth2Session(
            client_id=self.client_id,
            scope=self.scope,
            redirect_uri=self.redirect_uri
        )
        authorization_url, state = oauth_provider.authorization_url(self.authorization_base_url)

        session['oauth_state'] = state
        return redirect(authorization_url)

    def callback(self, oauth_state, request):

        oauth_provider = OAuth2Session(
            client_id=self.client_id,
            scope=self.scope,
            redirect_uri=self.redirect_uri,
            state=oauth_state
        )

        oauth_provider.fetch_token(
            token_url=self.token_url,
            client_secret=self.client_secret,
            authorization_response=request.url,
        )

        content = oauth_provider.get(
            url=self.info_url,
            params={'format': 'json'}
        ).json()

        response = db_social_actions.get_account_by_login(
            email=content[self.email_field],
            user_id=content['id'],
            provider=self.provider
        )
        if response.success:
            db_actions.add_record_to_log_history(user=response.obj.user, user_agent=request.headers['user_agent'])
            return get_tokens(response.obj.user)
        return Response(response.message, status=HTTPStatus.UNAUTHORIZED)


class VKProvider(MainProvider):
    def __init__(self):
        self.client_id = settings.vk_client_id
        self.scope = 'email'
        self.redirect_uri = settings.redirect_uri + 'vk/callback'
        self.callback_redirect_uri = None
        self.authorization_base_url = settings.vk_authorization_base_url
        self.token_url = settings.vk_token_url
        self.client_secret = settings.vk_client_secret
        self.provider = 'vk'

    def callback(self, oauth_state, request):
        oauth_provider = OAuth2Session(
            client_id=self.client_id,
            scope=self.scope,
            redirect_uri=self.redirect_uri,
            state=oauth_state
        )

        token = oauth_provider.fetch_token(
            token_url=self.token_url,
            include_client_id=self.client_id,
            client_secret=self.client_secret,
            authorization_response=request.url,
            code=request.args.get('code')
        )

        response = db_social_actions.get_account_by_login(
            email=token['email'],
            user_id=token['user_id'],
            provider=self.provider
        )
        if response.success:
            db_actions.add_record_to_log_history(user=response.obj.user, user_agent=request.headers['user_agent'])
            return get_tokens(response.obj.user)
        return Response(response.message, status=HTTPStatus.UNAUTHORIZED)


class YandexProvider(MainProvider):
    def __init__(self):
        self.client_id = settings.yandex_client_id
        self.scope = None
        self.redirect_uri = settings.redirect_uri + 'yandex/callback'
        self.callback_redirect_uri = None
        self.authorization_base_url = settings.yandex_authorization_base_url
        self.token_url = settings.yandex_token_url
        self.client_secret = settings.yandex_client_secret
        self.info_url = settings.yandex_info_url
        self.email_field = 'default_email'
        self.provider = 'yandex'


class GoogleProvider(MainProvider):
    def __init__(self):
        self.client_id = settings.google_client_id
        self.scope = settings.google_scope
        self.redirect_uri = settings.redirect_uri + 'google/callback'
        self.callback_redirect_uri = settings.redirect_uri + 'google/callback'
        self.authorization_base_url = settings.google_authorization_base_url
        self.token_url = settings.google_token_url
        self.client_secret = settings.google_client_secret
        self.info_url = settings.google_info_url
        self.email_field = 'email'
        self.provider = 'google'


def get_provider(provider: str):
    social_services = {'vk': VKProvider,
                       'google': GoogleProvider,
                       'yandex': YandexProvider
                       }

    return social_services.get(provider)
