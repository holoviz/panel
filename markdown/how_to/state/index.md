# Access Session State

Whenever a Panel application is being served the `panel.state` object will provide a variety of information about the current user session. This includes the HTTP request that initiated the session, information about the browser and the current URL, and more. These How-to pages provide solutions for common tasks for managing the session state.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: url
:link-type: doc

How to access and manipulate the URL.
:::

:link: request
:link-type: doc

How to access information about the HTTP request associated with a session.
:::

:link: busy
:link-type: doc

How to access the busy state.
:::
::::

## Examples

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:img-top: https://assets.holoviz.org/panel/how_to/state/sync_url.png
:link: examples/sync_url
:link-type: doc

Sync the widget state with the URL to allow deep linking your application state using `pn.state.location`.
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
