# Add custom endpoints to the Panel Server

The Panel server is built on top of Tornado, which is a general framework for building performant web applications. This means it is very straightforward to add custom endpoints to serve as API endpoints for the application or to perform anything else we might want to do.

## Declaring a new endpoint

To add a new endpoint to our server we have to implement a so called [Tornado `RequestHandler`](https://www.tornadoweb.org/en/stable/web.html). A `RequestHandler` implements has to implement one or more methods corresponding to a so called HTTP verb method. The most common of these are:

- `.get`: Handles HTTP GET requests
- `.post`: Handles HTTP POST requests
- `.head`: Handles HTTP HEAD requests

As a very simple example we might implement a GET request that sums up numbers:

```python
from tornado.web import RequestHandler, HTTPError

class SumHandler(RequestHandler):

    def get(self):
        values = [self.get_argument(arg) for arg in self.request.arguments]
        if not all(arg.isdigit() for arg in values):
            raise HTTPError(400, 'Arguments were not all numbers.')
        self.set_header('Content-Type', 'text/plain')
        self.write(str(sum([int(v) for v in values])))

ROUTES = [('/sum', SumHandler, {})]
```

This `RequestHandler` does a few things:

1. Get the values of all request arguments
2. Validate the input by check if they are all numeric digits
3. Set the `Content-Type` header to declare we are returning text
4. Sum the values and return the `write` the result as a string

Lastly, a valid Panel server plugin must also declares the `ROUTES` to add to the server. In this case we will declare that our handler should be served on the route `/sum`.

Now let's try this handler, write it to a local file called `plugin.py` and then run:

```bash
panel serve --plugins plugin
```

A Panel server will start serving our new endpoint, which means we can visit `http://localhost:5006/sum` which should display zero.

If we add some request arguments we can actually see it summing our data:

```bash
>>> curl http://localhost:5006/sum?a=1&b=3&c=39
42
```

## Using `pn.serve`

When serving from the commandline you can provide handlers explicitly using the `extra_patterns` argument, e.g. you can provide the `SumHandler` by running:

```python
import panel as pn

from plugin import SumHandler

pn.serve({}, extra_patterns=[('/sum', SumHandler)])
```
