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
from .io import state
from .util import base64url_encode



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
    return body


class OAuthLoginHandler(tornado.web.RequestHandler):

    x_site_token = 'application'

    async def get_authenticated_user(self, redirect_uri, client_id, state,
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
            await self._fetch_access_token(
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

    async def _fetch_access_token(self, code, success_callback, error_callback,
                                  redirect_uri, client_id, client_secret):
        """
        Fetches the access token.

        Arguments
        ----------
        code:
          The response code from the server
        success_callback:
          The  callback used when fetching the access token succeeds
        error_callback:
          The callback used when fetching the access token fails
        redirect_uri:
          The redirect URI
        client_id:
          The client ID
        client_secret:
          The client secret
        state:
          The unguessable random string to protect against cross-site
          request forgery attacks
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

        http = self.get_auth_http_client()


        # Request the access token.
        response = await http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            method='POST',
            body=urlencode(params),
            headers=self._API_BASE_HEADERS
        )

        body = decode_response_body(response)

        if not body:
            return

        if 'access_token' not in body:
            data = {
                'code': response.code,
                'body': decoded_body
            }
            if response.error:
                data['error'] = response.error
            error_callback(**data)

        user_response = await http.fetch(
            '{}{}'.format(
                self._OAUTH_USER_URL, body['access_token']
            ),
            headers=self._API_BASE_HEADERS
        )

        user = decode_response_body(user_response)

        if not user:
            return
        success_callback(user, body['access_token'])

    async def get(self):
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
            await self.get_authenticated_user(**params)
            return
        # Redirect for user authentication
        await self.get_authenticated_user(**params)



class AzureAdLoginHandler(OAuthLoginHandler, OAuth2Mixin):

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

    async def _fetch_access_token(
        self, code, success_callback, error_callback, redirect_uri,
        client_id, client_secret):
        """
        Fetches the access token.

        Arguments
        ----------
        code:
          The response code from the server
        success_callback:
          The  callback used when fetching the access token succeeds
        error_callback:
          The callback used when fetching the access token fails
        redirect_uri:
          The redirect URI
        client_id:
          The client ID
        client_secret:
          The client secret
        state:
          The unguessable random string to protect against cross-site
          request forgery attacks
        """
        if not (client_secret and success_callback and error_callback):
            raise ValueError(
                'The client secret or any callbacks are undefined.'
            )

        http = self.get_auth_http_client()

        params = {
            'code':          code,
            'redirect_uri':  redirect_uri,
            'client_id':     client_id,
            'client_secret': client_secret,
            'grant_type':    'authorization_code'
        }

        # Request the access token.
        response = await http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            method='POST',
            data=urlencode(params),
            headers=self._API_BASE_HEADERS
        )

        decoded_body = decode_response_body(response)

        if 'access_token' not in decoded_body:
            data = {
                'code': response.code,
                'body': resp_json
            }

            if response.error:
                data['error'] = response.error
            error_callback(**data)
            return

        access_token = decoded_body['access_token']
        id_token = decoded_body['id_token']
        success_callback(id_token, access_token)

    def _on_auth(self, id_token, access_token):
        decoded = jwt.decode(id_token, verify=False)
        self.set_secure_cookie('user', decoded['email'])
        if state.encryption:
            access_token = state.encryption.encrypt(access_token.encode('utf-8'))
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
        self.set_secure_cookie('access_token', access_token)
        self.set_secure_cookie('id_token', id_token)
        self.redirect('/')

    def _on_error(self, user):
        self.clear_all_cookies()
        raise tornado.web.HTTPError(500, 'Github authentication failed')



class GithubLoginHandler(OAuthLoginHandler, OAuth2Mixin):
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

    def _on_auth(self, user_info, access_token):
        self.set_secure_cookie('user', user_info['login'])
        id_token = base64url_encode(json.dumps(user_info))
        if state.encryption:
            access_token = state.encryption.encrypt(access_token.encode('utf-8'))
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
        self.set_secure_cookie('access_token', access_token)
        self.set_secure_cookie('id_token', id_token)
        self.redirect('/')

    def _on_error(self, user):
        self.clear_all_cookies()
        raise tornado.web.HTTPError(500, 'Azure AD authentication failed')



class OAuthProvider(AuthProvider):

    @property
    def get_user(self):
        def get_user(request_handler):
            return request_handler.get_secure_cookie("user")
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
    'azure': AzureAdLoginHandler,
    'github': GithubLoginHandler,
}

# Populate AUTH Providers from external extensions
for entry_point in pkg_resources.iter_entry_points('panel.auth'):
    AUTH_PROVIDERS[entry_point.name] = entry_point.resolve()

config.param.objects(False)['_oauth_provider'].objects = list(AUTH_PROVIDERS.keys())
