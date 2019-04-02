import sys

import param

from pyviz_comms import JupyterComm

from .base import PaneBase

class Ace(PaneBase):
    """
    Ace panes allow rendering Ace editor.
    """
    
    code = param.String(doc="State of the current code in the editor")
    
    theme = param.String(default='chrome', doc="Theme of the editor")
     
    language = param.String(default='python', doc="Language of the editor")
    
    annotations = param.List(doc="List of annotations to add to the editor")

    _updates = False
    
    @classmethod
    def applies(cls, obj):
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
        model = AcePlot(**props)
        if root is None:
            root = model
        self._link_props(model, ['code', 'language', 'theme', 'annotations'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model
