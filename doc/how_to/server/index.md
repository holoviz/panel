# Running and configuring a Panel server

The Panel server can be launched either from the commandline (using `panel serve`) or programmatically (using `panel.serve()`). In this guide we will discover how to run and configure server instances using these two options.

## The server

The Bokeh server is built on Tornado, which handles all of the communication between the browser and the backend. Whenever a user accesses the app or dashboard in a browser a new session is created which executes the app code and creates a new ``Document`` containing the models served to the browser where they are rendered by BokehJS.

<div style="margin-left: auto; margin-right: auto; display: block">
<img src="https://bokeh.pydata.org/en/latest/_images/bokeh_serve.svg"></img>
</div>

If you do not want to maintain your own web server and/or set up complex reverse proxies various cloud providers make it relatively simple to quickly deploy arbitrary apps on their system. See the [deployment how-to guides](../deployment/index) for more details.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} Launch Panel server from the commandline
:link: commandline
:link-type: doc
:::

:::{grid-item-card} Launch Panel server programmatically
:link: programmatic
:link-type: doc
:::

:::{grid-item-card} Serving multiple applications
:link: multiple
:link-type: doc
:::

:::{grid-item-card} Accessing a deployment over SSH
:link: ssh
:link-type: doc
:::

:::{grid-item-card} Setting up a (reverse) proxy
:link: proxy
:link-type: doc
:::

:::{grid-item-card} Serving static files
:link: static_files
:link-type: doc
:::

::::
