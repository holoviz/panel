from __future__ import annotations

from typing import Any

import bokeh.core.properties as bp

from bokeh.events import ModelEvent
from bokeh.model import DataModel

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty
from .layout import HTMLBox


class ESMEvent(ModelEvent):

    event_name = 'esm_event'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)

    def event_values(self) -> dict[str, Any]:
        return dict(super().event_values(), data=self.data)


class ReactiveESM(HTMLBox):

    children = bp.List(bp.String)

    data = bp.Instance(DataModel)

    dev = bp.Bool(False)

    esm = bp.String()

    importmap = bp.Dict(bp.String, bp.Dict(bp.String, bp.String))

    __javascript_modules_raw__ = [
        f"{config.npm_cdn}/es-module-shims@^1.10.0/dist/es-module-shims.min.js"
    ]

    @classproperty
    def __javascript_modules__(cls):
        return bundled_files(cls, 'javascript_modules')


class ReactComponent(ReactiveESM):
    """
    Renders jsx/tsx based ESM bundles using React.
    """

    react_version = bp.String('18.3.1')


class AnyWidgetComponent(ReactComponent):
    """
    Renders AnyWidget esm definitions by adding a compatibility layer.
    """
