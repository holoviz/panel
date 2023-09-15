import base64
import codecs
import json
import logging
import os
import re
import urllib.parse as urlparse
import uuid

import tornado

from bokeh.server.auth_provider import AuthProvider
from tornado.auth import OAuth2Mixin
from tornado.httpclient import HTTPError, HTTPRequest
from tornado.httputil import url_concat
from tornado.web import RequestHandler

from .config import config
from .entry_points import entry_points_for
from .io import state
from .io.resources import (
    BASIC_LOGIN_TEMPLATE, CDN_DIST, ERROR_TEMPLATE, LOGOUT_TEMPLATE, _env,
)
from .util import base64url_decode, base64url_encode

log = logging.getLogger(__name__)

STATE_COOKIE_NAME = 'panel-oauth-state'


def decode_response_body(response):
    """
    Decodes the JSON-format response body

    Arguments
    ---------
    response: tornado.httpclient.HTTPResponse

    Returns
    -------
    Decoded response content
    """
    # Fix GitHub response.
    try:
        body = codecs.decode(response.body, 'ascii')
    except Exception:
        body = codecs.decode(response.body, 'utf-8')
    body = re.sub('"', '\"', body)
    body = re.sub("'", '"', body)
    body = json.loads(body)
    return body


def decode_id_token(id_token):
    """
    Decodes a signed ID JWT token.
    """
    signing_input, _ = id_token.encode('utf-8').rsplit(b".", 1)
    _, payload_segment = signing_input.split(b".", 1)
    return json.loads(base64url_decode(payload_segment).decode('utf-8'))


def extract_urlparam(args, key):
    """
    Extracts a request argument from a urllib.parse.parse_qs dict.
    """
    return args.get(key, args.get(f'/?{key}', [None]))[0]


def _serialize_state(state):
    """Serialize OAuth state to a base64 string after passing through JSON"""
    json_state = json.dumps(state)
    return base64.urlsafe_b64encode(json_state.encode('utf8')).decode('ascii')


def _deserialize_state(b64_state):
    """Deserialize OAuth state as serialized in _serialize_state"""
    if isinstance(b64_state, str):
        b64_state = b64_state.encode('ascii')
    try:
        json_state = base64.urlsafe_b64decode(b64_state).decode('utf8')
    except ValueError:
        log.error("Failed to b64-decode state: %r", b64_state)
        return {}
    try:
        return json.loads(json_state)
    except ValueError:
        log.error("Failed to json-decode state: %r", json_state)
        return {}


class OAuthLoginHandler(tornado.web.RequestHandler):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }

    _access_token_header = None

    _EXTRA_TOKEN_PARAMS = {}

    _SCOPE = None

    _state_cookie = None

    _error_template = ERROR_TEMPLATE

    async def get_authenticated_user(self, redirect_uri, client_id, state,
                                     client_secret=None, code=None):
        """
        Fetches the authenticated user

        Arguments
        ---------
        redirect_uri: (str)
          The OAuth redirect URI
        client_id: (str)
          The OAuth client ID
        state: (str)
          The unguessable random string to protect against
          cross-site request forgery attacks
        client_secret: (str, optional)
          The client secret
        code: (str, optional)
          The response code from the server
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
            'response_type': 'code',
            'extra_params': {
                'state': state,
            },
        }
        if self._SCOPE is not None:
            params['scope'] = self._SCOPE
        if 'scope' in config.oauth_extra_params:
            params['scope'] = config.oauth_extra_params['scope']
        log.debug("%s making authorize request", type(self).__name__)
        self.authorize_redirect(**params)

    async def _fetch_access_token(self, code, redirect_uri, client_id, client_secret):
        """
        Fetches the access token.

        Arguments
        ---------
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

        log.debug("%s making access token request.", type(self).__name__)
        params = {
            'code':          code,
            'redirect_uri':  redirect_uri,
            'client_id':     client_id,
            'client_secret': client_secret,
            **self._EXTRA_TOKEN_PARAMS
        }

        http = self.get_auth_http_client()

        # Request the access token.
        req = HTTPRequest(
            self._OAUTH_ACCESS_TOKEN_URL,
            method='POST',
            body=urlparse.urlencode(params),
            headers=self._API_BASE_HEADERS
        )
        try:
            response = await http.fetch(req)
        except HTTPError as e:
            return self._on_error(e.response)

        body = decode_response_body(response)

        if not body:
            return

        if 'access_token' not in body:
            return self._on_error(response, body)

        user_headers = dict(self._API_BASE_HEADERS)
        if self._access_token_header:
            user_url = self._OAUTH_USER_URL
            user_headers['Authorization'] = self._access_token_header.format(
                body['access_token']
            )
        else:
            user_url = '{}{}'.format(self._OAUTH_USER_URL, body['access_token'])

        user_response = await http.fetch(user_url, headers=user_headers)
        user = decode_response_body(user_response)

        if not user:
            return

        log.debug("%s received user information.", type(self).__name__)
        return self._on_auth(user, body['access_token'], body.get('refresh_token'))

    def get_state_cookie(self):
        """Get OAuth state from cookies
        To be compared with the value in redirect URL
        """
        if self._state_cookie is None:
            self._state_cookie = (
                self.get_secure_cookie(STATE_COOKIE_NAME, max_age_days=config.oauth_expiry) or b''
            ).decode('utf8', 'replace')
            self.clear_cookie(STATE_COOKIE_NAME)
        return self._state_cookie

    def set_state_cookie(self, state):
        self.set_secure_cookie(
            STATE_COOKIE_NAME, state, expires_days=config.oauth_expiry, httponly=True
        )

    def get_state(self):
        next_url = original_next_url = self.get_argument('next', self.request.uri.replace('/login', ''))
        if next_url:
            # avoid browsers treating \ as /
            next_url = next_url.replace('\\', urlparse.quote('\\'))
            # disallow hostname-having urls,
            # force absolute path redirect
            urlinfo = urlparse.urlparse(next_url)
            next_url = urlinfo._replace(
                scheme='', netloc='', path='/' + urlinfo.path.lstrip('/')
            ).geturl()
            if next_url != original_next_url:
                log.warning(
                    "Ignoring next_url %r, using %r", original_next_url, next_url
                )
        return _serialize_state(
            {'state_id': uuid.uuid4().hex, 'next_url': next_url or '/'}
        )

    async def get(self):
        log.debug("%s received login request", type(self).__name__)
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
        }

        # Some OAuth2 backends do not correctly return code
        next_arg = self.get_argument('next', {})
        if next_arg:
            next_arg = urlparse.parse_qs(next_arg)
            next_arg = {arg.split('?')[-1]: value for arg, value in next_arg.items()}
        code = self.get_argument('code', extract_urlparam(next_arg, 'code'))
        url_state = self.get_argument('state', extract_urlparam(next_arg, 'state'))

        # Handle authentication error
        error = self.get_argument('error', extract_urlparam(next_arg, 'error'))

        if error is not None:
            error_msg = self.get_argument(
                'error_description', extract_urlparam(next_arg, 'error_description'))
            if not error_msg:
                error_msg = error
            log.error(
                "%s failed to authenticate with following error: %s",
                type(self).__name__, error
            )
            self.set_header("Content-Type", 'text/html')
            self.write(self._error_template.render(
                npm_cdn=config.npm_cdn,
                title='Panel: Authentication Error',
                error_type='Authentication Error',
                error=error,
                error_msg=error_msg
            ))
            return

        # Seek the authorization
        cookie_state = self.get_state_cookie()
        if code:
            if cookie_state != url_state:
                log.warning("OAuth state mismatch: %s != %s", cookie_state, url_state)
                raise HTTPError(400, "OAuth state mismatch")

            state = _deserialize_state(url_state)
            # For security reason, the state value (cross-site token) will be
            # retrieved from the query string.
            params.update({
                'client_secret': config.oauth_secret,
                'code':  code,
                'state': url_state
            })
            user = await self.get_authenticated_user(**params)
            if user is None:
                raise HTTPError(403)
            log.debug("%s authorized user, redirecting to app.", type(self).__name__)
            self.redirect(state.get('next_url', '/'))
        else:
            # Redirect for user authentication
            params['state'] = state = self.get_state()
            self.set_state_cookie(state)
            await self.get_authenticated_user(**params)

    def _on_auth(self, user_info, access_token, refresh_token=None):
        user_key = config.oauth_jwt_user or self._USER_KEY
        user = user_info[user_key]
        self.set_secure_cookie('user', user, expires_days=config.oauth_expiry)
        id_token = base64url_encode(json.dumps(user_info))
        if state.encryption:
            access_token = state.encryption.encrypt(access_token.encode('utf-8'))
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
            if refresh_token:
                refresh_token = state.encryption.encrypt(refresh_token.encode('utf-8'))
        self.set_secure_cookie('access_token', access_token, expires_days=config.oauth_expiry)
        self.set_secure_cookie('id_token', id_token, expires_days=config.oauth_expiry)
        if refresh_token:
            self.set_secure_cookie('refresh_token', refresh_token, expires_days=config.oauth_expiry)
        return user

    def _on_error(self, response, body=None):
        self.clear_all_cookies()
        try:
            body = body or decode_response_body(response)
        except json.decoder.JSONDecodeError:
            body = body
        provider = self.__class__.__name__.replace('LoginHandler', '')
        if response.error:
            log.error(f"{provider} OAuth provider returned a {response.error} "
                      f"error. The full response was: {body}")
        else:
            log.warning(f"{provider} OAuth provider failed to fully "
                        f"authenticate returning the following response:"
                        f"{body}.")
        raise HTTPError(500, f"{provider} authentication failed {body}")


class GenericLoginHandler(OAuthLoginHandler, OAuth2Mixin):

    _access_token_header = 'Bearer {}'

    _EXTRA_TOKEN_PARAMS = {
        'grant_type':    'authorization_code'
    }

    @property
    def _OAUTH_ACCESS_TOKEN_URL(self):
        return config.oauth_extra_params.get('TOKEN_URL', os.environ.get('PANEL_OAUTH_TOKEN_URL'))

    @property
    def _OAUTH_AUTHORIZE_URL(self):
        return config.oauth_extra_params.get('AUTHORIZE_URL', os.environ.get('PANEL_OAUTH_AUTHORIZE_URL'))

    @property
    def _OAUTH_USER_URL(self):
        return config.oauth_extra_params.get('USER_URL', os.environ.get('PANEL_OAUTH_USER_URL'))

    @property
    def _SCOPE(self):
        if 'PANEL_OAUTH_SCOPE' not in os.environ:
            return ['openid', 'email']
        return [scope for scope in os.environ['PANEL_OAUTH_SCOPE'].split(',')]

    @property
    def _USER_KEY(self):
        return config.oauth_extra_params.get('USER_KEY', os.environ.get('PANEL_USER_KEY', 'email'))


class GithubLoginHandler(OAuthLoginHandler, OAuth2Mixin):
    """GitHub OAuth2 Authentication
    To authenticate with GitHub, first register your application at
    https://github.com/settings/applications/new to get the client ID and
    secret.
    """

    _EXTRA_AUTHORIZE_PARAMS = {}

    _OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
    _OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    _OAUTH_USER_URL = 'https://api.github.com/user'

    _access_token_header = 'token {}'

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


class Auth0Handler(OAuthLoginHandler, OAuth2Mixin):

    _EXTRA_AUTHORIZE_PARAMS = {
        'subdomain'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://{0}.auth0.com/oauth/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://{0}.auth0.com/authorize'
    _OAUTH_USER_URL_ = 'https://{0}.auth0.com/userinfo?access_token='

    @property
    def _OAUTH_ACCESS_TOKEN_URL(self):
        url = config.oauth_extra_params.get('subdomain', 'example')
        return self._OAUTH_ACCESS_TOKEN_URL_.format(url)

    @property
    def _OAUTH_AUTHORIZE_URL(self):
        url = config.oauth_extra_params.get('subdomain', 'example')
        return self._OAUTH_AUTHORIZE_URL_.format(url)

    @property
    def _OAUTH_USER_URL(self):
        url = config.oauth_extra_params.get('subdomain', 'example')
        return self._OAUTH_USER_URL_.format(url)

    _USER_KEY = 'email'

    _EXTRA_TOKEN_PARAMS = {
        'grant_type':    'authorization_code'
    }


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

        log.debug("%s making access token request.", type(self).__name__)

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
        req = HTTPRequest(
            url,
            method="POST",
            headers=self._API_BASE_HEADERS,
            body=''
        )
        try:
            response = await http.fetch(req)
        except HTTPError as e:
            return self._on_error(e.response)

        body = decode_response_body(response)

        if not body:
            return

        if 'access_token' not in body:
            return self._on_error(response, body)

        log.debug("%s granted access_token.", type(self).__name__)

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

        log.debug("%s received user information.", type(self).__name__)

        return self._on_auth(user, body['access_token'])



class OAuthIDTokenLoginHandler(OAuthLoginHandler):

    _API_BASE_HEADERS = {
        'Content-Type':
        'application/x-www-form-urlencoded; charset=UTF-8'
    }

    _EXTRA_AUTHORIZE_PARAMS = {
        'grant_type': 'authorization_code'
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

        log.debug("%s making access token request.", type(self).__name__)

        http = self.get_auth_http_client()

        params = {
            'code':          code,
            'redirect_uri':  redirect_uri,
            'client_id':     client_id,
            'client_secret': client_secret,
            **self._EXTRA_AUTHORIZE_PARAMS
        }

        data = urlparse.urlencode(
            params, doseq=True, encoding='utf-8', safe='=')

        # Request the access token.
        req = HTTPRequest(
            self._OAUTH_ACCESS_TOKEN_URL,
            method="POST",
            headers=self._API_BASE_HEADERS,
            body=data
        )

        try:
            response = await http.fetch(req)
        except HTTPError as e:
            return self._on_error(e.response)

        body = decode_response_body(response)

        if 'access_token' not in body:
            return self._on_error(response, body)

        log.debug("%s granted access_token.", type(self).__name__)

        access_token = body['access_token']
        id_token = body['id_token']
        return self._on_auth(id_token, access_token, body.get('refresh_token'))

    def _on_auth(self, id_token, access_token, refresh_token=None):
        decoded = decode_id_token(id_token)
        user_key = config.oauth_jwt_user or self._USER_KEY
        if user_key in decoded:
            user = decoded[user_key]
        else:
            log.error("%s token payload did not contain expected %r.",
                      type(self).__name__, user_key)
            raise HTTPError(400, "OAuth token payload missing user information")
        self.set_secure_cookie('user', user, expires_days=config.oauth_expiry)
        if state.encryption:
            access_token = state.encryption.encrypt(access_token.encode('utf-8'))
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
            if refresh_token:
                refresh_token = state.encryption.encrypt(refresh_token.encode('utf-8'))
        self.set_secure_cookie('access_token', access_token, expires_days=config.oauth_expiry)
        self.set_secure_cookie('id_token', id_token, expires_days=config.oauth_expiry)
        if refresh_token:
            self.set_secure_cookie('refresh_token', refresh_token, expires_days=config.oauth_expiry)
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


class AzureAdV2LoginHandler(OAuthIDTokenLoginHandler, OAuth2Mixin):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize'
    _OAUTH_USER_URL_ = ''

    _USER_KEY = 'email'
    _SCOPE = ['openid', 'email', 'profile']

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


class OktaLoginHandler(OAuthIDTokenLoginHandler, OAuth2Mixin):
    """Okta OAuth2 Authentication

    To authenticate with Okta you first need to set up and configure
    in the Okta developer console.
    """

    _EXTRA_TOKEN_PARAMS = {
        'grant_type':    'authorization_code',
        'response_type': 'code,token,id_token'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://{0}/oauth2/{1}/v1/token'
    _OAUTH_ACCESS_TOKEN_URL__ = 'https://{0}/oauth2/v1/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://{0}/oauth2/{1}/v1/authorize'
    _OAUTH_AUTHORIZE_URL__ = 'https://{0}/oauth2/v1/authorize'
    _OAUTH_USER_URL_ = 'https://{0}/oauth2/{1}/v1/userinfo?access_token='
    _OAUTH_USER_URL__ = 'https://{0}/oauth2/v1/userinfo?access_token='

    _USER_KEY = 'email'

    _SCOPE = ['openid', 'email', 'profile']

    @property
    def _OAUTH_ACCESS_TOKEN_URL(self):
        url = config.oauth_extra_params.get('url', 'okta.com')
        server = config.oauth_extra_params.get('server', 'default')
        if server:
            return self._OAUTH_ACCESS_TOKEN_URL_.format(url, server)
        else:
            return self._OAUTH_ACCESS_TOKEN_URL__.format(url)

    @property
    def _OAUTH_AUTHORIZE_URL(self):
        url = config.oauth_extra_params.get('url', 'okta.com')
        server = config.oauth_extra_params.get('server', 'default')
        if server:
            return self._OAUTH_AUTHORIZE_URL_.format(url, server)
        else:
            return self._OAUTH_AUTHORIZE_URL__.format(url)

    @property
    def _OAUTH_USER_URL(self):
        url = config.oauth_extra_params.get('url', 'okta.com')
        server = config.oauth_extra_params.get('server', 'default')
        if server:
            return self._OAUTH_USER_URL_.format(url, server)
        else:
            return self._OAUTH_USER_URL__.format(url, server)


class GoogleLoginHandler(OAuthIDTokenLoginHandler, OAuth2Mixin):

    _API_BASE_HEADERS = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }

    _OAUTH_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    _OAUTH_ACCESS_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"

    _SCOPE = ['profile', 'email']

    _USER_KEY = 'email'


class LogoutHandler(tornado.web.RequestHandler):

    _logout_handler = LOGOUT_TEMPLATE

    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("id_token")
        self.clear_cookie("access_token")
        self.clear_cookie(STATE_COOKIE_NAME)
        html = self._logout_template.render(PANEL_CDN=CDN_DIST)
        self.write(html)


class OAuthProvider(AuthProvider):

    def __init__(self, error_template=None, logout_template=None):
        if error_template is None:
            self._error_template = ERROR_TEMPLATE
        else:
            with open(error_template) as f:
                self._error_template = _env.from_string(f.read())
        if logout_template is None:
            self._logout_template = LOGOUT_TEMPLATE
        else:
            with open(logout_template) as f:
                self._logout_template = _env.from_string(f.read())
        super().__init__()

    @property
    def get_user(self):
        def get_user(request_handler):
            return request_handler.get_secure_cookie("user", max_age_days=config.oauth_expiry)
        return get_user

    @property
    def login_url(self):
        return '/login'

    @property
    def login_handler(self):
        handler = AUTH_PROVIDERS[config.oauth_provider]
        if self._error_template:
            handler._error_template = self._error_template
        return handler

    @property
    def logout_url(self):
        return '/logout'

    @property
    def logout_handler(self):
        if self._logout_template:
            LogoutHandler._logout_template = self._logout_template
        return LogoutHandler


class BasicLoginHandler(RequestHandler):

    def get(self):
        try:
            errormessage = self.get_argument("error")
        except Exception:
            errormessage = ""

        next_url = self.get_argument('next', None)
        if next_url:
            self.set_cookie("next_url", next_url)
        html = self._basic_login_template.render(
            errormessage=errormessage,
            PANEL_CDN=CDN_DIST
        )
        self.write(html)

    def _validate(self, username, password):
        if 'basic_auth' in state._server_config.get(self.application, {}):
            auth_info = state._server_config[self.application]['basic_auth']
        else:
            auth_info = config.basic_auth
        if isinstance(auth_info, str) and os.path.isfile(auth_info):
            with open(auth_info, encoding='utf-8') as auth_file:
                auth_info = json.loads(auth_file.read())
        if isinstance(auth_info, dict):
            if username not in auth_info:
                return False
            return password == auth_info[username]
        elif password == auth_info:
            return True
        return False

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self._validate(username, password)
        if auth:
            self.set_current_user(username)
            next_url = self.get_cookie("next_url", "/")
            self.redirect(next_url)
        else:
            error_msg = "?error=" + tornado.escape.url_escape("Invalid username or password!")
            self.redirect(self.request.uri + error_msg)

    def set_current_user(self, user):
        if not user:
            self.clear_cookie("user")
            return
        self.set_secure_cookie("user", user, expires_days=config.oauth_expiry)
        id_token = base64url_encode(json.dumps({'user': user}))
        if state.encryption:
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
        self.set_secure_cookie('id_token', id_token, expires_days=config.oauth_expiry)



class BasicProvider(OAuthProvider):

    def __init__(self, basic_login_template=None, logout_template=None):
        if basic_login_template is None:
            self._basic_login_template = BASIC_LOGIN_TEMPLATE
        else:
            with open(basic_login_template) as f:
                self._basic_login_template = _env.from_string(f.read())
        super().__init__(logout_template=logout_template)

    @property
    def login_url(self):
        return '/login'

    @property
    def login_handler(self):
        BasicLoginHandler._basic_login_template = self._basic_login_template
        return BasicLoginHandler


AUTH_PROVIDERS = {
    'auth0': Auth0Handler,
    'azure': AzureAdLoginHandler,
    'azurev2': AzureAdV2LoginHandler,
    'bitbucket': BitbucketLoginHandler,
    'generic': GenericLoginHandler,
    'google': GoogleLoginHandler,
    'github': GithubLoginHandler,
    'gitlab': GitLabLoginHandler,
    'okta': OktaLoginHandler
}

# Populate AUTH Providers from external extensions
for entry_point in entry_points_for('panel.auth'):
    AUTH_PROVIDERS[entry_point.name] = entry_point.load()

config.param.objects(False)['_oauth_provider'].objects = list(AUTH_PROVIDERS.keys())
