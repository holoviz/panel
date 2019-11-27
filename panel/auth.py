import codecs
import json
import re

try:
    from urllib import urlencode
except ImportError:
    # python 3
    from urllib.parse import urlencode

import tornado
    
from bokeh.server.auth_provider import AuthProvider
from tornado import httpclient
from tornado.auth import OAuth2Mixin
from tornado.escape import json_decode

from .config import config


class GithubMixin(OAuth2Mixin):
    """GitHub OAuth2 Authentication
    To authenticate with GitHub, first register your application at
    https://github.com/settings/applications/new to get the client ID and
    secret.
    """

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }
    _OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
    _OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    _OAUTH_USER_URL = 'https://api.github.com/user?access_token='

    def get_authenticated_user(self, redirect_uri, client_id, state,
                               client_secret=None, code=None,
                               success_callback=None,
                               error_callback=None):
        """ Fetches the authenticated user
        :param redirect_uri: the redirect URI
        :param client_id: the client ID
        :param state: the unguessable random string to protect against
                      cross-site request forgery attacks
        :param client_secret: the client secret
        :param code: the response code from the server
        :param success_callback: the success callback used when fetching
                                 the access token succeeds
        :param error_callback: the callback used when fetching the access
                               token fails
        """
        if code:
            self._fetch_access_token(
                code,
                success_callback,
                error_callback,
                redirect_uri,
                client_id,
                client_secret,
                state
            )

            return

        params = {
            'redirect_uri': redirect_uri,
            'client_id':    client_id,
            'extra_params': {
                'state': state
            }
        }

        self.authorize_redirect(**params)

    def _fetch_access_token(self, code, success_callback, error_callback,
                           redirect_uri, client_id, client_secret, state):
        """ Fetches the access token.
        :param code: the response code from the server
        :param success_callback: the success callback used when fetching
                                 the access token succeeds
        :param error_callback: the callback used when fetching the access
                               token fails
        :param redirect_uri: the redirect URI
        :param client_id: the client ID
        :param client_secret: the client secret
        :param state: the unguessable random string to protect against
                      cross-site request forgery attacks
        :return:
        """
        if not (client_secret and success_callback and error_callback):
            raise ValueError(
                'The client secret or any callbacks are undefined.'
            )

        params = {
            'code':          code,
            'redirect_url':  redirect_uri,
            'client_id':     client_id,
            'client_secret': client_secret,
            'state':         state
        }

        http = httpclient.AsyncHTTPClient()

        callback_sharing_data = {}

        def use_error_callback(response, decoded_body):
            data = {
                'code': response.code,
                'body': decoded_body
            }

            if response.error:
                data['error'] = response.error

            error_callback(**data)

        def decode_response_body(response):
            """ Decodes the JSON-format response body
            :param response: the response object
            :type response: tornado.httpclient.HTTPResponse
            :return: the decoded data
            """
            # Fix GitHub response.
            body = codecs.decode(response.body, 'ascii')
            body = re.sub('"', '\"', body)
            body = re.sub("'", '"', body)
            body = json.loads(body)

            if response.error:
                use_error_callback(response, body)

                return None

            return body

        def on_authenticate(response):
            """ The callback handling the authentication
            :param response: the response object
            :type response: tornado.httpclient.HTTPResponse
            """
            body = decode_response_body(response)

            if not body:
                return

            if 'access_token' not in body:
                use_error_callback(response, body)

                return

            callback_sharing_data['access_token'] = body['access_token']

            http.fetch(
                '{}{}'.format(
                    self._OAUTH_USER_URL, callback_sharing_data['access_token']
                ),
                on_fetching_user_information,
                headers=self._API_BASE_HEADERS
            )

        def on_fetching_user_information(response):
            """ The callback handling the data after fetching the user info
            :param response: the response object
            :type response: tornado.httpclient.HTTPResponse
            """
            # Fix GitHub response.
            user = decode_response_body(response)

            if not user:
                return

            success_callback(user, callback_sharing_data['access_token'])

        # Request the access token.
        http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            on_authenticate,
            method='POST',
            body=urlencode(params),
            headers=self._API_BASE_HEADERS
        )


class GithubLoginHandler(tornado.web.RequestHandler, GithubMixin):

    x_site_token = 'application'

    @tornado.gen.coroutine
    def get(self):
        redirect_uri = "{0}://{1}".format(
            self.request.protocol,
            self.request.host
        )
        params = {
            'redirect_uri': redirect_uri,
            'client_id':    config.oauth_key,
            'state':        self.x_site_token
        }
        code = self.get_argument('code', None)
        # Seek the authorization
        if code:
            # For security reason, the state value (cross-site token) will be
            # retrieved from the query string.
            params.update({
                'client_secret': config.oauth_secret,
                'success_callback': self._on_auth,
                'error_callback': self._on_error,
                'code':  code,
                'state': self.get_argument('state', None)
            })
            yield self.get_authenticated_user(**params)
            return
        # Redirect for user authentication
        self.get_authenticated_user(**params)

    def _on_auth(self, user):
        self.set_cookie('user', str(user['id']))
        self.redirect('/app')

    def _on_error(self, user):
        self.clear_all_cookies()
        raise tornado.web.HTTPError(500, 'Github authentication failed')


class OAuthProvider(AuthProvider):

    @property
    def get_user(self):
        def get_user(request_handler):
            return request_handler.get_cookie("user")
        return get_user

    @property
    def login_url(self):
        return '/login'

    @property
    def login_handler(self):
        if config.oauth_provider == 'github':
            return GithubLoginHandler

    @property
    def logout_handler(self):
        return
