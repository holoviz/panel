import codecs
import json
import logging
import os
import pkg_resources
import re
import uuid

from urllib.parse import urlencode

import tornado

from bokeh.server.auth_provider import AuthProvider
from tornado.auth import OAuth2Mixin
from tornado.httpclient import HTTPRequest, HTTPError
from tornado.httputil import url_concat

from .config import config
from .io import state
from .util import base64url_encode, base64url_decode

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


def extract_urlparam(name, urlparam):
    """
    Attempts to extract a url parameter embedded in another URL
    parameter.
    """
    if urlparam is None:
        return None
    query = name+'='
    if query in urlparam:
        split_args = urlparam[urlparam.index(query):].replace(query, '').split('&')
        return split_args[0] if split_args else None
    else:
        return None


class OAuthLoginHandler(tornado.web.RequestHandler):

    _API_BASE_HEADERS = {
        'Accept': 'application/json',
        'User-Agent': 'Tornado OAuth'
    }

    _access_token_header = None

    _EXTRA_TOKEN_PARAMS = {}

    _SCOPE = None

    _state_cookie = None

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
        req = HTTPRequest(
            self._OAUTH_ACCESS_TOKEN_URL,
            method='POST',
            body=urlencode(params),
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

        log.debug("%s received user information." % type(self).__name__)
        return self._on_auth(user, body['access_token'])

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
        }
        # Some OAuth2 backends do not correctly return code
        next_arg = self.get_argument('next', None)
        url_state = self.get_argument('state', None)
        code = self.get_argument('code', extract_urlparam('code', next_arg))
        url_state = self.get_argument('state', extract_urlparam('state', next_arg))

        # Seek the authorization
        cookie_state = self.get_state_cookie()
        if code:
            if cookie_state != url_state:
                log.warning("OAuth state mismatch: %s != %s", cookie_state, url_state)
                raise HTTPError(400, "OAuth state mismatch")

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
            log.debug("%s authorized user, redirecting to app." % type(self).__name__)
            self.redirect('/')
        else:
            # Redirect for user authentication
            state = uuid.uuid4().hex
            params['state'] = state
            self.set_state_cookie(state)
            await self.get_authenticated_user(**params)

    def _on_auth(self, user_info, access_token):
        user_key = config.oauth_jwt_user or self._USER_KEY
        user = user_info[user_key]
        self.set_secure_cookie('user', user, expires_days=config.oauth_expiry)
        id_token = base64url_encode(json.dumps(user_info))
        if state.encryption:
            access_token = state.encryption.encrypt(access_token.encode('utf-8'))
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
        self.set_secure_cookie('access_token', access_token, expires_days=config.oauth_expiry)
        self.set_secure_cookie('id_token', id_token, expires_days=config.oauth_expiry)
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
        raise HTTPError(500, f"{provider} authentication failed")


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

        try:
            response = await http.fetch(req)
        except HTTPError as e:
            return self._on_error(e.response)

        body = decode_response_body(response)

        if 'access_token' not in body:
            return self._on_error(response, body)

        log.debug("%s granted access_token." % type(self).__name__)

        access_token = body['access_token']
        id_token = body['id_token']
        return self._on_auth(id_token, access_token)

    def _on_auth(self, id_token, access_token):
        decoded = decode_id_token(id_token)
        user_key = config.oauth_jwt_user or self._USER_KEY
        if user_key in decoded:
            user = decoded[user_key]
        else:
            log.error("%s token payload did not contain expected '%s'." %
                      (type(self).__name__, user_key))
            raise HTTPError(400, "OAuth token payload missing user information")
        self.set_secure_cookie('user', user, expires_days=config.oauth_expiry)
        if state.encryption:
            access_token = state.encryption.encrypt(access_token.encode('utf-8'))
            id_token = state.encryption.encrypt(id_token.encode('utf-8'))
        self.set_secure_cookie('access_token', access_token, expires_days=config.oauth_expiry)
        self.set_secure_cookie('id_token', id_token, expires_days=config.oauth_expiry)
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

    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("id_token")
        self.clear_cookie("access_token")
        self.clear_cookie(STATE_COOKIE_NAME)
        self.redirect("/")


class OAuthProvider(AuthProvider):

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
        return AUTH_PROVIDERS[config.oauth_provider]

    @property
    def logout_url(self):
        return "/logout"

    @property
    def logout_handler(self):
        return LogoutHandler


AUTH_PROVIDERS = {
    'auth0': Auth0Handler,
    'azure': AzureAdLoginHandler,
    'bitbucket': BitbucketLoginHandler,
    'google': GoogleLoginHandler,
    'github': GithubLoginHandler,
    'gitlab': GitLabLoginHandler,
    'okta': OktaLoginHandler
}

# Populate AUTH Providers from external extensions
for entry_point in pkg_resources.iter_entry_points('panel.auth'):
    AUTH_PROVIDERS[entry_point.name] = entry_point.resolve()

config.param.objects(False)['_oauth_provider'].objects = list(AUTH_PROVIDERS.keys())
