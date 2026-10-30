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
from .accordion import Accordion  # noqa
from .base import (  # noqa
    Column, ListLike, ListPanel, Panel, Row, WidgetBox,
)
from .card import Card  # noqa
from .feed import Feed  # noqa
from .flex import FlexBox  # noqa
from .float import FloatPanel  # noqa
from .grid import GridBox, GridSpec  # noqa
from .gridstack import GridStack  # noqa
from .modal import Modal
from .spacer import (  # noqa
    Divider, HSpacer, Spacer, VSpacer,
)
from .swipe import Swipe  # noqa
from .tabs import Tabs  # noqa

# NOTE: `overlay` must be imported last -- the `isort:skip` pins it here
# (same pattern as `custom`/`chat` in panel/__init__.py) so `ruff --fix`
# can't sort it back up. It's the only layout module that reaches into
# `..custom` (for `JSComponent`), which transitively imports `..pane` ->
# `pane.holoviews`, which reaches back into `panel.layout` for `HSpacer`,
# `Row`, etc. Since `panel/__init__.py` imports `layout` before `pane`,
# that reach-back hits a partially-initialized `panel.layout`; importing
# `overlay` before `spacer` (which defines `HSpacer`) would raise a
# circular ImportError.
from .overlay import Overlay  # isort:skip # noqa

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
    "Modal",
    "Overlay",
    "Panel",
    "Row",
    "Spacer",
    "Swipe",
    "Tabs",
    "VSpacer",
    "WidgetBox"
)
