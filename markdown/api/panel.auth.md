# panel.auth module

class panel.auth.Auth0Handler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[OAuthLoginHandler](#panel.auth.OAuthLoginHandler)

class panel.auth.AzureAdLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[OAuthLoginHandler](#panel.auth.OAuthLoginHandler)

class panel.auth.AzureAdV2LoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[OAuthLoginHandler](#panel.auth.OAuthLoginHandler)

class panel.auth.BasicAuthProvider(login_endpoint=None, logout_endpoint=None, login_template=None, logout_template=None, error_template=None, guest_endpoints=None)
Bases: `AuthProvider`

An AuthProvider which serves a simple login and logout page.

Attributes:
[get_user](#panel.auth.BasicAuthProvider.get_user)
A function to get the current authenticated user.

[login_handler](#panel.auth.BasicAuthProvider.login_handler)
A request handler class for a login page.

[login_url](#panel.auth.BasicAuthProvider.login_url)
A URL to redirect unauthenticated users to for login.

[logout_handler](#panel.auth.BasicAuthProvider.logout_handler)
A request handler class for a logout page.

[logout_url](#panel.auth.BasicAuthProvider.logout_url)
A URL to redirect authenticated users to for logout.

property get_user
A function to get the current authenticated user.

This property may return None, if a
`get_user_async` function is supplied instead.

If a function is returned, it should accept a
`RequestHandler` and return the current
authenticated user.

property login_handler
A request handler class for a login page.

This property may return None, if `login_url`
is supplied instead.

If a class is returned, it must be a subclass of RequestHandler, which
will used for the endpoint specified by
`logout_url`

property login_url
A URL to redirect unauthenticated users to for login.

This property may return None, if a
`get_login_url` function is supplied instead.

property logout_handler
A request handler class for a logout page.

This property may return None.

If a class is returned, it must be a subclass of RequestHandler, which
will used for the endpoint specified by
`logout_url`

property logout_url
A URL to redirect authenticated users to for logout.

This property may return None.

class panel.auth.BasicLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: `RequestHandler`

Methods

|                      |     |
|----------------------|-----|
| **get**              |     |
| **post**             |     |
| **set_current_user** |     |

class panel.auth.BitbucketLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[OAuthLoginHandler](#panel.auth.OAuthLoginHandler)

class panel.auth.CodeChallengeLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[GenericLoginHandler](#panel.auth.GenericLoginHandler)

Methods

|         |     |
|---------|-----|
| **get** |     |

class panel.auth.GenericLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[OAuthLoginHandler](#panel.auth.OAuthLoginHandler)

class panel.auth.GitLabLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[OAuthLoginHandler](#panel.auth.OAuthLoginHandler)

class panel.auth.GithubLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[OAuthLoginHandler](#panel.auth.OAuthLoginHandler)

GitHub OAuth2 Authentication To authenticate with GitHub, first register
your application at
[settings/applications](https://github.com/settings/applications/new) to get the
client ID and secret.

class panel.auth.GoogleLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[OAuthLoginHandler](#panel.auth.OAuthLoginHandler)

class panel.auth.LogoutHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: `RequestHandler`

Methods

|         |     |
|---------|-----|
| **get** |     |

class panel.auth.OAuthLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: `RequestHandler`,
`OAuth2Mixin`

Methods

|  |  |
|----|----|
| [get_authenticated_user](#panel.auth.OAuthLoginHandler.get_authenticated_user)(redirect_uri, ...\[, ...\]) | Fetches the authenticated user |
| [get_state_cookie](#panel.auth.OAuthLoginHandler.get_state_cookie)() | Get OAuth state from cookies To be compared with the value in redirect URL |
| [write_error](#panel.auth.OAuthLoginHandler.write_error)(status_code, **kwargs) | Override to implement custom error pages. |

|                      |     |
|----------------------|-----|
| **get**              |     |
| **get_code**         |     |
| **get_code_cookie**  |     |
| **get_state**        |     |
| **set_auth_cookies** |     |
| **set_code_cookie**  |     |
| **set_state_cookie** |     |

async get_authenticated_user(redirect_uri, client_id, state, client_secret=None, code=None)
Fetches the authenticated user

Parameters:
**redirect_uri: (str)**
The OAuth redirect URI

**client_id: (str)**
The OAuth client ID

**state: (str)**
The unguessable random string to protect against cross-site request
forgery attacks

**client_secret: (str, optional)**
The client secret

**code: (str, optional)**
The response code from the server

get_state_cookie()
Get OAuth state from cookies To be compared with the value in redirect
URL

write_error(status_code, **kwargs)
Override to implement custom error pages.

`write_error` may call write, render,
set_header, etc to produce output as usual.

If this error was caused by an uncaught exception (including HTTPError),
an `exc_info` triple will be available as
`kwargs["exc_info"]`. Note that this exception
may not be the “current” exception for purposes of methods like
`sys.exc_info()` or
`traceback.format_exc`.

class panel.auth.OAuthProvider(login_endpoint=None, logout_endpoint=None, login_template=None, logout_template=None, error_template=None, guest_endpoints=None)
Bases:
[BasicAuthProvider](#panel.auth.BasicAuthProvider)

An AuthProvider using specific OAuth implementation selected via the
global config.oauth_provider configuration.

Attributes:
[get_user](#panel.auth.OAuthProvider.get_user)
A function to get the current authenticated user.

[get_user_async](#panel.auth.OAuthProvider.get_user_async)
An async function to get the current authenticated user.

[login_handler](#panel.auth.OAuthProvider.login_handler)
A request handler class for a login page.

property get_user
A function to get the current authenticated user.

This property may return None, if a
`get_user_async` function is supplied instead.

If a function is returned, it should accept a
`RequestHandler` and return the current
authenticated user.

property get_user_async
An async function to get the current authenticated user.

This property may return None, if a `get_user`
function is supplied instead.

If a function is returned, it should accept a
`RequestHandler` and return the current
authenticated user.

property login_handler
A request handler class for a login page.

This property may return None, if `login_url`
is supplied instead.

If a class is returned, it must be a subclass of RequestHandler, which
will used for the endpoint specified by
`logout_url`

class panel.auth.OktaLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[OAuthLoginHandler](#panel.auth.OAuthLoginHandler)

Okta OAuth2 Authentication

To authenticate with Okta you first need to set up and configure in the
Okta developer console.

class panel.auth.PAMLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[BasicLoginHandler](#panel.auth.BasicLoginHandler)

A LoginHandler that authenticates users via PAM.

class panel.auth.PasswordLoginHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[GenericLoginHandler](#panel.auth.GenericLoginHandler)

Methods

|          |     |
|----------|-----|
| **get**  |     |
| **post** |     |

panel.auth.decode_response_body(response)
Decodes the JSON-format response body

Parameters:
**response: tornado.httpclient.HTTPResponse**

Returns:
Decoded response content

panel.auth.extract_urlparam(args, key)
Extracts a request argument from a urllib.parse.parse_qs dict.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
