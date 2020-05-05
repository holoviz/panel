import sys

from io import BytesIO

import param

from bokeh.models import LayoutDOM, CustomJS, Spacer as BkSpacer

from ..models import IPyWidget as _BkIPyWidget
from .base import PaneBase



class IPyWidget(PaneBase):

    @classmethod
    def applies(cls, obj):
        return (hasattr(obj, 'traits') and hasattr(obj, 'get_manager_state') and hasattr(obj, 'comm'))

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if root is None:
            return self._get_root(doc, comm)

        if comm:
            IPyWidget = _BkIPyWidget
        else:
            from ipywidgets_bokeh.widget import IPyWidget

        model = IPyWidget(widget=self.object)
        self._models[root.ref['id']] = (model, parent)
        return model
