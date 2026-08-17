# Serving applications on wildcard routes

When serving multiple apps with `pn.serve`, the route keys are usually static paths (for example `"/app"`). You can also use wildcard-style route patterns to match dynamic URL segments.

## Serve an app on a wildcard route

Use a route pattern as the dictionary key:

```python
import panel as pn

pn.extension()

def app():
    return pn.pane.JSON(
        {
            "route_params": pn.state.route_params,
            "app_url": pn.state.app_url,
        },
        depth=2,
    )

pn.serve(
    {
        "/user/{name}": app,
    },
    show=False,
)
```

Now:

- `/user/alice` and `/user/bob` will both resolve to the same app
- `pn.state.route_params` will contain the captured values for the current request

For the two URLs above, `pn.state.route_params` will be:

- `{"name": "alice"}`
- `{"name": "bob"}`

Path converters are supported as well:

```python
pn.serve(
    {
        "/files/{filepath:path}": app,
    },
    show=False,
)
```

Then `pn.state.route_params` contains:

- `{"filepath": "a/b/c.txt"}`

Template converters currently supported are:

- `str` (default) for single path segments
- `path` for slash-containing paths
- `int` for signed integers (for example `-2`, `0`, `+3`)
- `float` for signed decimal/scientific formats (for example `-1.5`, `.5`, `1.`, `6.02e23`)
- `uuid` for canonical UUID strings

## Regex syntax (Tornado-style)

On Tornado you can also use regular expression routes directly:

```python
pn.serve(
    {
        "/user/([^/]+)": app,
    },
    show=False,
)
```

For this route, `pn.state.route_params` contains positional captures:

- `{"0": "alice"}`

Unlike path-template routes (which use parameter names), raw regex captures are exposed as positional string keys (`"0"`, `"1"`, ...).

### Named parameters with regex syntax

You can also use named groups:

```python
pn.serve(
    {
        "/org/(?P<org>[^/]+)/user/(?P<user>[^/]+)": app,
    },
    show=False,
)
```

Then `pn.state.route_params` contains the named captures:

- `{"org": "acme", "user": "alice"}`

## Backend compatibility

- **Tornado (`panel serve`, `panel.io.server.serve`)**
  - Supports regex-style routes, e.g. `"/user/([^/]+)"` and named groups.
  - Supports path-template syntax, which is normalized to Tornado-compatible patterns (for example `"/user/{name}"`).
- **FastAPI (`panel.io.fastapi.serve`)**
  - Supports path-template syntax, e.g. `"/user/{name}"`, `"/files/{filepath:path}"`.

## Best practices

- Prefer path-template syntax (`{name}`, `{name:path}`) when writing apps intended to run on both Tornado and FastAPI.
- If you use regex syntax, prefer non-greedy segment patterns such as `([^/]+)` for path segments.
- Prefer explicit groups over very broad patterns like `(.*)` unless you specifically need to capture slashes.
- Use `pn.state.app_url` when you need the concrete matched application URL for the current session.
- Use `pn.state.route_params` to access the route parameters.
