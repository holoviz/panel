# Access Session State

Whenever a Panel application is being served the `panel.state` object will provide a variety of information about the current user session. This includes the HTTP request that initiated the session, information about the browser and the current URL, and more. These How-to pages provide solutions for common tasks for managing the session state.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Access and Manipulate the URL
:link: url
:link-type: doc

How to access and manipulate the URL.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Access HTTP Request State
:link: request
:link-type: doc

How to access information about the HTTP request associated with a session.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Access Busyiness State
:link: busy
:link-type: doc

How to access the busy state.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

url
request
busy
```
