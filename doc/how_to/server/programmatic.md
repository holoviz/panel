# Launching a server dynamically

The CLI `panel serve` command described below is usually the best approach for deploying applications. However when working on the REPL or embedding a Panel/Bokeh server in another application it is sometimes useful to dynamically launch a server, either using the `.show` method or using the `pn.serve` function.

## Previewing an application

Working from the command line will not automatically display rich representations inline as in a notebook, but you can still interact with your Panel components if you start a Bokeh server instance and open a separate browser window using the ``show`` method. The method has the following arguments:

``` console
title : str | None
  A string title to give the Document (if served as an app)
port: int (optional, default=0)
  Allows specifying a specific port
address : str
  The address the server should listen on for HTTP requests.
websocket_origin: str or list(str) (optional)
  A list of hosts that can connect to the websocket.
  This is typically required when embedding a server app in
  an external web site.
  If None, "localhost" is used.
threaded: boolean (optional, default=False)
  Whether to launch the Server on a separate thread, allowing
  interactive use.
verbose: boolean (optional, default=True)
  Whether to print the address and port
open : boolean (optional, default=True)
  Whether to open the server in a new browser tab
location : boolean or panel.io.location.Location
  Whether to create a Location component to observe and
  set the URL location.
```

To work with an app completely interactively you can set ``threaded=True`` which will launch the server on a separate thread and let you interactively play with the app.

<img src='https://assets.holoviews.org/panel/gifs/commandline_show.gif'></img>

The ``.show`` call will return either a Bokeh server instance (if ``threaded=False``) or a ``StoppableThread`` instance (if ``threaded=True``) which both provide a ``stop`` method to stop the server instance.

The ``pn.serve`` accepts a number of arguments:

``` console
    panel: Viewable, function or {str: Viewable or function}
      A Panel object, a function returning a Panel object or a
      dictionary mapping from the URL slug to either.
    port: int (optional, default=0)
      Allows specifying a specific port
    address : str
      The address the server should listen on for HTTP requests.
    websocket_origin: str or list(str) (optional)
      A list of hosts that can connect to the websocket.

      This is typically required when embedding a server app in
      an external web site.

      If None, "localhost" is used.
    loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
      The tornado IOLoop to run the Server on
    show : boolean (optional, default=True)
      Whether to open the server in a new browser tab on start
    start : boolean(optional, default=True)
      Whether to start the Server
    title: str or {str: str} (optional, default=None)
      An HTML title for the application or a dictionary mapping
      from the URL slug to a customized title
    verbose: boolean (optional, default=True)
      Whether to print the address and port
    location : boolean or panel.io.location.Location
      Whether to create a Location component to observe and
      set the URL location.
    threaded: boolean (default=False)
      Whether to start the server on a new Thread
    admin: boolean (default=False)
      Whether to enable the admin panel
    kwargs: dict
      Additional keyword arguments to pass to Server instance
```
