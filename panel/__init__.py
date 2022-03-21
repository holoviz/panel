"""Panel is a high level app and dashboarding framework
====================================================

Panel is an open-source Python library that lets you create custom
interactive web apps and dashboards by connecting user-defined widgets
to plots, images, tables, or text.

Panel works with the tools you know and ❤️.

.. figure:: https://user-images.githubusercontent.com/42288570/152672367-6c239073-0ea0-4a2b-a4c0-817e8090e877.gif
   :alt: Panel Dashboard

   Panel Dashboard
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
