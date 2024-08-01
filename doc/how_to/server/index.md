# Configuring a Panel server

The Panel server can be launched either from the commandline (using `panel serve`) or programmatically (using `panel.serve()`). In this guide we will discover how to run and configure server instances using these two options.

## The server

The Bokeh server is built on Tornado, which handles all of the communication between the browser and the backend. Whenever a user accesses the app or dashboard in a browser a new session is created which executes the app code and creates a new ``Document`` containing the models served to the browser where they are rendered by BokehJS.

<div style="margin-left: auto; margin-right: auto; display: block">
<img src="https://bokeh.pydata.org/en/latest/_images/bokeh_serve.svg"></img>
</div>

If you do not want to maintain your own web server and/or set up complex reverse proxies various cloud providers make it relatively simple to quickly deploy arbitrary apps on their system. See the [deployment how-to guides](../deployment/index) for more details.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`terminal;2.5em;sd-mr-1 sd-animate-grow50` Launch from the commandline
:link: commandline
:link-type: doc

Discover how to launch and configure a Panel application from the commandline.
:::

:::{grid-item-card} {octicon}`code-square;2.5em;sd-mr-1 sd-animate-grow50` Launch programmatically
:link: programmatic
:link-type: doc

Discover how to launch and configure a Panel application programmatically.
:::

:::{grid-item-card} {octicon}`stack;2.5em;sd-mr-1 sd-animate-grow50` Serving multiple applications
:link: multiple
:link-type: doc

Discover how-to launch and configure multiple applications on the same server.
:::

:::{grid-item-card} {octicon}`server;2.5em;sd-mr-1 sd-animate-grow50` Setting up a (reverse) proxy
:link: proxy
:link-type: doc

Discover how-to configure a reverse proxy to scale your deployment.
:::

:::{grid-item-card} {octicon}`chevron-right;2.5em;sd-mr-1 sd-animate-grow50` Access via SSH
:link: ssh
:link-type: doc

Discover how to access a Panel deployment running remotely via SSH.
:::

:::{grid-item-card} {octicon}`file-media;2.5em;sd-mr-1 sd-animate-grow50` Serving static files
:link: static_files
:link-type: doc

Discover how to serve static files alongside your Panel application(s).
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

commandline
programmatic
multiple
ssh
proxy
static_files
```
