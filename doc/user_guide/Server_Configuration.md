# Server Configuration

The Panel server can be launched either from the commandline (using `panel serve`) or programmatically (using `panel.serve()`). In this guide we will discover how to run and configure server instances using these two options.

## Launching a server on the commandline

Once the app is ready for deployment it can be served using the Bokeh server.  For a detailed breakdown of the design and functionality of Bokeh server, see the [Bokeh documentation](https://bokeh.pydata.org/en/latest/docs/user_guide/server.html). The most important thing to know is that Panel (and Bokeh) provide a CLI command to serve a Python script, app directory, or Jupyter notebook containing a Bokeh or Panel app. To launch a server using the CLI, simply run:

    panel serve app.ipynb

Alternatively you can also list multiple apps:

    panel serve app1.py app2.ipynb

or even serve a number of apps at once:

    panel serve apps/*.py

For development it can be particularly helpful to use the ``--autoreload`` option to `panel serve` as that will automatically reload the page whenever the application code or any of its imports change.

The ``panel serve`` command has the following options:

    positional arguments:
      DIRECTORY-OR-SCRIPT   The app directories or scripts or notebooks to serve
                            (serve empty document if not specified)

    optional arguments:
      -h, --help            show this help message and exit
      --port PORT           Port to listen on
      --address ADDRESS     Address to listen on
      --log-level LOG-LEVEL
                            One of: trace, debug, info, warning, error or critical
      --log-format LOG-FORMAT
                            A standard Python logging format string (default:
                            '%(asctime)s %(message)s')
      --log-file LOG-FILE   A filename to write logs to, or None to write to the
                            standard stream (default: None)
      --args ...            Any command line arguments remaining are passed on to
                            the application handler
      --show                Open server app(s) in a browser
      --allow-websocket-origin HOST[:PORT]
                            Public hostnames which may connect to the Bokeh
                            websocket
      --prefix PREFIX       URL prefix for Bokeh server URLs
      --keep-alive MILLISECONDS
                            How often to send a keep-alive ping to clients, 0 to
                            disable.
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
                            Whether to enable Tornado support for XSRF cookies.
                            All PUT, POST, or DELETE handlers must be properly
                            instrumented when this setting is enabled.
      --exclude-headers EXCLUDE_HEADERS [EXCLUDE_HEADERS ...]
                            A list of request headers to exclude from the session
                            context (by default all headers are included).
      --exclude-cookies EXCLUDE_COOKIES [EXCLUDE_COOKIES ...]
                            A list of request cookies to exclude from the session
                            context (by default all cookies are included).
      --include-headers INCLUDE_HEADERS [INCLUDE_HEADERS ...]
                            A list of request headers to make available in the
                            session context (by default all headers are included).
      --include-cookies INCLUDE_COOKIES [INCLUDE_COOKIES ...]
                            A list of request cookies to make available in the
                            session context (by default all cookies are included).
      --session-ids MODE    One of: unsigned, signed, or external-signed
      --index INDEX         Path to a template to use for the site index or
                            an app to serve at the root.
      --disable-index       Do not use the default index on the root path
      --disable-index-redirect
                            Do not redirect to running app from root path
      --num-procs N         Number of worker processes for an app. Using 0 will
                            autodetect number of cores (defaults to 1)
      --num-threads N       Number of threads to launch in a ThreadPoolExecutor which
                            Panel will dispatch events to for concurrent execution on
                            separate cores (defaults to None).
      --warm                Whether to execute scripts on startup to warm up the server.
      --autoreload
                            Whether to automatically reload user sessions when the
			    application or any of its imports change.
      --static-dirs KEY=VALUE [KEY=VALUE ...]
                            Static directories to serve specified as key=value
                            pairs mapping from URL route to static file directory.

      --dev [FILES-TO-WATCH [FILES-TO-WATCH ...]]
                            Enable live reloading during app development.By
                            default it watches all *.py *.html *.css *.yaml
                            filesin the app directory tree. Additional files can
                            be passedas arguments. NOTE: This setting only works
                            with a single app.It also restricts the number of
                            processes to 1.
      --session-token-expiration N
                            Duration in seconds that a new session token is valid
                            for session creation. After the expiry time has elapsed,
                            the token will not be able create a new session
                            (defaults to seconds).
      --websocket-max-message-size BYTES
                            Set the Tornado websocket_max_message_size value
                            (defaults to 20MB) NOTE: This setting has effect ONLY
                            for Tornado>=4.5
      --websocket-compression-level LEVEL
                            Set the Tornado WebSocket compression_level
      --websocket-compression-mem-level LEVEL
                            Set the Tornado WebSocket compression mem_level
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
      --rest-provider REST_PROVIDER
                            The interface to use to serve REST API
      --rest-endpoint REST_ENDPOINT
                            Endpoint to store REST API on.
      --rest-session-info
                            Whether to serve session info on the REST API
      --session-history SESSION_HISTORY
                            The length of the session history to record.
      --setup
                            Path to a setup script to run before server starts, e.g. to cache data or set up scheduled tasks.
      --liveness
                            Whether to add an endpoint to confirm liveness of the server and optionally various endpoints
                            (defaults to /liveness but endpoint can be controlled with --liveness-endpoint)
      --liveness-endpoint
                            The endpoint to serve the liveness API at.
      --admin
                            Whether to add an admin panel.
      --admin-log-level
                            One of: debug, info, warning, error or critical
      --profiler PROFILER
                            The profiler to use by default, e.g. pyinstrument or snakeviz.

To turn a notebook into a deployable app simply append ``.servable()`` to one or more Panel objects, which will add the app to Bokeh's ``curdoc``, ensuring it can be discovered by Bokeh server on deployment. In this way it is trivial to build dashboards that can be used interactively in a notebook and then seamlessly deployed on Bokeh server.

When called on a notebook, `panel serve` first converts it to a python script using [`nbconvert.PythonExporter()`](https://nbconvert.readthedocs.io/en/stable/api/exporters.html), albeit with [IPython magics](https://ipython.readthedocs.io/en/stable/interactive/magics.html) stripped out. This means that non-code cells, such as raw cells, are entirely handled by `nbconvert` and [may modify the served app](https://nbsphinx.readthedocs.io/en/latest/raw-cells.html).

## Launching a server dynamically

The CLI `panel serve` command described below is usually the best approach for deploying applications. However when working on the REPL or embedding a Panel/Bokeh server in another application it is sometimes useful to dynamically launch a server, either using the `.show` method or using the `pn.serve` function.

### Previewing an application

Working from the command line will not automatically display rich representations inline as in a notebook, but you can still interact with your Panel components if you start a Bokeh server instance and open a separate browser window using the ``show`` method. The method has the following arguments:

    port: int (optional)
       Allows specifying a specific port (default=0 chooses an arbitrary open port)
    websocket_origin: str or list(str) (optional)
       A list of hosts that can connect to the websocket.
       This is typically required when embedding a server app in
       an external-facing web site.
       If None, "localhost" is used.
    threaded: boolean (optional, default=False)
       Whether to launch the Server on a separate thread, allowing
       interactive use.
    title : str
       A string title to give the Document (if served as an app)
    **kwargs : dict
       Additional keyword arguments passed to the bokeh.server.server.Server instance.

To work with an app completely interactively you can set ``threaded=True`` which will launch the server on a separate thread and let you interactively play with the app.

<img src='https://assets.holoviews.org/panel/gifs/commandline_show.gif'></img>

The ``.show`` call will return either a Bokeh server instance (if ``threaded=False``) or a ``StoppableThread`` instance (if ``threaded=True``) which both provide a ``stop`` method to stop the server instance.

### Serving multiple apps

If you want to serve more than one app on a single server you can use the ``pn.serve`` function. By supplying a dictionary where the keys represent the URL slugs and the values must be either Panel objects or functions returning Panel objects you can easily launch a server with a number of apps, e.g.:

```python
import panel as pn
pn.serve({
    'markdown': '# This is a Panel app',
    'json': pn.pane.JSON({'abc': 123})
})
```

Note that when you serve an object directly all sessions will share the same state, i.e. the parameters of all components will be synced across sessions such that the change in a widget by one user will affect all other users. Therefore you will usually want to wrap your app in a function, ensuring that each user gets a new instance of the application:

```python

def markdown_app():
    return '# This is a Panel app'

def json_app():
    return pn.pane.JSON({'abc': 123})

pn.serve({
    'markdown': markdown_app,
    'json': json_app
})
```

You can customize the HTML title of each application by supplying a dictionary where the keys represent the URL slugs and the values represent the titles, e.g.:

```python
pn.serve({
    'markdown': '# This is a Panel app',
    'json': pn.pane.JSON({'abc': 123})
}, title={'markdown': 'A Markdown App', 'json': 'A JSON App'}
)
```

The ``pn.serve`` accepts a number of arguments:

    panel: Viewable, function or {str: Viewable or function}
      A Panel object, a function returning a Panel object or a
      dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port
    address: str
      The address the server should listen on for HTTP requests.
    websocket_origin: str or list(str) (optional)
      A list of hosts that can connect to the websocket.

      This is typically required when embedding a server app in
      an external web site.

      If None, "localhost" is used.
    loop: tornado.ioloop.IOLoop (optional, default=IOLoop.current())
      The tornado IOLoop to run the Server on
    show: boolean (optional, default=False)
      Whether to open the server in a new browser tab on start
    start: boolean(optional, default=False)
      Whether to start the Server
    title: str or {str: str} (optional, default=None)
      An HTML title for the application or a dictionary mapping
      from the URL slug to a customized title
    verbose: boolean (optional, default=True)
      Whether to print the address and port
    location: boolean or panel.io.location.Location
      Whether to create a Location component to observe and
      set the URL location.
    kwargs: dict
      Additional keyword arguments to pass to Server instance

## Static file hosting

Whether you're launching your application using `panel serve` from the commandline or using `pn.serve` in a script you can also serve static files. When using `panel serve` you can use the `--static-dirs` argument to specify a list of static directories to serve along with their routes, e.g.:

    panel serve some_script.py --static-dirs assets=./assets

This will serve the `./assets` directory on the servers `/assets` route. Note however that the `/static` route is reserved internally by Panel.

Similarly when using `pn.serve` or `panel_obj.show` the static routes may be defined as a dictionary, e.g. the equivalent to the example would be:

    pn.serve(panel_obj, static_dirs={'assets': './assets'})
