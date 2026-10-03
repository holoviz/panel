# Serving multiple applications

If you want to serve more than one app on a single server you can use the ``pn.serve`` function. By supplying a dictionary where the keys represent the URL slugs and the values must be either Panel objects or functions returning Panel objects you can easily launch a server with a number of apps, e.g.:

```python
import panel as pn
pn.serve({
    'markdown': '# This is a Panel app',
    'json': pn.ui.JSON({'abc': 123})
})
```

Note that when you serve an object directly all sessions will share the same state, i.e. the parameters of all components will be synced across sessions such that the change in a widget by one user will affect all other users. Therefore you will usually want to wrap your app in a function, ensuring that each user gets a new instance of the application:

```python

def markdown_app():
    return '# This is a Panel app'

def json_app():
    return pn.ui.JSON({'abc': 123})

pn.serve({
    'markdown': markdown_app,
    'json': json_app
})
```

You can customize the HTML title of each application by supplying a dictionary where the keys represent the URL slugs and the values represent the titles, e.g.:

```python
pn.serve({
    'markdown': '# This is a Panel app',
    'json': pn.ui.JSON({'abc': 123})
}, title={'markdown': 'A Markdown App', 'json': 'A JSON App'}
)
```

## Scoping frontend extensions per app

When serving multiple apps on the same server, each app may require different JavaScript and CSS extensions (e.g. `'codeeditor'`, `'tabulator'`, `'katex'`). By default, Panel tracks which extensions have been loaded **globally** and includes them in every session, regardless of which app the user is visiting.

This means that if one app loads a heavy extension (such as the ACE editor), subsequent visits to a *different*, lighter app will **also** receive those assets — even if they are not needed.

To prevent this, call `pn.extension()` **inside the app function** rather than at module level. When `pn.extension` is called inside a session function, Panel scopes the extension list to that session only:

```python
import panel as pn

def editor_app():
    pn.extension('codeeditor')  # scoped to this session only
    return pn.widgets.CodeEditor(filename="demo.md", value="# Hello")

def simple_app():
    pn.extension()  # scoped to this session — no extra extensions loaded
    return pn.widgets.StaticText(value="Hello world")

pn.serve({
    'editor': editor_app,
    'simple': simple_app,
}, port=5006)
```

With this pattern:

- Visiting `/editor` loads the ACE editor assets — as expected.
- Visiting `/simple` loads **only** the core Panel assets — no ACE editor JS is sent to the browser.

:::{note}
If `pn.extension()` is **not** called inside a session function, that session inherits all extensions that have been registered globally (including those loaded by other app functions that ran earlier). Always call `pn.extension()` inside each app function when you want precise per-app asset control.
:::
