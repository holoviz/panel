"""
Defines a BrowserInfo component exposing the browser window and
navigator APIs.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Mapping

import param  # type: ignore

from ..models.browser import BrowserInfo as _BkBrowserInfo
from ..reactive import Syncable
from .document import create_doc_if_none_exists
from .state import state

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class BrowserInfo(Syncable):
    """
    The Location component can be made available in a server context
    to provide read and write access to the URL components in the
    browser.
    """

    dark_mode = param.Boolean(default=None, doc="""
        Whether the user prefers dark mode.""")

    device_pixel_ratio = param.Number(default=None, doc="""
        Provides the ratio of the resolution in physical pixels to
        the resolution in CSS pixels for the current display device.""")

    language = param.String(default=None, doc="""
        The preferred language of the user, usually the language of the
        browser UI.""")

    timezone = param.String(default=None, doc="""
        The timezone configured as the local timezone of the user.""")

    timezone_offset = param.Number(default=None, doc="""
        The time offset from UTC in minutes.""")

    webdriver = param.Boolean(default=None, doc="""
        Indicates whether the user agent is controlled by automation.""")

    # Mapping from parameter name to bokeh model property name
    _rename: ClassVar[Mapping[str, str | None]] = {"name": None}

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = _BkBrowserInfo()
        root = root or model
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, self._linked_properties, doc, root, comm)
        return model

    def get_root(
        self, doc: Document | None = None, comm: Comm | None = None,
        preprocess: bool = True
    ) -> 'Model':
        doc = create_doc_if_none_exists(doc)
        root = self._get_model(doc, comm=comm)
        ref = root.ref['id']
        state._views[ref] = (self, root, doc, comm)
        self._documents[doc] = root
        return root

    def _cleanup(self, root: Model | None = None) -> None:
        if root:
            if root.document in self._documents:
                del self._documents[root.document]
            ref = root.ref['id']
        else:
            ref = None
        super()._cleanup(root)
        if ref in state._views:
            del state._views[ref]
