"""
Panel is a high level app and dashboarding framework
====================================================

Panel is an open-source Python library that lets you create custom
interactive web apps and dashboards by connecting user-defined widgets
to plots, images, tables, or text.

Panel works with the tools you know and ❤️.

Check out https://panel.holoviz.org/

.. figure:: https://user-images.githubusercontent.com/42288570/152672367-6c239073-0ea0-4a2b-a4c0-817e8090e877.gif
   :alt: Panel Dashboard

   Panel Dashboard

How to develop a Panel app in 3 simple steps
--------------------------------------------

- Write the app

>>> import panel as pn
>>> pn.extension(sizing_mode="stretch_width", template="fast")
>>> pn.state.template.param.update(title="My Data App")
>>> pn.panel(some_python_object).servable()

- Run your app

$ panel serve my_script.py --autoreload --show

or

$ panel serve my_notebook.ipynb --autoreload --show

The app will be available in your browser!

- Change your code and save it

The app will reload with your changes!

You can also add automatic reload to jupyterlab. Check out
https://blog.holoviz.org/panel_0.12.0.html#JupyterLab-previews

To learn more about Panel check out
https://panel.holoviz.org/getting_started/index.html
"""
from . import layout  # noqa
from . import links  # noqa
from . import pane  # noqa
from . import param  # noqa
from . import pipeline  # noqa
from . import reactive  # noqa
from . import viewable  # noqa
from . import widgets  # noqa
from .config import __version__, config, panel_extension as extension  # noqa
from .depends import bind, depends  # noqa
from .interact import interact  # noqa
from .io import (  # noqa
    _jupyter_server_extension_paths, cache, ipywidget, serve, state,
)
from .layout import (  # noqa
    Accordion, Card, Column, FlexBox, FloatPanel, GridBox, GridSpec, GridStack,
    HSpacer, Row, Spacer, Swipe, Tabs, VSpacer, WidgetBox,
)
from .pane import panel  # noqa
from .param import Param  # noqa
from .react import react  # noqa
from .template import Template  # noqa
from .widgets import indicators, widget  # noqa

__all__ = (
    "__version__",
    "Accordion",
    "Card",
    "Column",
    "FlexBox",
    "FloatPanel",
    "GridBox",
    "GridSpec",
    "GridStack",
    "HSpacer",
    "Param",
    "Row",
    "Spacer",
    "Tabs",
    "Template",
    "VSpacer",
    "WidgetBox",
    "bind",
    "cache",
    "config",
    "depends",
    "extension",
    "indicators",
    "interact",
    "ipywidget",
    "layout",
    "links",
    "pane",
    "panel",
    "param",
    "pipeline",
    "react",
    "reactive",
    "serve",
    "state",
    "viewable",
    "widgets",
    "widget"
)
