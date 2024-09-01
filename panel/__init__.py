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
from typing import TYPE_CHECKING as _TC

from param import rx

from .__version import __version__
from .config import config, panel_extension as extension
from .depends import bind, depends

if _TC:
    from . import (
        chat, custom, layout, links, pane, param, pipeline, reactive, template,
        theme, viewable, widgets,
    )
    from ._interact import interact
    from .io import serve, state
    from .io.cache import cache
    from .io.notebook import (  # noqa: F401
        _jupyter_server_extension_paths, ipywidget,
    )
    from .layout import (
        Accordion, Card, Column, Feed, FlexBox, FloatPanel, GridBox, GridSpec,
        GridStack, HSpacer, Row, Spacer, Swipe, Tabs, VSpacer, WidgetBox,
    )
    from .pane import panel
    from .param import Param, ReactiveExpr
    from .template import Template
    from .widgets import indicators, widget

_attrs = {
    "Accordion": "panel.layout:Accordion",
    "Card": "panel.layout:Card",
    "Column": "panel.layout:Column",
    "Feed": "panel.layout:Feed",
    "FlexBox": "panel.layout:FlexBox",
    "FloatPanel": "panel.layout:FloatPanel",
    "GridBox": "panel.layout:GridBox",
    "GridSpec": "panel.layout:GridSpec",
    "GridStack": "panel.layout:GridStack",
    "HSpacer": "panel.layout:HSpacer",
    "Param": "panel.param:Param",
    "ReactiveExpr": "panel.param:ReactiveExpr",
    "Row": "panel.layout:Row",
    "Spacer": "panel.layout:Spacer",
    "Swipe": "panel.layout:Swipe",
    "Tabs": "panel.layout:Tabs",
    "Template": "panel.template:Template",
    "VSpacer": "panel.layout:VSpacer",
    "WidgetBox": "panel.layout:WidgetBox",
    "_jupyter_server_extension_paths": "panel.io.notebook:_jupyter_server_extension_paths",
    "cache": "panel.io.cache:cache",
    "chat": "panel.chat",
    "custom": "panel.custom",
    "indicators": "panel.widgets:indicators",
    "interact": "panel._interact:interact",
    "ipywidget": "panel.io.notebook:ipywidget",
    "layout": "panel.layout",
    "links": "panel.links",
    "pane": "panel.pane",
    "panel": "panel.pane:panel",
    "param": None,  # available in panel/param.py
    "pipeline": "panel.pipeline",
    "reactive": "panel.reactive",
    "serve": "panel.io:serve",
    "state": "panel.io.state:state",
    "template": "panel.template",
    "theme": "panel.theme",
    "viewable": "panel.viewable",
    "widget": "panel.widgets:widget",
    "widgets": "panel.widgets",
}


def __getattr__(name: str) -> object:
    if name in _attrs:
        import importlib
        mod_name, _, attr_name = _attrs[name].partition(':')
        mod = importlib.import_module(mod_name)
        return getattr(mod, attr_name) if attr_name else mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = (
    "__version__",
    "Accordion",
    "Card",
    "chat",
    "Column",
    "custom",
    "Feed",
    "FlexBox",
    "FloatPanel",
    "GridBox",
    "GridSpec",
    "GridStack",
    "HSpacer",
    "Param",
    "ReactiveExpr",
    "Row",
    "Spacer",
    "Swipe",
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
    "reactive",
    "rx",
    "serve",
    "state",
    "theme",
    "template",
    "viewable",
    "widgets",
    "widget"
)

__dir__ = lambda: list(__all__)
