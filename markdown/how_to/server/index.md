# Configuring a Panel server

The Panel server can be launched either from the commandline (using `panel serve`) or programmatically (using `panel.serve()`). In this guide we will discover how to run and configure server instances using these two options.

## The server

The Bokeh server is built on Tornado, which handles all of the communication between the browser and the backend. Whenever a user accesses the app or dashboard in a browser a new session is created which executes the app code and creates a new ``Document`` containing the models served to the browser where they are rendered by BokehJS.

If you do not want to maintain your own web server and/or set up complex reverse proxies various cloud providers make it relatively simple to quickly deploy arbitrary apps on their system. See the [deployment how-to guides](../deployment/index) for more details.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: commandline
:link-type: doc

Discover how to launch and configure a Panel application from the commandline.
:::

:link: programmatic
:link-type: doc

Discover how to launch and configure a Panel application programmatically.
:::

:link: multiple
:link-type: doc

Discover how-to launch and configure multiple applications on the same server.
:::

:link: wildcard_routes
:link-type: doc

Discover how to serve apps on dynamic URL patterns and access route parameters.
:::

:link: reconnect
:link-type: doc

Discover how-to configure server sessions to re-connect.
:::

:link: proxy
:link-type: doc

Discover how-to configure a reverse proxy to scale your deployment.
:::

:link: ssh
:link-type: doc

Discover how to access a Panel deployment running remotely via SSH.
:::

:link: static_files
:link-type: doc

Discover how to serve static files alongside your Panel application(s).
:::

:link: endpoints
:link-type: doc

Discover how to add custom endpoints to your Panel server.
:::

:link: endpoints
:link-type: websockets

Discover how configure the web socket settings to enable larger data transfers
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

commandline
programmatic
multiple
wildcard_routes
ssh
reconnect
proxy
static_files
endpoints
websockets
```
