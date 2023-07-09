from __future__ import annotations

from typing import (
    TYPE_CHECKING, ClassVar, List, Type,
)

from ..io.resources import CDN_DIST
from ..layout.base import Column
from ..models import ScrollLog as BkScrollLog

if TYPE_CHECKING:
    from bokeh.model import Model


class ScrollLog(Column):
    """
    A `ScrollLog` layout allows arranging multiple panel objects in a
    scrollable, vertical container with a header bar.

    Reference: https://panel.holoviz.org/reference/layouts/ScrollLog.html
    """

    _bokeh_model: ClassVar[Type[Model]] = BkScrollLog

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}/layout/scrolllog.css"]

    def __init__(self, *objects, **params):
        if "sizing_mode" not in params:
            params["sizing_mode"] = "stretch_width"
        super().__init__(objects=list(objects), **params)
