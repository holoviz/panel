"""[Panel site](https://panel.holoviz.org/), [Getting started guide](https://panel.holoviz.org/getting_started/index.html), [Community forum](https://discourse.holoviz.org/), [Github](https://github.com/holoviz/panel), [Twitter](https://twitter.com/Panel_org), and [LinkedIn](https://www.linkedin.com/company/79754450)

# Panel is a high level app and dashboarding framework

Panel is an open-source Python library that lets you create custom interactive web apps and 
dashboards by connecting user-defined widgets to plots, images, tables, or text. 

Panel works with the tools you know and ❤️.

![Panel Dashboard](https://assets.holoviews.org/panel/thumbnails/docstrings/panel.gif)
"""
from . import layout # noqa
from . import links # noqa
from . import pane # noqa
from . import param # noqa
from . import pipeline # noqa
from . import reactive # noqa
from . import viewable # noqa
from . import widgets # noqa

from .config import config, panel_extension as extension, __version__ # noqa
from .depends import bind, depends # noqa
from .interact import interact # noqa
from .io import _jupyter_server_extension_paths, ipywidget, serve, state # noqa
from .layout import ( # noqa
    Accordion, Card, Column, GridSpec, GridBox, FlexBox, Tabs, Row,
    Spacer, WidgetBox
)
from .pane import panel, Pane # noqa
from .param import Param # noqa
from .template import Template # noqa
from .widgets import indicators # noqa
