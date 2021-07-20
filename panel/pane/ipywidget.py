import os

import param

from pyviz_comms import JupyterComm

from ..config import config
from ..models import IPyWidget as _BkIPyWidget
from .base import PaneBase


class IPyWidget(PaneBase):

    priority = 0.6

    @classmethod
    def applies(cls, obj):
        return (hasattr(obj, 'traits') and hasattr(obj, 'get_manager_state') and hasattr(obj, 'comm'))

    def _get_ipywidget(self, obj, doc, root, comm, **kwargs):
        if isinstance(comm, JupyterComm) and not config.embed and not "PANEL_IPYWIDGET" in os.environ:
            IPyWidget = _BkIPyWidget
        else:
            import ipykernel
            from ipywidgets_bokeh.widget import IPyWidget
            from ..io.ipywidget import PanelKernel
            if not isinstance(ipykernel.kernelbase.Kernel._instance, PanelKernel):
                kernel = PanelKernel(document=doc, key=str(id(doc)).encode('utf-8'))
                for w in obj.widgets.values():
                    w.comm.kernel = kernel
                    w.comm.open()

        model = IPyWidget(widget=obj, **kwargs)
        return model

    def _get_model(self, doc, root=None, parent=None, comm=None):
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

    priority = 0.7

    @classmethod
    def applies(cls, obj):
        return IPyWidget.applies(obj) and obj._view_module == 'jupyter-leaflet'
