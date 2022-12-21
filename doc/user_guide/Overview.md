# Overview

In order to get the best use out of the Panel user guide, it is important to have a grasp of some core concepts, ideas, and terminology.

## Components

Panel provides three main types of component: ``Pane``, ``Widget``, and ``Panel``. These components are introduced and explained in the [Components user guide](./Components.rst), but briefly:

* **``Pane``**: A ``Pane`` wraps a user supplied object of almost any type and turns it into a renderable view. When the wrapped ``object`` or any parameter changes, a pane will update the view accordingly.

* **``Widget``**: A ``Widget`` is a control component that allows users to provide input to your app or dashboard, typically by clicking or editing objects in a browser, but also controllable from within Python.

* **``Panel``**: A ``Panel`` is a hierarchical container to lay out multiple components (panes, widgets, or other ``Panel``s) into an arrangement that forms an app or dashboard.

---

## APIs

Panel is a very flexible system that supports many different usage patterns, via multiple application programming interfaces (APIs).  Each API has its own advantages and disadvantages, and is suitable for different tasks and ways of working. The [API user guide](APIs.rst) goes through each of the APIs in detail, comparing their pros and cons and providing recommendations on when to use each.

### [Reactive functions](./APIs.rst#reactive-functions)

Defining a reactive function using the ``pn.bind`` function or ``pn.depends`` decorator provides an explicit way to link specific inputs (such as the value of a widget) to some computation in a function, reactively updating the output of the function whenever the parameter changes. This approach is a highly convenient, intuitive, and flexible way of building interactive UIs.

### [``interact``](./Interact.rst)

The ``interact`` API will be familiar to ipywidgets users; it provides a very simple API to define an interactive view of the results of a Python function. This approach works by declaring functions whose arguments will be inspected to infer a set of widgets. Changing any of the resulting widgets causes the function to be re-run, updating the displayed output. This approach makes it extremely easy to get started and also easy to rearrange and reconfigure the resulting plots and widgets, but it may not be suited to more complex scenarios. See the [Interact user guide](./Interact.rst) for more detail.

### [``Param``](./Param.rst)

``Panel`` itself is built on the [param](https://param.pyviz.org) library, which allows capturing parameters and their allowable values entirely independently of any GUI code. By using Param to declare the parameters along with methods that depend on those parameters, even very complex GUIs can be encapsulated in a tidy, well-organized, maintainable, and declarative way. Panel will automatically convert parameter definition to corresponding widgets, allowing the same codebase to support command-line, batch, server, and GUI usage. This API requires the use of the param library to express the inputs and encapsulate the computations to be performed, but once implemented this approach leads to flexible, robust, and well encapsulated code. See the Panel [Param user guide](./Param.rst) for more detail.

### [Callback API](./Widgets.rst)

At the lowest level, you can build interactive applications using ``Pane``, ``Widget``, and ``Panel`` components and connect them using explicit callbacks. Registering callbacks on components to modify other components provides full flexibility in building interactive features, but once you have defined numerous callbacks it can be very difficult to track how they all interact. This approach affords the most amount of flexibility but can easily grow in complexity, and is not recommended as a starting point for most users. That said, it is the interface that all the other APIs are built on, so it is powerful and is a good approach for building entirely new ways of working with Panel, or when you need some specific behavior not covered by the other APIs. See the [Widgets user guide](./Widgets.rst) and [Links user guide](./Links.rst) for more detail.

---

## Display and rendering

Throughout this user guide we will cover a number of ways to display Panel objects, including display in a Jupyter notebook, in a standalone server, by saving and embedding, and more. For a detailed description see the [Display and Export user guide](./Display_and_Export.rst).

### Notebook

All of Panel's documentation is built from Jupyter notebooks that you can explore at your own pace. Panel does not require Jupyter in any way, but it has extensive Jupyter support:

#### ``pn.extension()``

> The Panel extension loads BokehJS, any custom models required, and optionally additional custom JS and CSS in Jupyter notebook environments. It also allows passing any [`pn.config`](#pn.config) variables

#### ``pn.ipywidget()``

> Given a Panel model `pn.ipywidget` will return an ipywidget model that renders the object in the notebook. This can be useful for including an panel widget in an ipywidget layout and deploying Panel objects using [Voilà](https://github.com/voila-dashboards/voila/).

#### ``pn.io.push_notebook``

> When working with Bokeh models directly in a Jupyter Notebook any changes to the model are not automatically sent to the frontend. Instead we have to explicitly call `pn.io.push_notebook` on the Panel component(s) wrapping the Bokeh component being updated.

#### Rich display

Jupyter notebooks allow the final value of a notebook cell to display itself, using a mechanism called [rich display](https://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display). As long as `pn.extension()` has been called in a notebook, all Panel components (widgets, panes, and panels) will display themselves when placed on the last line of a notebook cell.

#### ``.app()``

> The ``.app()`` method present on all viewable Panel objects allows displaying a Panel server process inline in a notebook, which can be useful for debugging a standalone server interactively.

### Python REPL and embedding a server

When working in a Python REPL that does not support rich-media output (e.g. in a text-based terminal) or when embedding a Panel application in another tool, a panel can be launched in a browser tab using:

#### ``.show()``

> The ``.show()`` method is present on all viewable Panel objects and starts a server instance then opens a browser tab to point to it. To support working remotely, a specific port on which to launch the app can be supplied.

#### ``pn.serve()``

>Similar to .show() on a Panel object but allows serving one or more Panel apps on a single server. Supplying a dictionary mapping from the URL slugs to the individual Panel objects being served allows launching multiple apps at once. Note that to ensure that each user gets separate session state you should wrap your app in a function which returns the Panel component to render. This ensures that whenever a new user visits the application a new instance of the application can be created.

### Command line

Panel mirrors Bokeh's command-line interface for launching and exporting apps and dashboards:

#### ``panel serve app.py``

> The ``panel serve`` command allows allows interactively displaying and deploying Panel web-server apps from the commandline.

#### ``panel serve app.ipynb``

> ``panel serve`` also supports using Jupyter notebook files, where it will serve any Panel objects that were marked `.servable()` in a notebook cell. This feature allows you to maintain a notebook for exploring and analysis that provides certain elements meant for broader consumption as a standalone app.

### Export

When not working interactively, a Panel object can be exported to a static file.

#### ``.save()`` to PNG

> The ``.save`` method present on all viewable Panel objects allows saving the visual representation of a Panel object to a PNG file.

#### ``.save()`` to HTML

> ``.save`` to HTML allows sharing the full Panel object, including any static links ("jslink"s) between widgets and other components, but other features that depend on having a live running Python process will not work (as for many of the Panel webpages).

### Embedding

Panel objects can be serialized into a static JSON format that captures the widget state space and the corresponding plots or other viewable items for each combination of widget values, allowing fully usable Panel objects to be embedded into external HTML files or emails.  For simple cases, this approach allows distributing or publishing Panel apps that no longer require a Python server in any way. Embedding can be enabled when using ``.save()``, using the ``.embed()`` method or globally using [Python and Environment variables](#Python and Environment variables) on ``pn.config``.

#### ``.embed()``

> The ``.embed()`` method embeds the contents of the object it is being called on in the notebook.

___

## Linking and callbacks

One of the most important aspects of a general app and dashboarding framework is the ability to link different components in flexible ways, scheduling callbacks in response to internal and external events. Panel provides convenient lower and higher-level APIs to achieve both.  For more details, see the [Links](./Links.rst) user guide.

### Methods

#### ``.param.watch``

> The ``.param.watch`` method allows listening to parameter changes on an object using Python callbacks. It is the lowest level API and provides the most amount of control, but higher-level APIs are more appropriate for most users and most use cases.

#### ``.link()``

> The Python-based ``.link()`` method present on all viewable Panel objects is a convenient API to link the parameters of two objects together, uni- or bi-directionally.

#### ``.jscallback``

> The Javascript-based ``.jscallback()`` method allows defining arbitrary Javascript code to be executed when some property changes or event is triggered.

#### ``.jslink()``

> The JavaScript-based ``.jslink()`` method directly links properties of the underlying Bokeh models, making it possible to define interactivity that works even without a running Python server.

___

## State and configuration

Panel provides top-level objects to hold current state and control high-level configuration variables.

### `pn.config`

The `pn.config` object allows setting various configuration variables, the config variables can also be set as environment variables or passed through the [`pn.extension`](#pn-extension):

#### Python only

> - `css_files`: External CSS files to load.
> - `js_files`: External JS files to load. Dictionary should map from exported name to the URL of the JS file.
> - `loading_spinner`: The style of the global loading indicator, e.g. 'arcs', 'bars', 'dots', 'petals'.
> - `loading_color`: The color of the global loading indicator as a hex color, e.g. #6a6a6a
> - `defer_load`: Whether reactive function evaluation is deferred until the page is rendered.
> - `exception_handler`: A custom exception handler can be defined which should accept any exceptions raised while processing events originating from the frontend and onload callbacks.
> - `nthreads`: If set will start a `ThreadPoolExecutor` to dispatch events to for concurrent execution on separate cores. By default no thread pool is launched, while setting nthreads=0 launches `min(32, os.cpu_count() + 4)` threads.
> - `raw_css`: List of raw CSS strings to add to load.
> - `reuse_sessions`: Whether to reuse a session for the initial request to speed up the initial page render. Note that if the initial page differs between sessions, e.g. because it uses query parameters to modify the rendered content, then this option will result in the wrong content being rendered. See the [Performance and Debugging guide](Performance_and_Debugging.rst#Reuse-sessions) for more information.
> - `safe_embed`: Whether to record all set events when embedding rather than just those that are changed
> - `session_history`: If set to a non-zero value this determines the maximum length of the pn.state.session_info dictionary, which tracks information about user sessions. A value of -1 indicates an unlimited history.
> - `sizing_mode`:  Specify the default sizing mode behavior of panels.
> - `template`: The template to render the served application into, e.g. `'bootstrap'` or `'material'`.
> - `theme`: The theme to apply to the selected template (no effect unless `template` is set)
> - `throttled`: Whether sliders and inputs should be throttled until release of mouse.

#### Python and Environment variables

> - `comms` (`PANEL_COMMS`): Whether to render output in Jupyter with the default Jupyter extension or use the `jupyter_bokeh` ipywidget model.
> - `console_output` (`PANEL_CONSOLE_OUTPUT`): How to log errors and stdout output triggered by callbacks from Javascript in the notebook. Options include `'accumulate'`, `'replace'` and `'disable'`.
> - `embed` (`PANEL_EMBED`): Whether plot data will be [embedded](./Deploy_and_Export.rst#Embedding).
> - `embed_json` (`PANEL_EMBED_JSON`): Whether to save embedded state to json files.
> - `embed_json_prefix` (`PANEL_EMBED_JSON_PREFIX`): Prefix for randomly generated json directories.
> - `embed_load_path` (`PANEL_EMBED_LOAD_PATH`): Where to load json files for embedded state.
> - `embed_save_path` (`PANEL_EMBED_SAVE_PATH`): Where to save json files for embedded state.
> - `inline` (`PANEL_INLINE`): Whether to inline JS and CSS resources. If disabled, resources are loaded from CDN if one is available.
> - `npm_cdn` (`PANEL_NPM_CDN`): The CDN to load NPM packages from if resources are served from CDN. Allows switching between 'https://unpkg.com' (default) and 'https://cdn.jsdelivr.net/npm' for most resources.

#### `pn.state`

The `pn.state` object makes various global state available and provides methods to manage that state:

- - `access_token`: The access token issued by the OAuth provider to authorize requests to its APIs.
> - `busy`: A boolean value to indicate whether a callback is being actively processed.
> - `cache`: A global cache which can be used to share data between different processes.
> - `cookies`: HTTP request cookies for the current session.
> - `curdoc`: When running a server session this property holds the current bokeh Document.
> - `location`: In a server context this provides read and write access to the URL:
>   * `hash`: hash in window.location e.g. '#interact'
>   * `pathname`: pathname in window.location e.g. '/user_guide/Interact.html'
>   * `search`: search in window.location e.g. '?color=blue'
>   * `reload`: Reloads the page when the location is updated.
>   * `href` (readonly): The full url, e.g. 'https://localhost:80?color=blue#interact'
>   * `hostname` (readonly): hostname in window.location e.g. 'panel.holoviz.org'
>   * `protocol` (readonly): protocol in window.location e.g. 'http:' or 'https:'
>   * `port` (readonly): port in window.location e.g. '80'
> - `headers`: HTTP request headers for the current session.
> - `refresh_token`: The refresh token issued by the OAuth provider to authorize requests to its APIs (if available these are usually longer lived than the `access_token`).
> - `session_args`: When running a server session this return the request arguments.
> - `session_info`: A dictionary tracking information about server sessions:
>   * `total` (int): The total number of sessions that have been opened
>   * `live` (int): The current number of live sessions
>   * `sessions` (dict(str, dict)): A dictionary of session information:
>       * `started`: Timestamp when the session was started
>       * `rendered`: Timestamp when the session was rendered
>       * `ended`: Timestamp when the session was ended
>       * `user_agent`: User-Agent header of client that opened the session
> - `webdriver`: Caches the current webdriver to speed up export of bokeh models to PNGs.
>
> #### Methods
>
> - `add_periodic_callback`: Schedules a periodic callback to be run at an interval set by the period
> - `as_cached`: Allows caching data across sessions by memoizing on the provided key and keyword arguments to the provided function.
> - `cancel_scheduled`: Cancel a scheduled task by name.
> - `execute`: Executes both synchronous and asynchronous callbacks appropriately depending on the context the application is running in.
> - `kill_all_servers`: Stops all running server sessions.
> - `onload`: Allows defining a callback which is run when a server is fully loaded
> - `schedule`: Schedule a callback periodically at a specific time (click [here](./Deploy_and_Export.rst#pn.state.schedule) for more details)
> - `sync_busy`: Sync an indicator with a boolean value parameter to the busy property on state
