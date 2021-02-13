import param

from six import string_types
from pyviz_comms import JupyterComm

from ..util import lazy_load
from .base import PaneBase


class Ace(PaneBase):
    """
    Ace panes allow rendering Ace editor.
    """

    annotations = param.List(default=[], doc="""
        List of annotations to add to the editor.""")

    language = param.String(default='python', doc="""
        Language of the editor.""")

    object = param.String(default='', allow_None=True, doc="""
        The code to be displayed.""")

    theme = param.String(default='chrome', doc="Theme of the editor.")

    readonly = param.Boolean(default=False, doc="""
        Define if editor content can be modified.""")

    priority = 0

    _rename = {'object': 'code'}

    _updates = True

    @classmethod
    def applies(cls, obj):
        return None if isinstance(obj, string_types) else False

    def _get_model(self, doc, root=None, parent=None, comm=None):
        AcePlot = lazy_load('panel.models.ace', 'AcePlot', isinstance(comm, JupyterComm))
        print(AcePlot)
        props = self._process_param_change(self._init_params())
        model = AcePlot(code=self.object or '', **props)
        if root is None:
            root = model
        self._link_props(model, ['code', 'language', 'theme', 'annotations', 'readonly'], doc, root, comm)
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, ref=None, model=None):
        model.code = self.object if self.object else ''
