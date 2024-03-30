# Access and Manipulate the URL

This guide addresses how to access and manipulate the URL.

This powerful technique enables you to save the state of your app via the url. You can bookmark the URL or share the URL with friends or colleagues to open the app in the exact same state later.

## Access

When starting a server session Panel will attach a `Location` component which can be accessed using `pn.state.location`. The `Location` component serves a number of functions:

- Navigation between pages via ``pathname``
- Sharing (parts of) the page state in the url as ``search`` parameters for bookmarking and sharing.
- Navigating to subsections of the page via the ``hash_`` parameter.

### Core

* **``pathname``** (string): pathname part of the url, e.g. '/how_to/layout/spacing.html'.
* **``search``** (string): search part of the url e.g. '?color=blue'.
* **``hash_``** (string): hash part of the url e.g. '#margin-parameter'.
* **``reload``** (bool): Whether or not to reload the page when the url is updated.
    - For independent apps this should be set to True.
    - For integrated or single page apps this should be set to False.

### Readonly

* **``href``** (string): The full url, e.g. 'https://panel.holoviz.org:443/how_to/layout/spacing.html?color=blue#margin-parameter'.
* **``protocol``** (string): protocol part of the url, e.g. 'http:' or 'https:'
* **``port``** (string): port number, e.g. '80'

```{note}
In a notebook environment `pn.state.location` is not initialized until the first plot has been displayed
```

## Manipulate

By default the current [query parameters](https://en.wikipedia.org/wiki/Query_string) in the URL (specified as a URL suffix such as `?color=blue`) are made available on `pn.state.location.query_params`.

## Sync and Unsync

To make working with query parameters straightforward the `Location` object provides a `sync` method which allows syncing query parameters with the parameters on a `Parameterized` object.

We will start by defining a `Parameterized` class:

```python
import panel as pn
import param


class Settings(param.Parameterized):
    integer = param.Integer(default=1, bounds=(0, 10))
    string = param.String(default='A string')

    dont_sync = param.String(default='A string')
```

Now we will use the `pn.state.location` object to sync it with the URL query string. The sync method takes the **`Parameterized` class or instance** to sync with as the first argument and a list or dictionary of the parameters as the second argument. If a dictionary is provided it should map from the Parameterized object's parameters to the query parameter name in the URL:

```python
settings = Settings()

pn.state.location.sync(settings, {'integer': 'int', 'string': 'str'})
```

Now the Parameterized object is bi-directionally linked to the URL query parameter.

Lets try to serve it as an app

```Python
pn.Param(settings).servable()
```

<video controls="" poster="../../_static/images/location_example_app.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/how_to/state/sync_url.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

Note to *unsync* the Parameterized object you can simply call `pn.state.location.unsync(query_example)`.

## Related Resources
