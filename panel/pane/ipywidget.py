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

    def _get_ipywidget(self, obj, doc, root, comm, **kwargs):
        if isinstance(comm, JupyterComm) and not config.embed and not "PANEL_IPYWIDGET" in os.environ:
            IPyWidget = _BkIPyWidget
        else:
            import ipykernel

            from ipywidgets_bokeh.widget import IPyWidget

            from ..io.ipywidget import PanelKernel

            # Patch font-awesome CSS
            IPyWidget.__css__ = [
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.5.0/css/font-awesome.css"
            ]

            if not isinstance(ipykernel.kernelbase.Kernel._instance, PanelKernel):
                kernel = PanelKernel(document=doc, key=str(id(doc)).encode('utf-8'))
                # Support ipywidgets >=8.0 and <8.0
                widgets = (obj._active_widgets if hasattr(obj, '_active_widgets') else obj.widgets).values()
                for w in widgets:
                    w.comm.kernel = kernel
                    w.comm.open()

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
