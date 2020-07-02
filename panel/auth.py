import codecs
import json
import pkg_resources
import requests
import re
import jwt
import urllib
import uuid

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


class OAuthLoginHandler(tornado.web.RequestHandler):

    x_site_token = 'application'

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
                client_secret
            )
            return

        params = {
            'redirect_uri': redirect_uri,
            'client_id':    client_id,
            'client_secret': client_secret,
            'extra_params': {
                'state': state
            }
        }

        self.authorize_redirect(**params)

    def _fetch_access_token(self, code, success_callback, error_callback,
                            redirect_uri, client_id, client_secret):
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
            **self._EXTRA_AUTHORIZE_PARAMS
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

        print(params)
        # Request the access token.
        http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            on_authenticate,
            method='POST',
            body=urlencode(params),
            headers=self._API_BASE_HEADERS
        )

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
        # Some OAuth2 backends do not correctly return code
        next_code = self.get_argument('next', None)
        if 'code=' in next_code:
            url_params = next_code[next_code.index('code='):].replace('code=', '').split('&')
            code = url_params[0]
            state = [p.replace('state=', '') for p in url_params if p.startswith('state')]
            state = state[0] if state else None
        else:
            code = self.get_argument('code', None)
            state = self.get_argument('state', None)
        # Seek the authorization
        if code:
            # For security reason, the state value (cross-site token) will be
            # retrieved from the query string.
            params.update({
                'client_secret': config.oauth_secret,
                'success_callback': self._on_auth,
                'error_callback': self._on_error,
                'code':  code,
                'state': state
            })
            yield self.get_authenticated_user(**params)
            return
        # Redirect for user authentication
        self.get_authenticated_user(**params)

    def _on_auth(self, user, access_token):
        print(user)
        self.set_cookie('user', str(user['id']))
        self.set_secure_cookie('access_token', access_token)
        self.redirect('/')

    def _on_error(self, user):
        self.clear_all_cookies()
        raise tornado.web.HTTPError(500, 'Github authentication failed')



class AzureAdMixin(OAuth2Mixin):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }

    _EXTRA_AUTHORIZE_PARAMS = {
        'grant_type':    'authorization_code'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/authorize'
    _OAUTH_USER_URL_ = ''

    @property
    def _OAUTH_ACCESS_TOKEN_URL(self):
        return self._OAUTH_ACCESS_TOKEN_URL_.format(**config.oauth_extra_params)

    @property
    def _OAUTH_AUTHORIZE_URL(self):
        return self._OAUTH_AUTHORIZE_URL_.format(**config.oauth_extra_params)

    @property
    def _OAUTH_USER_URL(self):
        return self._OAUTH_USER_URL_.format(**config.oauth_extra_params)

    def _fetch_access_token(self, code, success_callback, error_callback,
                            redirect_uri, client_id, client_secret):
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
            'redirect_uri':  redirect_uri,
            'client_id':     client_id,
            'client_secret': client_secret,
            'grant_type':    'authorization_code'
        }

        # Request the access token.
        response = requests.post(
            self._OAUTH_ACCESS_TOKEN_URL,
            data=params
        )

        if not resp_json:
            return

        if 'access_token' not in resp_json:
            data = {
                'code': response.code,
                'body': resp_json
            }

            if response.error:
                data['error'] = response.error

            error_callback(**data)
            return

        access_token = resp_json['access_token']
        id_token = resp_json['id_token']
        decoded = jwt.decode(id_token, verify=False)
        success_callback(decoded, access_token)

    def _on_auth(self, id_token, access_token):
        self.set_cookie('user_family_name', id_token['family_name'])
        self.set_cookie('user_given_name', id_token['given_name'])
        self.set_cookie('user_ipaddr', id_token['ipaadr'])
        self.set_cookie('user_unique_name', id_token['unique_name'])
        self.set_cookie('user_name', id_token['name'])
        self.set_cookie('user_email', id_token['email'])
        self.set_cookie('user', id_token['email'])
        self.set_secret_cookie('id_token', id_token)
        self.set_secret_cookie('access_token', id_token)
        self.redirect('/')


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

    _EXTRA_AUTHORIZE_PARAMS = {}

    _OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
    _OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    _OAUTH_USER_URL = 'https://api.github.com/user?access_token='


class GithubLoginHandler(OAuthLoginHandler, GithubMixin):
    """
    """


class AzureAdLoginHandler(AzureAdMixin, OAuthLoginHandler):
    """
    """


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
        return AUTH_PROVIDERS[config.oauth_provider]

    @property
    def logout_handler(self):
        return


AUTH_PROVIDERS = {
    'github': GithubLoginHandler,
    'azure': AzureAdLoginHandler
}

# Populate AUTH Providers from external extensions
for entry_point in pkg_resources.iter_entry_points('panel.auth'):
    AUTH_PROVIDERS[entry_point.name] = entry_point.resolve()

config.param.objects(False)['_oauth_provider'].objects = list(AUTH_PROVIDERS.keys())
