"""
Layout
======

Layouts can layout your python objects and panel components.

Most layouts behave as the Python containers you already know. For example
`Column` and `Row` behaves as lists. I.e. they have a list-like API with
methods to `append`, `extend`, `clear`, `insert`, `pop`, `remove` and
`__setitem__`, which make it possible to interactively update and modify them.

Check out the Panel gallery of layouts
https://panel.holoviz.org/reference/index.html#layouts for inspiration.

How to use layouts in 2 simple steps
------------------------------------

1. Define your Python objects

>>> some_python_object = ...
>>> some_widget = pn.widgets...
>>> some_pane = pn.pane...

2. Define your layouts

>>> pn.Column(some_python_object, some_widget, some_pane)

For more detail see the Getting Started Guide
https://panel.holoviz.org/getting_started/index.html
"""
from typing import TYPE_CHECKING as _TC

from .gridstack import GridStack  # ReactiveHTML

if _TC:
    from .accordion import Accordion
    from .base import (
        Column, ListLike, ListPanel, Panel, Row, WidgetBox,
    )
    from .card import Card
    from .feed import Feed
    from .flex import FlexBox
    from .float import FloatPanel
    from .grid import GridBox, GridSpec
    from .spacer import (
        Divider, HSpacer, Spacer, VSpacer,
    )
    from .swipe import Swipe
    from .tabs import Tabs

_attrs = {
    "Accordion": "panel.layout.accordion:Accordion",
    "Card": "panel.layout.card:Card",
    "Column": "panel.layout.base:Column",
    "Divider": "panel.layout.spacer:Divider",
    "Feed": "panel.layout.feed:Feed",
    "FloatPanel": "panel.layout.float:FloatPanel",
    "FlexBox": "panel.layout.flex:FlexBox",
    "GridBox": "panel.layout.grid:GridBox",
    "GridSpec": "panel.layout.grid:GridSpec",
    # "GridStack": "panel.layout.gridstack:GridStack",
    "HSpacer": "panel.layout.spacer:HSpacer",
    "ListLike": "panel.layout.base:ListLike",
    "ListPanel": "panel.layout.base:ListPanel",
    "Panel": "panel.layout.base:Panel",
    "Row": "panel.layout.base:Row",
    "Spacer": "panel.layout.spacer:Spacer",
    "Swipe": "panel.layout.swipe:Swipe",
    "Tabs": "panel.layout.tabs:Tabs",
    "VSpacer": "panel.layout.spacer:VSpacer",
    "WidgetBox": "panel.layout.base:WidgetBox",
}

def __getattr__(name: str):
    if name == "no_lazy":
        for attr in _attrs:
            mod = __getattr__(attr)
            if hasattr(mod, "_attrs"):
                getattr(mod._attrs, "no_lazy", None)
        return name
    if name in _attrs:
        import importlib
        mod_name, _, attr_name = _attrs[name].partition(':')
        mod = importlib.import_module(mod_name)
        return getattr(mod, attr_name) if attr_name else mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = (
    "Accordion",
    "Card",
    "Column",
    "Divider",
    "Feed",
    "FloatPanel",
    "FlexBox",
    "GridBox",
    "GridSpec",
    "GridStack",
    "HSpacer",
    "ListLike",
    "ListPanel",
    "Panel",
    "Row",
    "Spacer",
    "Swipe",
    "Tabs",
    "VSpacer",
    "WidgetBox"
)

__dir__ = lambda: list(__all__)
