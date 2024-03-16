# Configure Logging

## Utilize Bokeh and Panel Environment Variables

Bokeh and Panel offer several environment variables for logging control:

- `BOKEH_LOG_LEVEL`: Sets the log level of the `bokeh` JavaScript logger, with the default being 'info'.
- `BOKEH_PY_LOG_LEVEL`: Sets the log level of the `bokeh` Python logger, by default it's "none".
- `PANEL_LOG_LEVEL`: Sets the log level of the `panel` Python logger, with the default being "WARNING".

For more detailed information, refer to [`bokeh.util.logconfig`](https://github.com/bokeh/bokeh/blob/main/src/bokeh/util/logconfig.py) or [`panel.io.logging`](https://github.com/holoviz/panel/blob/main/panel/io/logging.py).

## Reconfigure the Root Logger

Bokeh executes `logging.basicConfig` to configure the root logger. Fortunately, since Python 3.9, we can redo this using `force=True`.

```python
import logging
import panel as pn

FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

@pn.cache
def reconfig_basic_config(format_=FORMAT, level=logging.INFO):
    """(Re-)configure logging"""
    logging.basicConfig(format=format_, level=level, force=True)
    logging.info("Logging.basicConfig completed successfully")

reconfig_basic_config()
logger = logging.getLogger(name="app")

logger.info("Hello World")
pn.panel("Hello World").servable()
```

Upon use, it should resemble:

```bash
$ panel serve app.py
2024-03-16 08:20:35,993 Starting Bokeh server version 3.4.0 (running on Tornado 6.4)
2024-03-16 08:20:35,995 User authentication hooks NOT provided (default user enabled)
2024-03-16 08:20:36,002 Bokeh app running at: http://localhost:5006/app
2024-03-16 08:20:36,002 Starting Bokeh server with process id: 25540
2024-03-16 08:20:36,930 | INFO | root | Logging.basicConfig completed successfully
2024-03-16 08:20:36,930 | INFO | app | Hello World
2024-03-16 08:20:37,080 | INFO | tornado.access | 200 GET /app (::1) 168.75ms
2024-03-16 08:20:37,184 | INFO | tornado.access | 101 GET /app/ws (::1) 0.00ms
2024-03-16 08:20:37,185 | INFO | bokeh.server.views.ws | WebSocket connection opened
2024-03-16 08:20:37,186 | INFO | bokeh.server.views.ws | ServerConnection created
2024-03-16 08:20:37,189 | INFO | tornado.access | 200 GET /static/extensions/panel/images/favicon.ico (::1) 2.00ms
```

:::{note}

Please be aware that loggers like `tornado`, which were not displayed previously, will now be shown because we've modified the root log level to INFO.

:::

:::{note}

We utilize caching (`pn.cache`) because `reconfig_basic_config` runs each time a new Panel session starts. If you move the logging reconfiguration to a separate module, caching won't be necessary.

:::

## Configure a Single Logger

If you prefer not to reconfigure all logging, you can configure a single logger as demonstrated below.

```python
import logging
import sys
import panel as pn

FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

@pn.cache
def get_logger(name, format_=FORMAT, level=logging.INFO):
    logger = logging.getLogger(name)

    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setStream(sys.stdout)
    formatter = logging.Formatter(format_)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    logger.setLevel(level)
    logger.info("Logger successfully configured")
    return logger

logger = get_logger(name="app")

logger.info("Hello World")
pn.panel("Hello World").servable()
```

It should yield:

```bash
$ panel serve app.py
2024-03-16 08:24:02,469 Starting Bokeh server version 3.4.0 (running on Tornado 6.4)
2024-03-16 08:24:02,469 User authentication hooks NOT provided (default user enabled)
2024-03-16 08:24:02,485 Bokeh app running at: http://localhost:5006/app
2024-03-16 08:24:02,485 Starting Bokeh server with process id: 33536
2024-03-16 08:24:05,272 | INFO | app | Logger successfully configured
2024-03-16 08:24:05,272 | INFO | app | Hello World
2024-03-16 08:24:05,565 WebSocket connection opened
2024-03-16 08:24:05,566 ServerConnection created
```

## Configure the Panel and Bokeh Loggers

If you want to configure the Panel and Bokeh loggers as well, it's straightforward.

```python
import logging
import sys
import panel as pn

FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

@pn.cache
def get_logger(name, format_=FORMAT, level=logging.INFO):
    logger = logging.getLogger(name)

    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setStream(sys.stdout)
    formatter = logging.Formatter(format_)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    logger.setLevel(level)
    logger.info("Logger successfully configured")
    return logger

get_logger(name="bokeh")
get_logger(name="panel")
logger = get_logger(name="app")

logger.info("Hello World")
pn.panel("Hello World").servable()
```

It will appear as follows:

```bash
$ panel serve app.py
2024-03-16 08:26:59,183 Starting Bokeh server version 3.4.0 (running on Tornado 6.4)
2024-03-16 08:26:59,183 User authentication hooks NOT provided (default user enabled)
2024-03-16 08:26:59,199 Bokeh app running at: http://localhost:5006/app
2024-03-16 08:26:59,199 Starting Bokeh server with process id: 11200
2024-03-16 08:27:00,434 | INFO | app | logger successfully configured
2024-03-16 08:27:00,435 | INFO | bokeh | logger successfully configured
2024-03-16 08:27:00,437 | INFO | panel | logger successfully configured
2024-03-16 08:27:00,437 | INFO | app | Hello World
2024-03-16 08:27:00,585 | INFO | panel.io.server | Session 2863386286800 created
```
