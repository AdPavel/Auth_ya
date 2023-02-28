from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
from flask import Blueprint
from utils.settings import settings

oauth = Blueprint('oauth', __name__, url_prefix='/oauth')


@oauth.route("/yandex")
def authorization():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider
    using an URL with a few key OAuth parameters.
    """

    oauth_provider = OAuth2Session(settings.yandex_client_id)
    authorization_url, state = oauth_provider.authorization_url(settings.yandex_authorization_base_url)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@oauth.route("/yandex/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    oauth_provider = OAuth2Session(settings.provider['client_id'], state=session['oauth_state'])
    token = oauth_provider.fetch_token(settings.provider['token_url'],
                                       client_secret=settings.provider['client_secret'],
                                       authorization_response=request.url)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))

#
# @oauth.route("/profile", methods=["GET"])
# def profile():
#     """Fetching a protected resource using an OAuth 2 token.
#     """
#     github = OAuth2Session(settings.provider['client_id'], token=session['oauth_token'])
#     return jsonify(github.get('https://api.github.com/user').json())
