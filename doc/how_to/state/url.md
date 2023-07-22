# Access and Manipulate the URL

This guide addresses how to access and manipulate the URL.

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

## Manipulate

By default the current [query parameters](https://en.wikipedia.org/wiki/Query_string) in the URL (specified as a URL suffix such as `?color=blue`) are made available on `pn.state.location.query_params`. To make working with query parameters straightforward the `Location` object also provides a `sync` method which allows syncing query parameters with the parameters on a `Parameterized` object.

We will start by defining a `Parameterized` class:

```python
import param
import panel as pn

class QueryExample(param.Parameterized):

    integer = param.Integer(default=None, bounds=(0, 10))

    string = param.String(default='A string')
```

Now we will use the `pn.state.location` object to sync it with the URL query string (note that in a notebook environment `pn.state.location` is not initialized until the first plot has been displayed). The sync method takes the Parameterized object or instance to sync with as the first argument and a list or dictionary of the parameters as the second argument. If a dictionary is provided it should map from the Parameterized object's parameters to the query parameter name in the URL:

```python
pn.state.location.sync(QueryExample, {'integer': 'int', 'string': 'str'})
```

Now the Parameterized object is bi-directionally linked to the URL query parameter, if we set a query parameter in Python it will update the URL bar and when we specify a URL with a query parameter that will be set on the Parameterized, e.g. let us set the 'integer' parameter and watch the URL in your browser update:

```python
QueryExample.integer = 5
```

Note to unsync the Parameterized object you can simply call `pn.state.location.unsync(QueryExample)`.

## Related Resources
