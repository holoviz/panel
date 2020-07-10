import codecs
import json
import logging
import os
import pkg_resources
import re

from urllib.parse import urlencode

import tornado

from bokeh.server.auth_provider import AuthProvider
from tornado.auth import OAuth2Mixin
from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat

from .config import config
from .io import state
from .util import base64url_encode, base64url_decode

log = logging.getLogger(__name__)


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

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }

    _EXTRA_TOKEN_PARAMS = {}

    _SCOPE = None

    x_site_token = 'application'

    async def get_authenticated_user(self, redirect_uri, client_id, state,
                                     client_secret=None, code=None):
        """ Fetches the authenticated user
        :param redirect_uri: the redirect URI
        :param client_id: the client ID
        :param state: the unguessable random string to protect against
                      cross-site request forgery attacks
        :param client_secret: the client secret
        :param code: the response code from the server
        """
        if code:
            return await self._fetch_access_token(
                code,
                redirect_uri,
                client_id,
                client_secret
            )

        params = {
            'redirect_uri': redirect_uri,
            'client_id':    client_id,
            'client_secret': client_secret,
            'extra_params': {
                'state': state,
            },
        }
        if self._SCOPE is not None:
            params['scope'] = self._SCOPE
        if 'scope' in config.oauth_extra_params:
            params['scope'] = config.oauth_extra_params['scope']
        log.debug("%s making authorize request" % type(self).__name__)
        self.authorize_redirect(**params)

    async def _fetch_access_token(self, code, redirect_uri, client_id, client_secret):
        """
        Fetches the access token.

        Arguments
        ----------
        code:
          The response code from the server
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
        if not client_secret:
            raise ValueError('The client secret is undefined.')

        log.debug("%s making access token request." % type(self).__name__)

        params = {
            'code':          code,
            'redirect_uri':  redirect_uri,
            'client_id':     client_id,
            'client_secret': client_secret,
            **self._EXTRA_TOKEN_PARAMS
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
                'body': body
            }
            if response.error:
                data['error'] = response.error
            return self._on_error(**data)

        user_response = await http.fetch(
            '{}{}'.format(
                self._OAUTH_USER_URL, body['access_token']
            ),
            headers=self._API_BASE_HEADERS
        )

        user = decode_response_body(user_response)

        if not user:
            return

        log.debug("%s received user information." % type(self).__name__)
        return self._on_auth(user, body['access_token'])

    async def get(self):
        log.debug("%s received login request" % type(self).__name__)
        if config.oauth_redirect_uri:
            redirect_uri = config.oauth_redirect_uri
        else:
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
        if next_code and 'code=' in next_code:
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
                'code':  code,
                'state': state
            })
            user = await self.get_authenticated_user(**params)
            if user is None:
                raise tornado.web.HTTPError(403)
            log.debug("%s authorized user, redirecting to app." % type(self).__name__)
            self.redirect('/')
        else:
            # Redirect for user authentication
            await self.get_authenticated_user(**params)

    def _on_auth(self, user_info, access_token):
        user_key = config.oauth_jwt_user or self._USER_KEY
        user = user_info[user_key]
        self.set_secure_cookie('user', user)
        id_token = base64url_encode(json.dumps(user_info))
        if state.encryption:
            access_token = state.encryption.encrypt(access_token.encode('utf-8'))
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
        self.set_secure_cookie('access_token', access_token)
        self.set_secure_cookie('id_token', id_token)
        return user

    def _on_error(self, **kwargs):
        self.clear_all_cookies()
        name = type(self).__name__.replace('LoginHandler', '')
        raise tornado.web.HTTPError(500, '%s authentication failed' % name)


class GithubLoginHandler(OAuthLoginHandler, OAuth2Mixin):
    """GitHub OAuth2 Authentication
    To authenticate with GitHub, first register your application at
    https://github.com/settings/applications/new to get the client ID and
    secret.
    """

    _EXTRA_AUTHORIZE_PARAMS = {}

    _OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
    _OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    _OAUTH_USER_URL = 'https://api.github.com/user?access_token='

    _USER_KEY = 'login'


class BitbucketLoginHandler(OAuthLoginHandler, OAuth2Mixin):

    _API_BASE_HEADERS = {
        "Accept": "application/json",
    }

    _EXTRA_TOKEN_PARAMS = {
        'grant_type':    'authorization_code'
    }

    _OAUTH_ACCESS_TOKEN_URL = "https://bitbucket.org/site/oauth2/access_token"
    _OAUTH_AUTHORIZE_URL = "https://bitbucket.org/site/oauth2/authorize"
    _OAUTH_USER_URL = "https://api.bitbucket.org/2.0/user?access_token="

    _USER_KEY = 'username'


class GitLabLoginHandler(OAuthLoginHandler, OAuth2Mixin):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
    }

    _EXTRA_TOKEN_PARAMS = {
        'grant_type':    'authorization_code'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://{0}/oauth/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://{0}/oauth/authorize'
    _OAUTH_USER_URL_ = 'https://{0}/api/v4/user'

    _USER_KEY = 'username'

    @property
    def _OAUTH_ACCESS_TOKEN_URL(self):
        url = config.oauth_extra_params.get('url', 'gitlab.com')
        return self._OAUTH_ACCESS_TOKEN_URL_.format(url)

    @property
    def _OAUTH_AUTHORIZE_URL(self):
        url = config.oauth_extra_params.get('url', 'gitlab.com')
        return self._OAUTH_AUTHORIZE_URL_.format(url)

    @property
    def _OAUTH_USER_URL(self):
        url = config.oauth_extra_params.get('url', 'gitlab.com')
        return self._OAUTH_USER_URL_.format(url)

    async def _fetch_access_token(self, code, redirect_uri, client_id, client_secret):
        """
        Fetches the access token.

        Arguments
        ----------
        code:
          The response code from the server
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
        if not client_secret:
            raise ValueError('The client secret is undefined.')

        log.debug("%s making access token request." % type(self).__name__)

        http = self.get_auth_http_client()

        params = {
            'code':          code,
            'redirect_uri':  redirect_uri,
            'client_id':     client_id,
            'client_secret': client_secret,
            **self._EXTRA_TOKEN_PARAMS
        }

        url = url_concat(self._OAUTH_ACCESS_TOKEN_URL, params)

        # Request the access token.
        response = await http.fetch(
            url,
            method='POST',
            body='',
            headers=self._API_BASE_HEADERS
        )

        body = decode_response_body(response)

        if not body:
            return

        if 'access_token' not in body:
            data = {
                'code': response.code,
                'body': body
            }
            if response.error:
                data['error'] = response.error
            return self._on_error(**data)

        log.debug("%s granted access_token." % type(self).__name__)

        headers = dict(self._API_BASE_HEADERS, **{
            "Authorization": "Bearer {}".format(body['access_token']),
        })

        user_response = await http.fetch(
            self._OAUTH_USER_URL,
            method="GET",
            headers=headers
        )

        user = decode_response_body(user_response)

        if not user:
            return

        log.debug("%s received user information." % type(self).__name__)

        return self._on_auth(user, body['access_token'])



class OAuthIDTokenLoginHandler(OAuthLoginHandler):

    _API_BASE_HEADERS = {
        'Content-Type':
        'application/x-www-form-urlencoded; charset=UTF-8'
    }

    _EXTRA_AUTHORIZE_PARAMS = {
        'grant_type':    'authorization_code'
    }

    async def _fetch_access_token(self, code, redirect_uri, client_id, client_secret):
        """
        Fetches the access token.

        Arguments
        ----------
        code:
          The response code from the server
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
        if not client_secret:
            raise ValueError('The client secret are undefined.')

        log.debug("%s making access token request." % type(self).__name__)

        http = self.get_auth_http_client()

        params = {
            'code':          code,
            'redirect_uri':  redirect_uri,
            'client_id':     client_id,
            'client_secret': client_secret,
            **self._EXTRA_AUTHORIZE_PARAMS
        }

        data = urlencode(
            params, doseq=True, encoding='utf-8', safe='=')

        # Request the access token.
        req = HTTPRequest(
            self._OAUTH_ACCESS_TOKEN_URL,
            method="POST",
            headers=self._API_BASE_HEADERS,
            body=data
        )

        response = await http.fetch(req)
        decoded_body = decode_response_body(response)

        if 'access_token' not in decoded_body:
            data = {
                'code': response.code,
                'body': decoded_body
            }

            if response.error:
                data['error'] = response.error
            return self._on_error(**data)

        log.debug("%s granted access_token." % type(self).__name__)

        access_token = decoded_body['access_token']
        id_token = decoded_body['id_token']
        return self._on_auth(id_token, access_token)

    def _on_auth(self, id_token, access_token):
        signing_input, _ = id_token.encode('utf-8').rsplit(b".", 1)
        _, payload_segment = signing_input.split(b".", 1)
        decoded = json.loads(base64url_decode(payload_segment).decode('utf-8'))
        user_key = config.oauth_jwt_user or self._USER_KEY
        user = decoded[user_key]
        self.set_secure_cookie('user', user)
        if state.encryption:
            access_token = state.encryption.encrypt(access_token.encode('utf-8'))
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
        self.set_secure_cookie('access_token', access_token)
        self.set_secure_cookie('id_token', id_token)
        return user


class AzureAdLoginHandler(OAuthIDTokenLoginHandler, OAuth2Mixin):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/authorize'
    _OAUTH_USER_URL_ = ''

    _USER_KEY = 'unique_name'

    @property
    def _OAUTH_ACCESS_TOKEN_URL(self):
        tenant = os.environ.get('AAD_TENANT_ID', config.oauth_extra_params.get('tenant', 'common'))
        return self._OAUTH_ACCESS_TOKEN_URL_.format(tenant=tenant)

    @property
    def _OAUTH_AUTHORIZE_URL(self):
        tenant = os.environ.get('AAD_TENANT_ID', config.oauth_extra_params.get('tenant', 'common'))
        return self._OAUTH_AUTHORIZE_URL_.format(tenant=tenant)

    @property
    def _OAUTH_USER_URL(self):
        return self._OAUTH_USER_URL_.format(**config.oauth_extra_params)


class GoogleLoginHandler(OAuthIDTokenLoginHandler, OAuth2Mixin):

    _API_BASE_HEADERS = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }

    _OAUTH_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    _OAUTH_ACCESS_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"

    _SCOPE = ['profile', 'email']

    _USER_KEY = 'email'


class LogoutHandler(tornado.web.RequestHandler):

    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("id_token")
        self.clear_cookie("access_token")
        self.redirect("/")


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
    def logout_url(self):
        return "/logout"

    @property
    def logout_handler(self):
        return LogoutHandler


AUTH_PROVIDERS = {
    'azure': AzureAdLoginHandler,
    'bitbucket': BitbucketLoginHandler,
    'google': GoogleLoginHandler,
    'github': GithubLoginHandler,
    'gitlab': GitLabLoginHandler,
}

# Populate AUTH Providers from external extensions
for entry_point in pkg_resources.iter_entry_points('panel.auth'):
    AUTH_PROVIDERS[entry_point.name] = entry_point.resolve()

config.param.objects(False)['_oauth_provider'].objects = list(AUTH_PROVIDERS.keys())
