# Launching a server on the commandline

Once the app is ready for deployment it can be served using the Bokeh server.  For a detailed breakdown of the design and functionality of Bokeh server, see the [Bokeh documentation](https://bokeh.pydata.org/en/latest/docs/user_guide/server.html). The most important thing to know is that Panel (and Bokeh) provide a CLI command to serve a Python script, app directory, or Jupyter notebook containing a Bokeh or Panel app. To launch a server using the CLI, simply run:

    panel serve app.ipynb

Alternatively you can also list multiple apps:

    panel serve app1.py app2.ipynb

or even serve a number of apps at once:

    panel serve apps/*.py

For development it can be particularly helpful to use the ``--autoreload`` option to `panel serve` as that will automatically reload the page whenever the application code or any of its imports change.

```{note}
We recommend installing `watchfiles`, which will provide a significantly better user experience when using `--autoreload`.
```

The ``panel serve`` command has the following options:

``` console
positional arguments:
  DIRECTORY-OR-SCRIPT   The app directories or scripts to serve (serve empty document if not specified)

options:
  -h, --help            show this help message and exit
  --port PORT           Port to listen on
  --address ADDRESS     Address to listen on
  --unix-socket UNIX-SOCKET
                        Unix socket to bind. Network options such as port, address, ssl options are incompatible with unix socket
  --log-level LOG-LEVEL
                        One of: trace, debug, info, warning, error or critical
  --log-format LOG-FORMAT
                        A standard Python logging format string (default: '%(asctime)s %(message)s')
  --log-file LOG-FILE   A filename to write logs to, or None to write to the standard stream (default: None)
  --use-config CONFIG   Use a YAML config file for settings
  --args ...            Command line arguments remaining to passed on to the application handler. NOTE: if this argument precedes DIRECTORY-OR-SCRIPT then some other argument, e.g. --show, must be placed before the directory or script.
  --dev [FILES-TO-WATCH ...]
                        Enable live reloading during app development. By default it watches all *.py *.html *.css *.yaml files in the app directory tree. Additional files can be passed as arguments. NOTE: if this argument precedes DIRECTORY-OR-SCRIPT then some other argument, e.g
                        --show, must be placed before the directory or script. NOTE: This setting only works with a single app. It also restricts the number of processes to 1. NOTE FOR WINDOWS USERS : this option must be invoked using 'python -m bokeh'. If not Tornado will fail to
                        restart the server
  --show                Open server app(s) in a browser
  --allow-websocket-origin HOST[:PORT]
                        Public hostnames which may connect to the Bokeh websocket With unix socket, the websocket origin restrictions should be enforced by the proxy.
  --prefix PREFIX       URL prefix for Bokeh server URLs
  --ico-path ICO_PATH   Path to a .ico file to use as the favicon.ico, or 'none' to disable favicon.ico support. If unset, a default Bokeh .ico file will be used
  --keep-alive MILLISECONDS
                        How often to send a keep-alive ping to clients, 0 to disable.
  --check-unused-sessions MILLISECONDS
                        How often to check for unused sessions
  --unused-session-lifetime MILLISECONDS
                        How long unused sessions last
  --stats-log-frequency MILLISECONDS
                        How often to log stats
  --mem-log-frequency MILLISECONDS
                        How often to log memory usage information
  --use-xheaders        Prefer X-headers for IP/protocol information
  --ssl-certfile CERTFILE
                        Absolute path to a certificate file for SSL termination
  --ssl-keyfile KEYFILE
                        Absolute path to a private key file for SSL termination
  --session-ids MODE    One of: unsigned, signed or external-signed
  --auth-module AUTH_MODULE
                        Absolute path to a Python module that implements auth hooks
  --enable-xsrf-cookies
                        Whether to enable Tornado support for XSRF cookies. All PUT, POST, or DELETE handlers must be properly instrumented when this setting is enabled.
  --exclude-headers EXCLUDE_HEADERS [EXCLUDE_HEADERS ...]
                        A list of request headers to exclude from the session context (by default all headers are included).
  --exclude-cookies EXCLUDE_COOKIES [EXCLUDE_COOKIES ...]
                        A list of request cookies to exclude from the session context (by default all cookies are included).
  --include-headers INCLUDE_HEADERS [INCLUDE_HEADERS ...]
                        A list of request headers to make available in the session context (by default all headers are included).
  --include-cookies INCLUDE_COOKIES [INCLUDE_COOKIES ...]
                        A list of request cookies to make available in the session context (by default all cookies are included).
  --cookie-secret COOKIE_SECRET
                        Configure to enable getting/setting secure cookies
  --index INDEX         Path to a template to use for the site index
  --disable-index       Do not use the default index on the root path
  --disable-index-redirect
                        Do not redirect to running app from root path
  --num-procs N         Number of worker processes for an app. Using 0 will autodetect number of cores (defaults to 1)
  --session-token-expiration N
                        Duration in seconds that a new session token is valid for session creation. After the expiry time has elapsed, the token will not be able create a new session (defaults to seconds).
  --websocket-max-message-size BYTES
                        Set the Tornado websocket_max_message_size value (default: 20MB)
  --websocket-compression-level LEVEL
                        Set the Tornado WebSocket compression_level
  --websocket-compression-mem-level LEVEL
                        Set the Tornado WebSocket compression mem_level
  --glob                Process all filename arguments as globs
  --static-dirs KEY=VALUE [KEY=VALUE ...]
                        Static directories to serve specified as key=value pairs mapping from URL route to static file directory.
  --basic-auth BASIC_AUTH
                        Password or filepath to use with Basic Authentication.
  --oauth-provider OAUTH_PROVIDER
                        The OAuth2 provider to use.
  --oauth-key OAUTH_KEY
                        The OAuth2 key to use
  --oauth-secret OAUTH_SECRET
                        The OAuth2 secret to use
  --oauth-redirect-uri OAUTH_REDIRECT_URI
                        The OAuth2 redirect URI
  --oauth-extra-params OAUTH_EXTRA_PARAMS
                        Additional parameters to use.
  --oauth-jwt-user OAUTH_JWT_USER
                        The key in the ID JWT token to consider the user.
  --oauth-encryption-key OAUTH_ENCRYPTION_KEY
                        A random string used to encode the user information.
  --oauth-error-template OAUTH_ERROR_TEMPLATE
                        A random string used to encode the user information.
  --oauth-expiry-days OAUTH_EXPIRY_DAYS
                        Expiry off the OAuth cookie in number of days.
  --oauth-refresh-tokens OAUTH_REFRESH_TOKENS
                        Whether to automatically refresh OAuth access tokens when they expire.
  --auth-template AUTH_TEMPLATE
                        Template to serve when user is unauthenticated.
  --basic-login-template BASIC_LOGIN_TEMPLATE
                        Template to serve for Basic Authentication login page.
  --rest-provider REST_PROVIDER
                        The interface to use to serve REST API
  --rest-endpoint REST_ENDPOINT
                        Endpoint to store REST API on.
  --rest-session-info   Whether to serve session info on the REST API
  --session-history SESSION_HISTORY
                        The length of the session history to record.
  --warm                Whether to execute scripts on startup to warm up the server.
  --admin               Whether to add an admin panel.
  --admin-log-level {debug,info,warning,error,critical}
                        One of: debug (default), info, warning, error or critical
  --profiler PROFILER   The profiler to use by default, e.g. pyinstrument, snakeviz or memray.
  --autoreload          Whether to autoreload source when script changes.
  --num-threads NUM_THREADS
                        Whether to start a thread pool which events are dispatched to.
  --setup SETUP         Path to a setup script to run before server starts.
  --liveness            Whether to add a liveness endpoint.
  --liveness-endpoint LIVENESS_ENDPOINT
                        The endpoint for the liveness API.
  --reuse-sessions      Whether to reuse sessions when serving the initial request.
  --global-loading-spinner
                        Whether to add a global loading spinner to the application(s).
```

To turn a notebook into a deployable app simply append ``.servable()`` to one or more Panel objects, which will add the app to Bokeh's ``curdoc``, ensuring it can be discovered by Bokeh server on deployment. In this way it is trivial to build dashboards that can be used interactively in a notebook and then seamlessly deployed on Bokeh server.

When called on a notebook, `panel serve` first converts it to a python script using [`nbconvert.PythonExporter()`](https://nbconvert.readthedocs.io/en/stable/api/exporters.html), albeit with [IPython magics](https://ipython.readthedocs.io/en/stable/interactive/magics.html) stripped out. This means that non-code cells, such as raw cells, are entirely handled by `nbconvert` and [may modify the served app](https://nbsphinx.readthedocs.io/en/latest/raw-cells.html).
