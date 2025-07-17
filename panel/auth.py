import asyncio
import base64
import codecs
import datetime as dt
import hashlib
import json
import logging
import os
import re
import urllib.parse as urlparse
import uuid

from base64 import urlsafe_b64encode
from functools import partial
from typing import ClassVar

import tornado

from bokeh.server.auth_provider import AuthProvider
from bokeh.util.token import get_token_payload
from tornado.auth import OAuth2Mixin
from tornado.httpclient import HTTPError as HTTPClientError, HTTPRequest
from tornado.web import HTTPError, RequestHandler, decode_signed_value
from tornado.websocket import WebSocketHandler

from .config import config
from .entry_points import entry_points_for
from .io.resources import (
    BASIC_LOGIN_TEMPLATE, CDN_DIST, ERROR_TEMPLATE, LOGOUT_TEMPLATE, _env,
)
from .io.state import state
from .util import base64url_encode, decode_token

log = logging.getLogger(__name__)

STATE_COOKIE_NAME = 'panel-oauth-state'
CODE_COOKIE_NAME = 'panel-oauth-code'


def decode_response_body(response):
    """
    Decodes the JSON-format response body

    Parameters
    ----------
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
    body = re.sub("\'", '\\"', body)
    body = re.sub('"', '\"', body)
    body = re.sub("'", '"', body)
    body = json.loads(body)
    return body


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


class OAuthLoginHandler(tornado.web.RequestHandler, OAuth2Mixin):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }

    _DEFAULT_SCOPES = ['openid', 'email', 'profile', 'offline_access']

    _EXTRA_TOKEN_PARAMS = {
        'grant_type':    'authorization_code'
    }

    _access_token_header: ClassVar[str | None] = None

    _state_cookie: ClassVar[str | None] = None

    _error_template = ERROR_TEMPLATE

    _login_endpoint: ClassVar[str] = '/login'

    @property
    def _SCOPE(self):
        if 'scope' in config.oauth_extra_params:
            return config.oauth_extra_params['scope']
        elif 'PANEL_OAUTH_SCOPE' not in os.environ:
            return self._DEFAULT_SCOPES
        return [scope for scope in os.environ['PANEL_OAUTH_SCOPE'].split(',')]

    @property
    def _redirect_uri(self):
        if config.oauth_redirect_uri:
            return config.oauth_redirect_uri
        return f"{self.request.protocol}://{self.request.host}{state.base_url[:-1]}"

    async def get_authenticated_user(self, redirect_uri, client_id, state,
                                     client_secret=None, code=None):
        """
        Fetches the authenticated user

        Parameters
        ----------
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
            user, _, _, _ = await self._fetch_access_token(
                client_id,
                redirect_uri,
                client_secret=client_secret,
                code=code
            )
            return user

        params = {
            'redirect_uri': redirect_uri,
            'client_id':    client_id,
            'client_secret': client_secret,
            'response_type': 'code',
            'extra_params': {
                'state': state,
            }
        }
        if 'audience' in config.oauth_extra_params:
            params['extra_params']['audience'] = config.oauth_extra_params['audience']
        if self._SCOPE is not None:
            params['scope'] = self._SCOPE
        if 'scope' in config.oauth_extra_params:
            params['scope'] = config.oauth_extra_params['scope']
        log.debug("%s making authorize request", type(self).__name__)
        self.authorize_redirect(**params)

    async def _fetch_access_token(
        self, client_id, redirect_uri=None, client_secret=None, code=None,
        refresh_token=None, username=None, password=None
    ):
        """
        Fetches the access token.

        Parameters
        ----------
        client_id:
          The client ID
        redirect_uri:
          The redirect URI
        code:
          The response code from the server
        client_secret:
          The client secret
        refresh_token:
          A token used for refreshing the access_token
        username:
          A username
        password:
          A password
        """
        log.debug("%s making access token request.", type(self).__name__)
        params = {
            'client_id': client_id,
            **self._EXTRA_TOKEN_PARAMS
        }
        if redirect_uri:
            params['redirect_uri'] = redirect_uri
        if self._SCOPE:
            params['scope'] = ' '.join(self._SCOPE)
        if code:
            params['code'] = code
        if refresh_token:
            refreshing = True
            params['refresh_token'] = refresh_token
            params['grant_type'] = 'refresh_token'
        else:
            refreshing = False
        if client_secret:
            params['client_secret'] = client_secret
        elif username:
            params.update(username=username, password=password)
        else:
            params['code_verifier'] = self.get_code_cookie()

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
        except HTTPClientError as e:
            log.debug("%s access token request failed.", type(self).__name__)
            self._raise_error(e.response, status=401)

        if not response.body or not (body:= decode_response_body(response)):
            log.debug("%s token endpoint did not return a valid access token.", type(self).__name__)
            self._raise_error(response)

        if 'access_token' not in body:
            if refresh_token:
                log.debug("%s token endpoint did not reissue an access token.", type(self).__name__)
                return None, None, None
            self._raise_error(response, body, status=401)

        expires_in = body.get('expires_in')
        if expires_in:
            expires_in = int(expires_in)

        access_token, refresh_token = body['access_token'], body.get('refresh_token')
        if refreshing:
            # When refreshing the tokens we do not need to re-fetch the id_token or user info
            return None, access_token, refresh_token, expires_in
        elif id_token:= body.get('id_token'):
            try:
                user = OAuthLoginHandler.set_auth_cookies(self, id_token, access_token, refresh_token, expires_in)
            except HTTPError:
                pass
            else:
                log.debug("%s successfully obtained access_token and id_token.", type(self).__name__)
                return user, access_token, refresh_token, expires_in

        user_headers = dict(self._API_BASE_HEADERS)
        if self._OAUTH_USER_URL:
            if self._access_token_header:
                user_url = self._OAUTH_USER_URL
                user_headers['Authorization'] = self._access_token_header.format(
                    body['access_token']
                )
            else:
                user_url = '{}{}'.format(self._OAUTH_USER_URL, body['access_token'])

            log.debug("%s requesting OpenID userinfo.", type(self).__name__)
            try:
                user_response = await http.fetch(user_url, headers=user_headers)
                id_token = decode_response_body(user_response)
            except HTTPClientError:
                id_token = None

        if not id_token:
            log.debug(
                "%s could not fetch user information, the token endpoint did not "
                "return an id_token and no OpenID user info endpoint was provided. "
                "Attempting to code access_token to resolve user information.",
                type(self).__name__
            )
            try:
                id_token = decode_token(body['access_token'])
            except Exception:
                log.debug("%s could not decode access_token.", type(self).__name__)
                self._raise_error(response, body, status=401)

        log.debug("%s successfully obtained access_token and userinfo.", type(self).__name__)
        user = OAuthLoginHandler.set_auth_cookies(self, id_token, access_token, refresh_token, expires_in)
        return user, access_token, refresh_token, expires_in

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
        # Determine root url by removing login subpath and query parameters
        root_url = self.request.uri.replace(self._login_endpoint, '').split('?')[0]
        if not root_url.endswith('/'):
            root_url += '/'
        next_url = original_next_url = self.get_argument('next', root_url)
        if state.base_url and not next_url.startswith(state.base_url):
            next_url = original_next_url = next_url.replace('/', state.base_url, 1)
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
            {'state_id': uuid.uuid4().hex, 'next_url': next_url or state.base_url}
        )

    def get_code(self):
        code_verifier = uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex
        hashed_code_verifier = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = urlsafe_b64encode(hashed_code_verifier).decode("utf-8").replace("=", "")
        return code_verifier, code_challenge

    def get_code_cookie(self):
        code = (self.get_secure_cookie(CODE_COOKIE_NAME, max_age_days=config.oauth_expiry) or b'').decode('utf8', 'replace')
        self.clear_cookie(CODE_COOKIE_NAME)
        return code

    def set_code_cookie(self, code):
        self.set_secure_cookie(
            CODE_COOKIE_NAME, code, expires_days=config.oauth_expiry, httponly=True, path=config.cookie_path
        )

    async def get(self):
        log.debug("%s received login request", type(self).__name__)
        params = {
            'redirect_uri': self._redirect_uri,
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
            raise HTTPError(401, error_msg, reason=error)

        # Seek the authorization
        cookie_state = self.get_state_cookie()
        if code:
            if cookie_state != url_state:
                log.warning("OAuth state mismatch: %s != %s", cookie_state, url_state)
                raise HTTPError(401, "OAuth state mismatch. Please restart the authentication flow.", reason='state mismatch')

            decoded_state = _deserialize_state(url_state)
            # For security reason, the state value (cross-site token) will be
            # retrieved from the query string.
            params.update({
                'client_secret': config.oauth_secret,
                'code':  code,
                'state': url_state
            })
            user = await self.get_authenticated_user(**params)
            if user is None:
                raise HTTPError(403, "Permissions unknown.")
            log.debug("%s authorized user, redirecting to app.", type(self).__name__)
            self.redirect(decoded_state.get('next_url', state.base_url))
        else:
            # Redirect for user authentication
            params['state'] = decoded_state = self.get_state()
            self.set_state_cookie(decoded_state)
            await self.get_authenticated_user(**params)

    @staticmethod
    def set_auth_cookies(handler, id_token, access_token, refresh_token=None, expires_in=None):
        if id_token:
            if isinstance(id_token, str):
                decoded = decode_token(id_token)
            else:
                decoded = id_token
                id_token = base64url_encode(json.dumps(id_token))
            user_key = config.oauth_jwt_user or handler._USER_KEY
            if user_key in decoded:
                user = decoded[user_key]
            else:
                log.error("%s token payload did not contain expected %r.",
                          type(handler).__name__, user_key)
                raise HTTPError(401, "OAuth token payload missing user information")
            handler.clear_cookie('is_guest')
            handler.set_secure_cookie('user', user, expires_days=config.oauth_expiry, httponly=True, path=config.cookie_path)
        else:
            user = None

        if state.encryption:
            access_token = state.encryption.encrypt(access_token.encode('utf-8'))
            if id_token:
                id_token = state.encryption.encrypt(id_token.encode('utf-8'))
            if refresh_token:
                refresh_token = state.encryption.encrypt(refresh_token.encode('utf-8'))
        handler.set_secure_cookie('access_token', access_token, expires_days=config.oauth_expiry, httponly=True, path=config.cookie_path)
        if id_token:
            handler.set_secure_cookie('id_token', id_token, expires_days=config.oauth_expiry, httponly=True, path=config.cookie_path)
        if expires_in:
            now_ts = dt.datetime.now(dt.timezone.utc).timestamp()
            handler.set_secure_cookie('oauth_expiry', str(int(now_ts + expires_in)), expires_days=config.oauth_expiry, httponly=True, path=config.cookie_path)
        if refresh_token:
            handler.set_secure_cookie('refresh_token', refresh_token, expires_days=config.oauth_expiry, httponly=True, path=config.cookie_path)
        if user and user in state._oauth_user_overrides:
            state._oauth_user_overrides.pop(user, None)
        return user

    def _raise_error(self, response, body=None, status=400):
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
        if hasattr(body, "get"):
            log_message = body.get('error_description', str(body))
            reason = body.get('error', 'Unknown error')
        else:
            log_message = str(response)
            reason = 'Unknown Error'

        raise HTTPError(
            status,
            log_message=log_message,
            reason=reason
        )

    def write_error(self, status_code, **kwargs):
        _, e, _ = kwargs['exc_info']
        self.clear_all_cookies()
        self.set_header("Content-Type", 'text/html')
        if isinstance(e, HTTPError):
            error, error_msg = e.reason, e.log_message
        else:
            provider = self.__class__.__name__.replace('LoginHandler', '')
            log.error(
                f'{provider} OAuth provider encountered unexpected '
                f'error: {e}'
            )
            error, error_msg = (
                '500: Internal Server Error',
                'Server encountered unexpected problem.'
            )
        self.write(self._error_template.render(
            npm_cdn=config.npm_cdn,
            title='Panel: Authentication Error',
            error_type='Authentication Error',
            error=error,
            error_msg=error_msg,
            oauth_logout_link=self._OAUTH_LOGOUT_URL,
        ))


class GenericLoginHandler(OAuthLoginHandler):

    _access_token_header = 'Bearer {}'

    _EXTRA_TOKEN_PARAMS = {
        'grant_type': 'authorization_code'
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
    def _OAUTH_LOGOUT_URL(self):
        return config.oauth_extra_params.get('LOGOUT_URL', os.environ.get('PANEL_OAUTH_LOGOUT_URL'))

    @property
    def _USER_KEY(self):
        return config.oauth_extra_params.get('USER_KEY', os.environ.get('PANEL_USER_KEY', 'email'))


class PasswordLoginHandler(GenericLoginHandler):

    _EXTRA_TOKEN_PARAMS = {
        'grant_type': 'password'
    }

    def get(self):
        try:
            errormessage = self.get_argument("error")
        except Exception:
            errormessage = ""

        next_url = self.get_argument('next', None)
        if next_url:
            if state.base_url and not next_url.startswith(state.base_url):
                next_url = next_url.replace('/', state.base_url, 1)
            self.set_cookie("next_url", next_url)
        html = self._login_template.render(
            errormessage=errormessage,
            PANEL_CDN=CDN_DIST
        )
        self.write(html)

    async def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        user, _, _, _ = await self._fetch_access_token(
            client_id=config.oauth_key,
            redirect_uri=self._redirect_uri,
            username=username,
            password=password
        )
        next_url = self.get_cookie("next_url", state.base_url)
        self.redirect(next_url)


class CodeChallengeLoginHandler(GenericLoginHandler):

    async def get(self):
        code = self.get_argument("code", "")
        url_state = self.get_argument("state", "")
        redirect_uri = self._redirect_uri
        if not code or not url_state:
            self._authorize_redirect(redirect_uri)
            return

        cookie_state = self.get_state_cookie()
        if cookie_state != url_state:
            log.warning("OAuth state mismatch: %s != %s", cookie_state, url_state)
            raise HTTPError(400, "OAuth state mismatch")

        decoded_state = _deserialize_state(url_state)
        user = await self.get_authenticated_user(redirect_uri, config.oauth_key, url_state, code=code)
        if user is None:
            raise HTTPError(403)
        log.debug("%s authorized user, redirecting to app.", type(self).__name__)
        self.redirect(decoded_state.get('next_url', state.base_url))

    def _authorize_redirect(self, redirect_uri):
        state = self.get_state()
        self.set_state_cookie(state)
        code_verifier, code_challenge = self.get_code()
        self.set_code_cookie(code_verifier)
        params = {
            "client_id": config.oauth_key,
            "response_type": "code",
            "scope": ' '.join(self._SCOPE),
            "state": state,
            "response_mode": "query",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "redirect_uri": redirect_uri
        }
        query_params = urlparse.urlencode(params)
        self.redirect(f"{self._OAUTH_AUTHORIZE_URL}?{query_params}")



class GithubLoginHandler(OAuthLoginHandler):
    """GitHub OAuth2 Authentication
    To authenticate with GitHub, first register your application at
    https://github.com/settings/applications/new to get the client ID and
    secret.
    """

    _OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
    _OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    _OAUTH_USER_URL = 'https://api.github.com/user'
    _OAUTH_LOGOUT_URL = ''

    _access_token_header = 'token {}'

    _USER_KEY = 'login'


class BitbucketLoginHandler(OAuthLoginHandler):

    _API_BASE_HEADERS = {
        "Accept": "application/json",
    }

    _OAUTH_ACCESS_TOKEN_URL = "https://bitbucket.org/site/oauth2/access_token"
    _OAUTH_AUTHORIZE_URL = "https://bitbucket.org/site/oauth2/authorize"
    _OAUTH_USER_URL = "https://api.bitbucket.org/2.0/user?access_token="
    _OAUTH_LOGOUT_URL = ""

    _USER_KEY = 'username'


class Auth0Handler(OAuthLoginHandler):

    _access_token_header = 'Bearer {}'

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://{0}.auth0.com/oauth/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://{0}.auth0.com/authorize'
    _OAUTH_USER_URL_ = 'https://{0}.auth0.com/userinfo'
    _OAUTH_LOGOUT_URL_ = 'https://{0}.auth0.com/v2/logout?client_id={1}&returnTo={2}'

    _USER_KEY = 'email'

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

    @property
    def _OAUTH_LOGOUT_URL(self):
        subdomain = config.oauth_extra_params.get('subdomain', 'example')
        client_id = config.oauth_key
        return_to = f'{self.request.protocol}://{self.request.host}/logout'
        return self._OAUTH_LOGOUT_URL_.format(subdomain, client_id, return_to)


class GitLabLoginHandler(OAuthLoginHandler):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
    }

    _EXTRA_TOKEN_PARAMS = {
        'grant_type': 'authorization_code'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://{0}/oauth/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://{0}/oauth/authorize'
    _OAUTH_USER_URL_ = 'https://{0}/api/v4/user'
    _OAUTH_LOGOUT_URL_ = ''

    _access_token_header = 'Bearer {}'

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

    @property
    def _OAUTH_LOGOUT_URL(self):
        return self._OAUTH_LOGOUT_URL_.format(**config.oauth_extra_params)


class AzureAdLoginHandler(OAuthLoginHandler):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/authorize'
    _OAUTH_USER_URL_ = ''
    _OAUTH_LOGOUT_URL_ = ''

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

    @property
    def _OAUTH_LOGOUT_URL(self):
        return self._OAUTH_LOGOUT_URL_.format(**config.oauth_extra_params)


class AzureAdV2LoginHandler(OAuthLoginHandler):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize'
    _OAUTH_USER_URL_ = ''
    _OAUTH_LOGOUT_URL_ = ''

    _USER_KEY = 'email'

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

    @property
    def _OAUTH_LOGOUT_URL(self):
        return self._OAUTH_LOGOUT_URL_.format(**config.oauth_extra_params)


class OktaLoginHandler(OAuthLoginHandler):
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
    _OAUTH_LOGOUT_URL_ = ''
    _OAUTH_LOGOUT_URL__ = ''

    _USER_KEY = 'email'

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

    @property
    def _OAUTH_LOGOUT_URL(self):
        url = config.oauth_extra_params.get('url', 'okta.com')
        server = config.oauth_extra_params.get('server', 'default')
        if server:
            return self._OAUTH_LOGOUT_URL_.format(url, server)
        else:
            return self._OAUTH_LOGOUT_URL__.format(url, server)


class GoogleLoginHandler(OAuthLoginHandler):

    _API_BASE_HEADERS = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }
    _DEFAULT_SCOPES = ['openid', 'email', 'profile']
    _OAUTH_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    _OAUTH_ACCESS_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
    _USER_KEY = 'email'
    _OAUTH_LOGOUT_URL = ''


class BasicLoginHandler(RequestHandler):

    _login_endpoint = '/login'

    _login_template = BASIC_LOGIN_TEMPLATE

    def get(self):
        try:
            errormessage = self.get_argument("error")
        except Exception:
            errormessage = ""
        next_url = self.get_argument('next', state.base_url)
        if next_url:
            if state.base_url and not next_url.startswith(state.base_url):
                next_url = next_url.replace('/', state.base_url, 1)
            self.set_cookie("next_url", next_url)
        html = self._login_template.render(
            login_endpoint=self._login_endpoint,
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
            next_url = self.get_cookie("next_url", state.base_url)
            self.redirect(next_url)
        else:
            error_msg = "?error=" + tornado.escape.url_escape("Invalid username or password!")
            self.redirect(self.request.uri + error_msg)

    def set_current_user(self, user):
        if not user:
            self.clear_cookie("is_guest")
            self.clear_cookie("user")
            return
        self.clear_cookie("is_guest")
        self.set_secure_cookie("user", user, expires_days=config.oauth_expiry, httponly=True, path=config.cookie_path)
        id_token = base64url_encode(json.dumps({'user': user}))
        if state.encryption:
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
        self.set_secure_cookie('id_token', id_token, expires_days=config.oauth_expiry, httponly=True, path=config.cookie_path)


class LogoutHandler(tornado.web.RequestHandler):

    _login_endpoint = '/login'

    _logout_template = LOGOUT_TEMPLATE

    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("id_token")
        self.clear_cookie("access_token")
        self.clear_cookie("refresh_token")
        self.clear_cookie("oauth_expiry")
        self.clear_cookie(STATE_COOKIE_NAME)
        html = self._logout_template.render(
            PANEL_CDN=CDN_DIST,
            LOGIN_ENDPOINT=self._login_endpoint
        )
        self.write(html)


class BasicAuthProvider(AuthProvider):
    """
    An AuthProvider which serves a simple login and logout page.
    """

    def __init__(
        self, login_endpoint=None, logout_endpoint=None,
        login_template=None, logout_template=None, error_template=None,
        guest_endpoints=None
    ):
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
        if login_template is None:
            self._login_template = BASIC_LOGIN_TEMPLATE
        else:
            with open(login_template) as f:
                self._login_template = _env.from_string(f.read())
        self._login_endpoint = login_endpoint or '/login'
        self._logout_endpoint = logout_endpoint or '/logout'
        self._guest_endpoints = guest_endpoints or []

        state.on_session_destroyed(self._remove_user)
        super().__init__()

    def _remove_user(self, session_context):
        guest_cookie = session_context.request.cookies.get('is_guest')
        user_cookie = session_context.request.cookies.get('user')
        if guest_cookie:
            user = 'guest'
        elif user_cookie:
            user = decode_signed_value(
                config.cookie_secret, 'user', user_cookie
            )
            if user:
                user = user.decode('utf-8')
        else:
            user = None
        if not user:
            return
        state._active_users[user] -= 1
        if not state._active_users[user]:
            del state._active_users[user]

    def _allow_guest(self, uri):
        if config.oauth_optional and not (uri == self._login_endpoint or '?code=' in uri):
            return True
        return True if uri.replace('/ws', '') in self._guest_endpoints else False

    @property
    def get_user(self):
        def get_user(request_handler):
            user = request_handler.get_secure_cookie("user", max_age_days=config.oauth_expiry)
            if user:
                user = user.decode('utf-8')
            elif self._allow_guest(request_handler.request.uri):
                user = "guest"
                request_handler.request.cookies["is_guest"] = "1"
                if not isinstance(request_handler, WebSocketHandler):
                    request_handler.set_cookie("is_guest", "1", expires_days=config.oauth_expiry, path=config.cookie_path)

            if user and isinstance(request_handler, WebSocketHandler):
                state._active_users[user] += 1
            return user
        return get_user

    @property
    def login_url(self):
        return self._login_endpoint

    @property
    def login_handler(self):
        BasicLoginHandler._login_endpoint = self._login_endpoint
        BasicLoginHandler._login_template = self._login_template
        return BasicLoginHandler

    @property
    def logout_url(self):
        return self._logout_endpoint

    @property
    def logout_handler(self):
        if self._logout_template:
            LogoutHandler._logout_template = self._logout_template
        LogoutHandler._login_endpoint = self._login_endpoint
        return LogoutHandler


class OAuthProvider(BasicAuthProvider):
    """
    An AuthProvider using specific OAuth implementation selected via
    the global config.oauth_provider configuration.
    """

    @property
    def get_user(self):
        return None

    @property
    def get_user_async(self):
        async def get_user(handler):
            user = super(OAuthProvider, self).get_user(handler)
            if not config.oauth_refresh_tokens or user is None:
                return user

            # Try to obtain user oauth overrides from WS headers
            # in case the HTTP handler refreshed tokens
            is_ws = isinstance(handler, WebSocketHandler)
            if is_ws and 'Sec-Websocket-Protocol' in handler.request.headers:
                protocol_header = handler.request.headers['Sec-Websocket-Protocol']
                _, token = protocol_header.split(', ')
                payload = get_token_payload(token)
                if 'user_data' in payload:
                    user_data = payload['user_data']
                    if state.encryption:
                        user_data = state.encryption.decrypt(user_data).decode('utf-8')
                    user_data = json.loads(user_data)
                    state._oauth_user_overrides[user] = user_data

            now_ts = dt.datetime.now(dt.timezone.utc).timestamp()
            expiry = None
            if user in state._oauth_user_overrides:
                while not state._oauth_user_overrides[user]:
                    await asyncio.sleep(0.1)
                user_state = state._oauth_user_overrides[user]
                access_token = user_state['access_token']
                if user_state['expiry']:
                    expiry = user_state['expiry']
            else:
                access_cookie = handler.get_secure_cookie('access_token', max_age_days=config.oauth_expiry)
                if not access_cookie:
                    log.debug("No access token available, forcing user to reauthenticate.")
                    return
                access_token = state._decrypt_cookie(access_cookie)

            # Try to get expiry directly from the token since that is
            # the real source of truth
            try:
                access_json = decode_token(access_token)
                expiry = access_json['exp']
            except Exception:
                pass

            # Try casting expiry to float as it may be stored as bytes
            try:
                expiry = float(expiry)
            except Exception:
                expiry = None

            if expiry is None:
                expiry = handler.get_secure_cookie('oauth_expiry', max_age_days=config.oauth_expiry)
                if expiry is None:
                    # Token does not have content and therefore does not expire
                    log.debug("access_token is not a valid JWT token. Expiry cannot be determined.")
                    return user

            if user in state._oauth_user_overrides:
                refresh_token = state._oauth_user_overrides[user]['refresh_token']
            else:
                refresh_cookie = handler.get_secure_cookie('refresh_token', max_age_days=config.oauth_expiry)
                if refresh_cookie:
                    refresh_token = state._decrypt_cookie(refresh_cookie)
                else:
                    refresh_token = None

            if expiry > now_ts and refresh_token:
                log.debug("Fully authenticated and tokens still valid.")
                if is_ws:
                    self._schedule_refresh(expiry, user, refresh_token, handler.application, handler.request)
                expires_in = expiry - now_ts
                OAuthLoginHandler.set_auth_cookies(
                    handler, None, access_token, refresh_token, expires_in
                )
                return user

            if refresh_token:
                try:
                    refresh_json = decode_token(refresh_token)
                    if refresh_json['exp'] < now_ts:
                        refresh_token = None
                except Exception:
                    # If refresh token is not a valid JWT token then it does not expire
                    pass

            if refresh_token is None:
                handler.clear_cookie('state')
                log.debug("%s access_token is expired and refresh_token not available, forcing user to reauthenticate.", type(self).__name__)
                return

            log.debug("access_token has expired, %s using refresh_token to obtain new tokens.", type(self).__name__)
            access_token, refresh_token, expiry = await self._scheduled_refresh(
                user, refresh_token, handler.application, handler.request,
                reschedule=is_ws
            )
            # If user not in overrides refresh failed and we need to
            # fully reauthenticate
            if user not in state._oauth_user_overrides:
                return
            expires_in = expiry - now_ts
            OAuthLoginHandler.set_auth_cookies(
                handler, None, access_token, refresh_token, expires_in
            )
            return user
        return get_user

    @property
    def login_handler(self):
        handler = AUTH_PROVIDERS[config.oauth_provider]
        if self._error_template:
            handler._error_template = self._error_template
        handler._login_template = self._login_template
        handler._login_endpoint = self._login_endpoint
        return handler

    def _remove_user(self, session_context):
        guest_cookie = session_context.request.cookies.get('is_guest')
        user_cookie = session_context.request.cookies.get('user')
        if guest_cookie:
            user = 'guest'
        elif user_cookie:
            user = decode_signed_value(
                config.cookie_secret, 'user', user_cookie
            )
            if user:
                user = user.decode('utf-8')
        else:
            user = None
        if not user:
            return
        state._active_users[user] -= 1
        if not state._active_users[user]:
            del state._active_users[user]
            # Don't remove the user override when it is set to None or
            # is missing, as this means it is being refreshed.
            if state._oauth_user_overrides.get(user) is not None:
                del state._oauth_user_overrides[user]

    def _schedule_refresh(self, expiry_ts, user, refresh_token, application, request):
        if not state._active_users.get(user):
            return
        now_ts = dt.datetime.now(dt.timezone.utc).timestamp()
        expiry_seconds = expiry_ts - now_ts - 60
        expiry_date = dt.datetime.now() + dt.timedelta(seconds=expiry_seconds) # schedule_task is in local TZ
        refresh_cb = partial(self._scheduled_refresh, user, refresh_token, application, request)
        if expiry_seconds <= 0:
            log.debug("%s token expired unexpectedly, refreshing immediately.", type(self).__name__)
            state.execute(refresh_cb)
            return
        log.debug("%s scheduling token refresh in %d seconds", type(self).__name__, expiry_seconds)
        task = f'{user}-refresh-access-tokens'
        try:
            state.cancel_task(task)
        except KeyError:
            pass
        finally:
            state.schedule_task(task, refresh_cb, at=expiry_date)

    async def _scheduled_refresh(self, user, refresh_token, application, request, reschedule=True):
        await self._refresh_access_token(user, refresh_token, application, request)
        if user not in state._oauth_user_overrides:
            return None, None, None
        user_state = state._oauth_user_overrides[user]
        access_token, refresh_token = user_state['access_token'], user_state['refresh_token']
        if user_state['expiry']:
            expiry = user_state['expiry']
        else:
            expiry = decode_token(access_token)['exp']
        if reschedule:
            self._schedule_refresh(expiry, user, refresh_token, application, request)
        return access_token, refresh_token, expiry

    async def _refresh_access_token(self, user, refresh_token, application, request):
        if user in state._oauth_user_overrides:
            if not state._oauth_user_overrides[user]:
                # Token is already being refreshed await it
                while not state._oauth_user_overrides[user]:
                    await asyncio.sleep(0.1)
                return
            else:
                refresh_token = state._oauth_user_overrides[user]['refresh_token']
        log.debug("%s refreshing tokens", type(self).__name__)
        state._oauth_user_overrides[user] = {}
        auth_handler = self.login_handler(application=application, request=request)
        _, access_token, refresh_token, expires_in = await auth_handler._fetch_access_token(
            client_id=config.oauth_key,
            client_secret=config.oauth_secret,
            refresh_token=refresh_token
        )
        if access_token:
            log.debug("%s successfully refreshed access_token", type(self).__name__)
            now_ts = dt.datetime.now(dt.timezone.utc).timestamp()
            state._oauth_user_overrides[user] = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expiry': now_ts+expires_in if expires_in else None
            }
        else:
            log.debug("%s failed to refresh access_token", type(self).__name__)
            del state._oauth_user_overrides[user]


class PAMLoginHandler(BasicLoginHandler):
    """
    A LoginHandler that authenticates users via PAM.
    """

    def _validate(self, username, password):
        try:
            import pamela
        except ImportError as e:
            log.error(
                "PAM authentication requires the pamela package. Please install it with e.g. 'pip install pamela'"
            )
            raise e
        try:
            pamela.authenticate(username, password)
        except pamela.PAMError:
            return False
        return True


AUTH_PROVIDERS = {
    'auth0': Auth0Handler,
    'azure': AzureAdLoginHandler,
    'azurev2': AzureAdV2LoginHandler,
    'bitbucket': BitbucketLoginHandler,
    'generic': GenericLoginHandler,
    'google': GoogleLoginHandler,
    'github': GithubLoginHandler,
    'gitlab': GitLabLoginHandler,
    'okta': OktaLoginHandler,
    'password': PasswordLoginHandler,
    'auth_code': CodeChallengeLoginHandler,
    'pam': PAMLoginHandler,
}

# Populate AUTH Providers from external extensions
for entry_point in entry_points_for('panel.auth'):
    AUTH_PROVIDERS[entry_point.name] = entry_point.load()

config.param.objects(False)['_oauth_provider'].objects = list(AUTH_PROVIDERS.keys())
