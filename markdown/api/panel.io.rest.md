# panel.io.rest module

class panel.io.rest.BaseHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: `RequestHandler`

Methods

|  |  |
|----|----|
| [write_error](#panel.io.rest.BaseHandler.write_error)(status_code, **kwargs) | Override to implement custom error pages. |

write_error(status_code, **kwargs)
Override to implement custom error pages.

`write_error` may call write, render,
set_header, etc to produce output as usual.

If this error was caused by an uncaught exception (including HTTPError),
an `exc_info` triple will be available as
`kwargs["exc_info"]`. Note that this exception
may not be the “current” exception for purposes of methods like
`sys.exc_info()` or
`traceback.format_exc`.

exception panel.io.rest.HTTPError(status_code: int = 500, log_message: str \| None = None, \*args: Any, **kwargs: Any)
Bases: `HTTPError`

Custom HTTPError type

class panel.io.rest.ParamHandler(app, request, **kwargs)
Bases: [BaseHandler](#panel.io.rest.BaseHandler)

Methods

|                 |     |
|-----------------|-----|
| **deserialize** |     |
| **get**         |     |
| **serialize**   |     |

panel.io.rest.param_rest_provider(files, endpoint)
Returns a Param based REST API given the scripts or notebooks containing
the tranquilized functions.

Parameters:
**files: list(str)**
A list of paths being served

**endpoint: str**
The endpoint to serve the REST API on

Returns:
A Tornado routing pattern containing the route and handler

panel.io.rest.tranquilizer_rest_provider(files, endpoint)
Returns a Tranquilizer based REST API. Builds the API by evaluating the
scripts and notebooks being served and finding all tranquilized
functions inside them.

Parameters:
**files: list(str)**
A list of paths being served

**endpoint: str**
The endpoint to serve the REST API on

Returns:
A Tornado routing pattern containing the route and handler

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
