# Config

The `pn.config` object holds global configuration options for Panel.

The options can be set directly on the global config instance, via
keyword arguments to [`pn.extension`](cheatsheet#pn-extension) or via environment variables.

For example to set the `embed` option the following approaches can be used:

```python
pn.config.embed = True
pn.extension(embed=True)
os.environ['PANEL_EMBED'] = 'True'
```

## Options Summary

### `admin`

Whether the admin panel is enabled.

Default: False | Type: Boolean

### `admin_endpoint` (`PANEL_ADMIN_ENDPOINT`)

Name to use for the admin endpoint.

Default: None | Type: String

### `admin_log_level` (`PANEL_ADMIN_LOG_LEVEL`)

Log level of the Admin Panel logger

Default: 'DEBUG' | Type: Literal | Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

### `admin_plugins`

A list of tuples containing a title and a function that returns
an additional panel to be rendered into the admin page.

Default: [] | Type: List

### `apply_signatures`

Whether to set custom Signature which allows tab-completion
in some IDEs and environments.

Default: True | Type: Boolean

### `auth_template`

A jinja2 template rendered when the authorize_callback determines
that a user in not authorized to access the application.

Default: None | Type: Path

### `authorize_callback`

Authorization callback that is invoked when authentication
is enabled. The callback is given the user information returned
by the configured Auth provider and should return True or False
depending on whether the user is authorized to access the
application. The callback may also contain a second parameter,
which is the requested path the user is making. If the user
is authenticated and has explicit access to the path, then
the callback should return True otherwise it should return
False.

Default: None | Type: Callable

### `autoreload`

Whether to autoreload the page whenever the script or one of its dependencies changes.

Default: False | Type: Boolean

### `basic_auth` (`PANEL_BASIC_AUTH`)

Password, dictionary with a mapping from username to password
or filepath containing JSON to use with the basic auth
provider.

Default: None | Type: ClassSelector

### `basic_auth_template`

A jinja2 template to override the default Basic Authentication
login page.

Default: None | Type: Path

### `browser_info`

Whether to request browser info from the frontend.

Default: True | Type: Boolean

### `comms` (`PANEL_COMMS`)

Whether to render output in Jupyter with the default Jupyter
extension or use the jupyter_bokeh ipywidget model.

Default: 'default' | Type: Literal | Options: 'default', 'ipywidgets', 'vscode', 'colab'

### `console_output` (`PANEL_CONSOLE_OUTPUT`)

How to log errors and stdout output triggered by callbacks
from Javascript in the notebook.

Default: 'accumulate' | Type: Literal | Options: 'accumulate', 'replace', 'disable', 'False'

### `cookie_secret` (`PANEL_COOKIE_SECRET`)

Configure to enable getting/setting secure cookies.

Default: None | Type: String

### `css_files`

External CSS files to load.

Default: [] | Type: List

### `defer_load`

Whether to defer load of rendered functions.

Default: False | Type: Boolean

### `design`

The design system to use to style components.

Default: None | Type: ClassSelector

### `disconnect_notification`

The notification to display to the user when the connection
to the server is dropped.

Default: '' | Type: String

### `embed` (`PANEL_EMBED`)

Whether plot data will be embedded.

Default: False | Type: Boolean

### `embed_json` (`PANEL_EMBED_JSON`)

Whether to save embedded state to json files.

Default: False | Type: Boolean

### `embed_json_prefix` (`PANEL_EMBED_JSON_PREFIX`)

Prefix for randomly generated json directories.

Default: '' | Type: String

### `embed_load_path` (`PANEL_EMBED_LOAD_PATH`)

Where to load json files for embedded state.

Default: None | Type: String

### `embed_save_path` (`PANEL_EMBED_SAVE_PATH`)

Where to save json files for embedded state.

Default: './' | Type: String

### `exception_handler`

General exception handler for events.

Default: None | Type: Callable

### `global_css`

List of raw CSS to be added to the header.

Default: [] | Type: List

### `global_loading_spinner`

Whether to add a global loading spinner for the whole application.

Default: False | Type: Boolean

### `inline` (`PANEL_INLINE`)

Whether to inline JS and CSS resources. If disabled, resources
are loaded from CDN if one is available.

Default: True | Type: Boolean

### `js_files`

External JS files to load. Dictionary should map from exported
name to the URL of the JS file.

Default: {} | Type: Dict

### `js_modules`

External JS files to load as modules. Dictionary should map from
exported name to the URL of the JS file.

Default: {} | Type: Dict

### `layout_compatibility`

Provide compatibility for older layout specifications. Incompatible
specifications will trigger warnings by default but can be set to error.
Compatibility to be set to error by default in Panel 1.1.

Default: 'warn' | Type: Literal | Options: 'warn', 'error'

### `load_entry_points`

Load entry points from external packages.

Default: True | Type: Boolean

### `loading_color`

Color of the loading indicator.

Default: '#c3c3c3' | Type: Color

### `loading_indicator`

Whether a loading indicator is shown by default while panes are updating.

Default: False | Type: Boolean

### `loading_max_height`

Maximum height of the loading indicator.

Default: 400 | Type: Integer

### `loading_spinner`

Loading indicator to use when component loading parameter is set.

Default: 'arc' | Type: Literal | Options: 'arc', 'arcs', 'bar', 'dots', 'petal'

### `log_level` (`PANEL_LOG_LEVEL`)

Log level of Panel loggers

Default: 'WARNING' | Type: Literal | Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

### `notifications`

Whether to enable notifications functionality.

Default: False | Type: Boolean

### `npm_cdn` (`PANEL_NPM_CDN`)

The CDN to load NPM packages from if resources are served from
CDN. Allows switching between [https://unpkg.com](https://unpkg.com) and
[https://cdn.jsdelivr.net/npm](https://cdn.jsdelivr.net/npm) for most resources.

Default: 'https://cdn.jsdelivr.net/npm' | Type: Literal | Options: 'https://unpkg.com', 'https://cdn.jsdelivr.net/npm'

### `nthreads` (`PANEL_NTHREADS`)

When set to a non-None value a thread pool will be started.
Whenever an event arrives from the frontend it will be
dispatched to the thread pool to be processed.

Default: None | Type: Integer

### `oauth_encryption_key` (`PANEL_OAUTH_ENCRYPTION`)

A random string used to encode OAuth related user information.

Default: None | Type: ClassSelector

### `oauth_expiry` (`PANEL_OAUTH_EXPIRY`)

Expiry of the OAuth cookie in number of days.

Default: 1 | Type: Number

### `oauth_extra_params` (`PANEL_OAUTH_EXTRA_PARAMS`)

Additional parameters required for OAuth provider.

Default: {} | Type: Dict

### `oauth_guest_endpoints` (`PANEL_OAUTH_GUEST_ENDPOINTS`)

List of endpoints that can be accessed as a guest without authenticating.

Default: None | Type: List

### `oauth_jwt_user` (`PANEL_OAUTH_JWT_USER`)

The key in the ID JWT token to consider the user.

Default: None | Type: String

### `oauth_key` (`PANEL_OAUTH_KEY`)

A client key to provide to the OAuth provider.

Default: None | Type: String

### `oauth_optional` (`PANEL_OAUTH_OPTIONAL`)

Whether the user will be forced to go through login flow or if
they can access all applications as a guest.

Default: False | Type: Boolean

### `oauth_provider` (`PANEL_OAUTH_PROVIDER`)

Select between a list of authentication providers.

Default: None | Type: Literal | Options: 'None'

### `oauth_redirect_uri` (`PANEL_OAUTH_REDIRECT_URI`)

A redirect URI to provide to the OAuth provider.

Default: None | Type: String

### `oauth_refresh_tokens` (`PANEL_OAUTH_REFRESH_TOKENS`)

Whether to automatically refresh access tokens in the background.

Default: False | Type: Boolean

### `oauth_secret` (`PANEL_OAUTH_SECRET`)

A client secret to provide to the OAuth provider.

Default: None | Type: String

### `profiler`

The profiler engine to enable.

Default: None | Type: Literal | Options: 'pyinstrument', 'snakeviz', 'memray'

### `raw_css`

List of raw CSS strings to add to load.

Default: [] | Type: List

### `ready_notification`

The notification to display when the application is ready and
fully loaded.

Default: '' | Type: String

### `reuse_sessions`

Whether to reuse a session for the initial request to speed up
the initial page render. Note that if the initial page differs
between sessions, e.g. because it uses query parameters to modify
the rendered content, then this option will result in the wrong
content being rendered. Define a session_key_func to ensure that
reused sessions are only reused when appropriate.

Default: False | Type: Boolean

### `safe_embed`

Ensure all bokeh property changes trigger events which are
embedded. Useful when only partial updates are made in an
app, e.g. when working with HoloViews.

Default: False | Type: Boolean

### `session_history`

If set to a non-negative value this determines the maximum length
of the pn.state.session_info dictionary, which tracks
information about user sessions. A value of -1 indicates an
unlimited history.

Default: 0 | Type: Integer

### `session_key_func`

Used in conjunction with the reuse_sessions option, the
session_key_func is given a tornado.httputil.HTTPServerRequest
and should return a key that uniquely captures a session.

Default: None | Type: Callable

### `sizing_mode`

Specify the default sizing mode behavior of panels.

Default: None | Type: Literal | Options: 'fixed', 'stretch_width', 'stretch_height', 'stretch_both', 'scale_width', 'scale_height', 'scale_both', 'None'

### `template`

The default template to render served applications into.

Default: None | Type: Literal | Options: 'bootstrap', 'fast', 'fast-list', 'material', 'golden', 'slides', 'vanilla'

### `theme`

The theme to apply to components.

Default: None | Type: Literal | Options: 'default', 'dark'

### `throttled`

If sliders and inputs should be throttled until release of mouse.

Default: False | Type: Boolean
