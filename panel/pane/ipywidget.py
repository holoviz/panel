from __future__ import annotations

import os

from typing import (
    TYPE_CHECKING, Any, ClassVar, Optional,
)

import param

from pyviz_comms import JupyterComm

from ..config import config
from ..models import IPyWidget as _BkIPyWidget
from .base import PaneBase

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class IPyWidget(PaneBase):
    """
    The IPyWidget pane renders any ipywidgets model both in the notebook and
    in a deployed server.

    When rendering ipywidgets on the server you must add `ipywidgets` to
    `pn.extension`. You must not do this in Jupyterlab as this may render
    Jupyterlab unusable.

    Reference: https://panel.holoviz.org/reference/panes/IPyWidget.html

    :Example:

    >>> IPyWidget(some_ipywidget)
    """

    priority: ClassVar[float | bool | None] = 0.6

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return (hasattr(obj, 'traits') and hasattr(obj, 'get_manager_state') and hasattr(obj, 'comm'))

    def _resolve_ref(self, pname, value):
        if pname == 'object' and self.applies(value):
            return None, value
        return super()._resolve_ref(pname, value)

    def _get_ipywidget(self, obj, doc, root, comm, **kwargs):
        if isinstance(comm, JupyterComm) and not config.embed and "PANEL_IPYWIDGET" not in os.environ:
            IPyWidget = _BkIPyWidget
        else:
            # panel.io.ipywidgets MUST be loaded before ipywidgets_bokeh
            from ..io.ipywidget import _get_ipywidgets, _on_widget_constructed # isort: skip
            from ipywidgets_bokeh.widget import IPyWidget

            # Ensure all widgets are initialized
            for w in _get_ipywidgets().values():
                _on_widget_constructed(w, doc)

        model = IPyWidget(widget=obj, **kwargs)
        return model

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        if root is None:
            return self.get_root(doc, comm)
        kwargs = self._process_param_change(self._init_params())
        model = self._get_ipywidget(self.object, doc, root, comm, **kwargs)
        self._models[root.ref['id']] = (model, parent)
        return model


class IPyLeaflet(IPyWidget):

    sizing_mode = param.ObjectSelector(default='stretch_width', objects=[
        'fixed', 'stretch_width', 'stretch_height', 'stretch_both',
        'scale_width', 'scale_height', 'scale_both', None])

    priority: float | bool | None = 0.7

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return IPyWidget.applies(obj) and obj._view_module == 'jupyter-leaflet'


class Reacton(IPyWidget):

    def __init__(self, object=None, **params):
        super().__init__(object=object, **params)
        self._rcs = {}

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return getattr(obj, '__module__', 'None').startswith('reacton')

    def _cleanup(self, root: Model | None = None) -> None:
        if root and root.ref['id'] in self._rcs:
            rc = self._rcs.pop(root.ref['id'])
            try:
                rc.close()
            except Exception:
                pass
        super()._cleanup(root)

    def _get_ipywidget(
        self, obj, doc: Document, root: Model, comm: Optional[Comm], **kwargs
    ):
        if not isinstance(comm, JupyterComm) or "PANEL_IPYWIDGET" in os.environ:
            from ..io.ipywidget import Widget  # noqa
        import reacton
        widget, rc = reacton.render(obj)
        self._rcs[root.ref['id']] = rc
        return super()._get_ipywidget(widget, doc, root, comm, **kwargs)
