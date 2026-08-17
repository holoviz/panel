# panel.io.server module

Utilities for creating bokeh Server instances.

class panel.io.server.AuthenticatedStaticFileHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: `StaticFileHandler`

Methods

|  |  |
|----|----|
| [get_current_user](#panel.io.server.AuthenticatedStaticFileHandler.get_current_user)() | Delegate to the synchronous `get_user` method of the auth provider |
| [get_login_url](#panel.io.server.AuthenticatedStaticFileHandler.get_login_url)() | Delegates to\`\`get_login_url\`\` method of the auth provider, or the `login_url` attribute. |
| [prepare](#panel.io.server.AuthenticatedStaticFileHandler.prepare)() | Async counterpart to `get_current_user` |

|         |     |
|---------|-----|
| **get** |     |

get_current_user()
Delegate to the synchronous `get_user` method
of the auth provider

get_login_url()
Delegates to\`\`get_login_url\`\` method of the auth provider, or the
`login_url` attribute.

async prepare()
Async counterpart to `get_current_user`

class panel.io.server.AutoloadJsHandler(tornado_app: BokehTornado, \*args, **kw)
Bases: `AutoloadJsHandler`

Implements a custom Tornado handler for the autoload JS chunk

Methods

|         |     |
|---------|-----|
| **get** |     |

class panel.io.server.ComponentResourceHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: `StaticFileHandler`

A handler that serves local resources relative to a Python module. The
handler resolves a specific Panel component by module reference and
name, then resolves an attribute on that component to check if it
contains the requested resource path.

/\<endpoint\>/\<module\>/\<class\>/\<attribute\>/\<path\>

Methods

|  |  |
|----|----|
| [get_absolute_path](#panel.io.server.ComponentResourceHandler.get_absolute_path)(root, path) | Returns the absolute location of `path` relative to `root`. |
| [parse_url_path](#panel.io.server.ComponentResourceHandler.parse_url_path)(path) | Resolves the resource the URL pattern refers to. |
| [validate_absolute_path](#panel.io.server.ComponentResourceHandler.validate_absolute_path)(root, absolute_path) | Validate and return the absolute path. |

|                |     |
|----------------|-----|
| **initialize** |     |

classmethod get_absolute_path(root: str, path: str) → str
Returns the absolute location of `path`
relative to `root`.

`root` is the path configured for this
StaticFileHandler (in most cases the
`static_path` Application setting).

This class method may be overridden in subclasses. By default it returns
a filesystem path, but other strings may be used as long as they are
unique and understood by the subclass’s overridden get_content.

Added in version 3.1.

initialize(path: str \| Literal\['root'\] = 'root', default_filename: str \| None = None)

parse_url_path(path: str) → str
Resolves the resource the URL pattern refers to.

validate_absolute_path(root: str, absolute_path: str) → str
Validate and return the absolute path.

`root` is the configured path for the
StaticFileHandler, and `path` is the result of
get_absolute_path

This is an instance method called during request processing, so it may
raise HTTPError or use methods like RequestHandler.redirect (return None
after redirecting to halt further processing). This is where 404 errors
for missing files are generated.

This method may modify the path before returning it, but note that any
such modifications will not be understood by make_static_url.

In instance methods, this method’s result is available as
`self.absolute_path`.

Added in version 3.1.

class panel.io.server.DocHandler(tornado_app: BokehTornado, \*args, **kw)
Bases:
[LoginUrlMixin](#panel.io.server.LoginUrlMixin),
`DocHandler`

Methods

|                 |     |
|-----------------|-----|
| **get**         |     |
| **get_session** |     |

class panel.io.server.LoginUrlMixin
Bases: `object`

Overrides the AuthRequestHandler.get_login_url implementation to
correctly handle prefixes.

Methods

|  |  |
|----|----|
| [get_login_url](#panel.io.server.LoginUrlMixin.get_login_url)() | Delegates to\`\`get_login_url\`\` method of the auth provider, or the `login_url` attribute. |

get_login_url()
Delegates to\`\`get_login_url\`\` method of the auth provider, or the
`login_url` attribute.

class panel.io.server.ProxyFallbackHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: `RequestHandler`

A RequestHandler that wraps another HTTP server callback and proxies the
subpath.

Methods

|  |  |
|----|----|
| [prepare](#panel.io.server.ProxyFallbackHandler.prepare)() | Called at the beginning of a request before get/post/etc. |

|                |     |
|----------------|-----|
| **initialize** |     |

initialize(fallback, proxy=None)

prepare()
Called at the beginning of a request before get/post/etc.

Override this method to perform common initialization regardless of the
request method. There is no guarantee that
`prepare` will be called if an error occurs
that is handled by the framework.

Asynchronous support: Use
`async`` ``def` or
decorate this method with .gen.coroutine to make it asynchronous. If
this method returns an `Awaitable` execution
will not proceed until the `Awaitable` is done.

Added in version 3.1:
Asynchronous support.

class panel.io.server.RootHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases:
[LoginUrlMixin](#panel.io.server.LoginUrlMixin),
`RootHandler`

Custom RootHandler that provides the CDN_DIST directory as a template
variable.

Methods

|  |  |
|----|----|
| [render](#panel.io.server.RootHandler.render)(\*args, **kwargs) | Renders the template with the given arguments as the response. |

|         |     |
|---------|-----|
| **get** |     |

render(\*args, **kwargs)
Renders the template with the given arguments as the response.

`render()` calls
`finish()`, so no other output methods can be
called after it.

Returns a .Future with the same semantics as the one returned by finish.
Awaiting this .Future is optional.

Changed in version 5.1: Now
returns a .Future instead of `None`.

class panel.io.server.Server(\*args, **kwargs)
Bases: `Server`

Methods

|  |  |
|----|----|
| [start](#panel.io.server.Server.start)() | Install the Bokeh Server and its background tasks on a Tornado `IOLoop`. |
| [stop](#panel.io.server.Server.stop)(\[wait\]) | Stop the Bokeh Server. |

start() → None
Install the Bokeh Server and its background tasks on a Tornado
`IOLoop`.

This method does *not* block and does *not* affect the state of the
Tornado `IOLoop` You must start and stop the
loop yourself, i.e. this method is typically useful when you are already
explicitly managing an `IOLoop` yourself.

To start a Bokeh server and immediately “run forever” in a blocking
manner, see `run_until_shutdown()`.

stop(wait: bool = True) → None
Stop the Bokeh Server.

This stops and removes all Bokeh Server
`IOLoop` callbacks, as well as stops the
`HTTPServer` that this instance was configured
with.

Args:
wait (bool):
Whether to wait for orderly cleanup (default: True)

Returns:
None

class panel.io.server.WSHandler(tornado_app, \*args, **kw)
Bases: `WSHandler`

Methods

|  |  |
|----|----|
| [open](#panel.io.server.WSHandler.open)(\*args, **kwargs) | Initialize a connection to a client. |
| [prepare](#panel.io.server.WSHandler.prepare)() | Async counterpart to `get_current_user` |

open(\*args, **kwargs)
Initialize a connection to a client.

Returns:
None

async prepare()
Async counterpart to `get_current_user`

panel.io.server.async_execute(func: Callable\[..., None\]) → None
Wrap async event loop scheduling to ensure that with_lock flag is
propagated from function to partial wrapping it.

panel.io.server.get_server(panel: TViewableFuncOrPath \| dict\[str, TViewableFuncOrPath\], port: int = 0, address: str \| None = None, websocket_origin: str \| list\[str\] \| None = None, loop: IOLoop \| None = None, show: bool = False, start: bool = False, title: str \| dict\[str, str\] \| None = None, verbose: bool = False, location: bool \| Location = True, admin: bool = False, static_dirs: Mapping\[str, str\] = {}, basic_auth: str \| None = None, oauth_provider: str \| None = None, oauth_key: str \| None = None, oauth_secret: str \| None = None, oauth_redirect_uri: str \| None = None, oauth_extra_params: Mapping\[str, str\] = {}, oauth_error_template: str \| None = None, cookie_path: str = '/', cookie_secret: str \| None = None, oauth_encryption_key: str \| None = None, oauth_jwt_user: str \| None = None, oauth_refresh_tokens: str \| None = None, oauth_guest_endpoints: list\[str\] \| None = None, oauth_optional: bool \| None = None, root_path: str \| None = None, login_endpoint: str \| None = None, logout_endpoint: str \| None = None, login_template: str \| None = None, logout_template: str \| None = None, session_history: str \| None = None, liveness: bool \| str = False, warm: bool = False, **kwargs) → Server
Returns a Server instance with this panel attached as the root app.

Parameters:
**panel: Viewable, function or {str: Viewable}**
A Panel object, a function returning a Panel object or a dictionary
mapping from the URL slug to either.

**port: int (optional, default=0)**
Allows specifying a specific port

address : str
The address the server should listen on for HTTP requests.

**websocket_origin: str or list(str) (optional)**
A list of hosts that can connect to the websocket.

This is typically required when embedding a server app in an external
web site.

If None, “localhost” is used.

loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
The tornado IOLoop to run the Server on.

show : boolean (optional, default=False)
Whether to open the server in a new browser tab on start.

start : boolean(optional, default=False)
Whether to start the Server.

title : str or {str: str} (optional, default=None)
An HTML title for the application or a dictionary mapping from the URL
slug to a customized title.

**verbose: boolean (optional, default=False)**
Whether to report the address and port.

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

**admin: boolean (default=False)**
Whether to enable the admin panel

**static_dirs: dict (optional, default={})**
A dictionary of routes and local paths to serve as static file
directories on those routes.

**basic_auth: str (optional, default=None)**
Password or filepath to use with basic auth provider.

**oauth_provider: str**
One of the available OAuth providers

**oauth_key: str (optional, default=None)**
The public OAuth identifier

**oauth_secret: str (optional, default=None)**
The client secret for the OAuth provider

**oauth_redirect_uri: Optional\[str\] = None,**
Overrides the default OAuth redirect URI

**oauth_extra_params: dict (optional, default={})**
Additional information for the OAuth provider

**oauth_error_template: str (optional, default=None)**
Jinja2 template used when displaying authentication errors.

**cookie_path: str (optional, default=’/’)**
The sub path of the domain the cookie is valid for.

**cookie_secret: str (optional, default=None)**
A random secret string to sign cookies (required for OAuth)

**oauth_encryption_key: str (optional, default=None)**
A random encryption key used for encrypting OAuth user information and
access tokens.

**oauth_jwt_user: Optional\[str\] = None,**
Key that identifies the user in the JWT id_token.

**oauth_refresh_tokens: bool (optional, default=None)**
Whether to automatically refresh OAuth access tokens when they expire.

**oauth_guest_endpoints: list (optional, default=None)**
List of endpoints that can be accessed as a guest without
authenticating.

**oauth_optional: bool (optional, default=None)**
Whether the user will be forced to go through login flow or if they can
access all applications as a guest.

**root_path: str (optional, default=None)**
Root path the application is being served on when behind a reverse
proxy.

**login_endpoint: str (optional, default=None)**
Overrides the default login endpoint /login

**logout_endpoint: str (optional, default=None)**
Overrides the default logout endpoint /logout

**logout_template: str (optional, default=None)**
Jinja2 template served when viewing the login endpoint when
authentication is enabled.

**logout_template: str (optional, default=None)**
Jinja2 template served when viewing the logout endpoint when
authentication is enabled.

**session_history: int (optional, default=None)**
The amount of session history to accumulate. If set to non-zero and
non-None value will launch a REST endpoint at /rest/session_info, which
returns information about the session history.

**liveness: bool \| str (optional, default=False)**
Whether to add a liveness endpoint. If a string is provided then this
will be used as the endpoint, otherwise the endpoint will be hosted at
/liveness.

**warm: bool (optional, default=False)**
Whether to run the applications before serving them to ensure all
imports and caches are fully warmed up before serving the app.

**kwargs: dict**
Additional keyword arguments to pass to Server instance.

Returns:
server : panel.io.server.Server
Bokeh Server instance running this panel

panel.io.server.get_static_routes(static_dirs)
Returns a list of tornado routes of StaticFileHandlers given a
dictionary of slugs and file paths to serve.

panel.io.server.html_page_for_render_items(bundle: Bundle \| tuple\[str, str\], docs_json: dict\[ID, DocJson\], render_items: list\[RenderItem\], title: str, template: Template \| str \| None = None, template_variables: dict\[str, t.Any\] = {}) → str
Render an HTML page from a template and Bokeh render items.

Parameters:
**bundle (tuple):**
A tuple containing (bokehjs, bokehcss)

**docs_json (JSON-like):**
Serialized Bokeh Document

**render_items (RenderItems)**
Specific items to render from the document and where

**title (str or None)**
A title for the HTML page. If None, DEFAULT_TITLE is used

**template (str or Template or None, optional)**
A Template to be used for the HTML page. If None, FILE is used.

**template_variables (dict, optional):**
Any Additional variables to pass to the template

Returns:
str

panel.io.server.serve(panels: TViewableFuncOrPath \| dict\[str, TViewableFuncOrPath\], port: int = 0, address: str \| None = None, websocket_origin: str \| list\[str\] \| None = None, loop: IOLoop \| None = None, show: bool = True, start: bool = True, title: str \| None = None, verbose: bool = True, location: bool = True, threaded: bool = False, admin: bool = False, **kwargs) → StoppableThread \| Server
Allows serving one or more panel objects on a single server. The panels
argument should be either a Panel object or a function returning a Panel
object or a dictionary of these two. If a dictionary is supplied the
keys represent the slugs at which each app is served, e.g. serve({‘app’:
panel1, ‘app2’: panel2}) will serve apps at /app and /app2 on the
server.

Reference: [https://panel.holoviz.org/user_guide/Server_Configuration.html#serving-multiple-apps](https://panel.holoviz.org/user_guide/Server_Configuration.html#serving-multiple-apps)

Parameters:
**panels: Viewable, function or {str: Viewable or function}**
A Panel object, a function returning a Panel object or a dictionary
mapping from the URL slug to either.

**port: int (optional, default=0)**
Allows specifying a specific port

address : str
The address the server should listen on for HTTP requests.

**websocket_origin: str or list(str) (optional)**
A list of hosts that can connect to the websocket.

This is typically required when embedding a server app in an external
web site.

If None, “localhost” is used.

loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
The tornado IOLoop to run the Server on

show : boolean (optional, default=True)
Whether to open the server in a new browser tab on start

start : boolean(optional, default=True)
Whether to start the Server

**title: str or {str: str} (optional, default=None)**
An HTML title for the application or a dictionary mapping from the URL
slug to a customized title

**verbose: boolean (optional, default=True)**
Whether to print the address and port

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

**threaded: boolean (default=False)**
Whether to start the server on a new Thread

**admin: boolean (default=False)**
Whether to enable the admin panel

**kwargs: dict**
Additional keyword arguments to pass to Server instance

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
