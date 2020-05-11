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

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if root is None:
            return self._get_root(doc, comm)

        if isinstance(comm, JupyterComm) and not config.embed:
            IPyWidget = _BkIPyWidget
        else:
            from ipywidgets_bokeh.widget import IPyWidget

        props = self._process_param_change(self._init_properties())
        model = IPyWidget(widget=self.object, **props)
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
