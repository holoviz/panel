# Extensions

## Plugin support

Panel supports a number of entrypoint groups which can be used by external packages to extend its functionality.

 - panel.auth
 - panel.io.rest
 - panel.extension

### Authentication plugins

The `panel.auth` group should be used to register new authentication providers. The entrypoint should resolve to a subclass of `tornado.web.RequestHandler` that can handle authentication requests. The handler can be enabled for a given app by setting the `auth` config to to the name of the entrypoint.

### Rest plugins

The `panel.io.rest` entrypoint group can be used to register rest providers that will be served along the panel app. The entrypoint should resolve to a callable with the following signature:

```python
from typing import List, Tuple, Type
from tornado.web import RequestHandler
RequestHandlerClass = Type[RequestHandler]

def provider(files: list, endpoint: str) -> List[Tuple[str,RequestHandlerClass,dict]]:
    pass

```

It should accept a list of files to serve and the endpoint it will serve on, it should return a list of tuples where the list of tuples returned include a pattern to match, a request handler class and a dictionary of keyword arguments to pass to the handler class on initialization.

### Extension plugins

The `panel.extension` entrypoint group can be used to apply runtime extensions. These entrypoints are resolved when `panel.extension()` is called. If the entrypoint resolves to a module, it will be imported and if it resolves to a callable it will be called with no arguments. If you need to access the current configuration within the extension code, the Panel global config object will already be initialized at the time these entrypoints are resolved and available via `panel.config`.
