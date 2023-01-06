# Accessing session state

Whenever a Panel application is being served the `panel.state` object will provide a variety of information about the current user session including the HTTP request that initiated the session, information about the browser and the current URL and more.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` HTTP Request
:link: request
:link-type: doc

How to access information about the HTTP request associated with a session.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` URL state
:link: url
:link-type: doc

How to access and manipulate the URL.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Busyiness state
:link: busy
:link-type: doc

How to access the busy state.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

request
url
busy
```
