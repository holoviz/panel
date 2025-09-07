"""
Renders Streamz Stream objects.
"""
from __future__ import annotations

import sys

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, ClassVar

import param

from .base import ReplacementPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class Streamz(ReplacementPane):
    """
    The `Streamz` pane renders streamz `Stream` objects emitting arbitrary
    objects, unlike the DataFrame pane which specifically handles streamz
    DataFrame and Series objects and exposes various formatting objects.

    Reference: https://panel.holoviz.org/reference/panes/Streamz.html

    :Example:

    >>> Streamz(some_streamz_stream_object, always_watch=True)
    """

    always_watch = param.Boolean(default=False, doc="""
        Whether to watch even when not displayed.""")

    rate_limit = param.Number(default=0.1, bounds=(0, None), doc="""
        The minimum interval between events.""")

    _rename: ClassVar[Mapping[str, str | None]] = {'rate_limit': None, 'always_watch': None}

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._stream = None
        if self.always_watch:
            self._setup_stream()

    @param.depends('always_watch', 'object', 'rate_limit', watch=True)
    def _setup_stream(self):
        if self.object is None or (self.always_watch and self._stream):
            return
        elif self._stream:
            self._stream.destroy()
            self._stream = None
        if self._pane._models or self.always_watch:
            self._stream = self.object.latest().rate_limit(self.rate_limit).gather()
            self._stream.sink(self._update_inner)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._setup_stream()
        return model

    def _cleanup(self, root: Model | None = None):
        super()._cleanup(root)
        if not self._pane._models and self._stream:
            self._stream.destroy()
            self._stream = None

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if 'streamz' in sys.modules:
            from streamz import Stream
            return isinstance(obj, Stream)
        return False
