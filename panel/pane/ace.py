import sys

import param

from six import string_types
from pyviz_comms import JupyterComm

from .base import PaneBase


class Ace(PaneBase):
    """
    Ace panes allow rendering Ace editor.
    """

    annotations = param.List(default=[], doc="List of annotations to add to the editor")

    language = param.String(default='python', doc="Language of the editor")

    object = param.String(default='', allow_None=True, doc="""
        The code to be displayed.""")

    theme = param.String(default='chrome', doc="Theme of the editor")

    readonly = param.Boolean(default=False, doc="Define if editor content can be modified")

    priority = 0

    _rename = {'object': 'code'}

    _updates = True

    @classmethod
    def applies(cls, obj):
        if isinstance(obj, string_types):
            return None
        else:
            return False

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        if 'panel.models.ace' not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning('AcePlot was not imported on instantiation '
                                   'and may not render in a notebook. Restart '
                                   'the notebook kernel and ensure you load '
                                   'it as part of the extension using:'
                                   '\n\npn.extension(\'ace\')\n')
            from ..models.ace import AcePlot
        else:
            AcePlot = getattr(sys.modules['panel.models.ace'], 'AcePlot')

        props = self._process_param_change(self._init_properties())
        model = AcePlot(code=self.object or '', **props)
        if root is None:
            root = model
        self._link_props(model, ['code', 'language', 'theme', 'annotations', 'readonly'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, model):
        model.code = self.object if self.object else ''
