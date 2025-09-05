# Access HTTP Request State

This guide addresses how to access information about the HTTP request associated with a session.

```{admonition} Prerequisites
1. See the [How to > Access and Manipulate the URL](url) guide to learn how to work with the URL.
```
---

The `panel.state` object holds a wide range of information about the HTTP request that is associated with a running session. Note that if you are running Panel inside a notebook session these attributes will simply return `None`.

## Request arguments

The request arguments are made available to be accessed on ``pn.state.session_args``. For example if your application is hosted at ``localhost:8001/app``, appending ``?phase=0.5`` to the URL will allow you to access the phase variable using the following code:

```python
try:
    phase = int(pn.state.session_args.get('phase')[0])
except Exception:
    phase = 1
```

This mechanism may be used to modify the behavior of an app depending on parameters provided in the URL.

## Cookies

The `panel.state.cookies` will allow accessing the cookies stored in the browser and on the bokeh server.

## Headers

The `panel.state.headers` will allow accessing the HTTP headers stored in the browser and on the bokeh server.

## Related Resources
