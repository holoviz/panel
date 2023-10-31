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

`admin`
: Whether the admin panel was enabled.

`admin_endpoint` (`PANEL_ADMIN_ENDPOINT`)
: Name to use for the admin endpoint.

`admin_log_level` (`PANEL_ADMIN_LOG_LEVEL`)
: Log level of the Admin Panel logger

`admin_plugins`
: A list of tuples containing a title and a function that returns
        an additional panel to be rendered into the admin page.

`apply_signatures`
: Whether to set custom Signature which allows tab-completion
        in some IDEs and environments.

`auth_template`
: A jinja2 template rendered when the authorize_callback determines
        that a user in not authorized to access the application.

`authorize_callback`
: Authorization callback that is invoked when authentication
        is enabled. The callback is given the user information returned
        by the configured Auth provider and should return True or False
        depending on whether the user is authorized to access the
        application. The callback may also contain a second parameter,
        which is the requested path the user is making. If the user
        is authenticated and has explicit access to the path, then
        the callback should return True otherwise it should return
        False.

`autoreload`
: Whether to autoreload server when script changes.

`basic_auth` (`PANEL_BASIC_AUTH`)
: Password, dictionary with a mapping from username to password
        or filepath containing JSON to use with the basic auth
        provider.

`basic_auth_template`
: A jinja2 template to override the default Basic Authentication
        login page.

`browser_info`
: Whether to request browser info from the frontend.

`comms` (`PANEL_COMMS`)
: Whether to render output in Jupyter with the default Jupyter
        extension or use the jupyter_bokeh ipywidget model.

`console_output` (`PANEL_CONSOLE_OUTPUT`)
: How to log errors and stdout output triggered by callbacks
        from Javascript in the notebook.

`cookie_secret` (`PANEL_COOKIE_SECRET`)
: Configure to enable getting/setting secure cookies.

`css_files`
: External CSS files to load.

`defer_load`
: Whether to defer load of rendered functions.

`design`
: The design system to use to style components.

`disconnect_notification`
: The notification to display to the user when the connection
        to the server is dropped.

`embed` (`PANEL_EMBED`)
: Whether plot data will be embedded.

`embed_json` (`PANEL_EMBED_JSON`)
: Whether to save embedded state to json files.

`embed_json_prefix` (`PANEL_EMBED_JSON_PREFIX`)
: Prefix for randomly generated json directories.

`embed_load_path` (`PANEL_EMBED_LOAD_PATH`)
: Where to load json files for embedded state.

`embed_save_path` (`PANEL_EMBED_SAVE_PATH`)
: Where to save json files for embedded state.

`exception_handler`
: General exception handler for events.

`global_css`
: List of raw CSS to be added to the header.

`global_loading_spinner`
: Whether to add a global loading spinner for the whole application.

`inline` (`PANEL_INLINE`)
: Whether to inline JS and CSS resources. If disabled, resources
        are loaded from CDN if one is available.

`js_files`
: External JS files to load. Dictionary should map from exported
        name to the URL of the JS file.

`js_modules`
: External JS files to load as modules. Dictionary should map from
        exported name to the URL of the JS file.

`layout_compatibility`
: Provide compatibility for older layout specifications. Incompatible
        specifications will trigger warnings by default but can be set to error.
        Compatibility to be set to error by default in Panel 1.1.

`load_entry_points`
: Load entry points from external packages.

`loading_color`
: Color of the loading indicator.

`loading_indicator`
: Whether a loading indicator is shown by default while panes are updating.

`loading_max_height`
: Maximum height of the loading indicator.

`loading_spinner`
: Loading indicator to use when component loading parameter is set.

`log_level` (`PANEL_LOG_LEVEL`)
: Log level of Panel loggers

`name`
: String identifier for this object.

`notifications`
: Whether to enable notifications functionality.

`npm_cdn` (`PANEL_NPM_CDN`)
: The CDN to load NPM packages from if resources are served from
        CDN. Allows switching between [https://unpkg.com](https://unpkg.com) and
        [https://cdn.jsdelivr.net/npm(https://cdn.jsdelivr.net/npm) for most resources.

`nthreads` (`PANEL_NUM_THREADS`)
: When set to a non-None value a thread pool will be started.
        Whenever an event arrives from the frontend it will be
        dispatched to the thread pool to be processed.

`oauth_encryption_key` (`PANEL_OAUTH_ENCRYPTION`)
: A random string used to encode OAuth related user information.

`oauth_expiry` (`PANEL_OAUTH_EXPIRY`)
: Expiry of the OAuth cookie in number of days.

`oauth_extra_params` (`PANEL_OAUTH_EXTRA_PARAMS`)
: Additional parameters required for OAuth provider.

`oauth_guest_endpoints` (`PANEL_OAUTH_GUEST_ENDPOINTS`)
: List of endpoints that can be accessed as a guest without authenticating.

`oauth_jwt_user` (`PANEL_OAUTH_JWT_USER`)
: The key in the ID JWT token to consider the user.

`oauth_key` (`PANEL_OAUTH_KEY`)
: A client key to provide to the OAuth provider.

`oauth_optional` (`PANEL_OAUTH_OPTIONAL`)
: Whether the user will be forced to go through login flow or if
        they can access all applications as a guest.

`oauth_provider` (`PANEL_OAUTH_PROVIDER`)
: Select between a list of authentication providers.

`oauth_redirect_uri` (`PANEL_OAUTH_REDIRECT_URI`)
: A redirect URI to provide to the OAuth provider.

`oauth_refresh_tokens` (`PANEL_OAUTH_REFRESH_TOKENS`)
: Whether to automatically refresh access tokens in the background.

`oauth_secret` (`PANEL_OAUTH_SECRET`)
: A client secret to provide to the OAuth provider.

`profiler`
: The profiler engine to enable.

`raw_css`
: List of raw CSS strings to add to load.

`ready_notification`
: The notification to display when the application is ready and
        fully loaded.

`reuse_sessions`
: Whether to reuse a session for the initial request to speed up
        the initial page render. Note that if the initial page differs
        between sessions, e.g. because it uses query parameters to modify
        the rendered content, then this option will result in the wrong
        content being rendered. Define a session_key_func to ensure that
        reused sessions are only reused when appropriate.

`safe_embed`
: Ensure all bokeh property changes trigger events which are
        embedded. Useful when only partial updates are made in an
        app, e.g. when working with HoloViews.

`session_history`
: If set to a non-negative value this determines the maximum length
        of the pn.state.session_info dictionary, which tracks
        information about user sessions. A value of -1 indicates an
        unlimited history.

`session_key_func`
: Used in conjunction with the reuse_sessions option, the
        session_key_func is given a tornado.httputil.HTTPServerRequest
        and should return a key that uniquely captures a session.

`sizing_mode`
: Specify the default sizing mode behavior of panels.

`template`
: The default template to render served applications into.

`theme`
: The theme to apply to components.

`throttled`
: If sliders and inputs should be throttled until release of mouse.

## Options Details

To see the full details including types and default values run `?pn.config` in an ipython terminal or Notebook.
