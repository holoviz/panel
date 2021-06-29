"""
Defines various Select widgets which allow choosing one or more items
from a list of options.
"""
import param

from pyviz_comms import JupyterComm

from ..models.enums import ace_themes
from ..util import lazy_load
from .base import Widget


class Ace(Widget):
    """
    Ace widget allow editing text in an Ace editor.
    """

    annotations = param.List(default=[], doc="""
        List of annotations to add to the editor.""")

    filename = param.String(doc="Filename from which to deduce language")

    language = param.String(default='text', doc="Language of the editor")

    print_margin = param.Boolean(default=False, doc="""
        Whether to show the a print margin.""")

    readonly = param.Boolean(default=False, doc="""
        Define if editor content can be modified. Alias for disabled.""")

    theme = param.ObjectSelector(default="chrome", objects=list(ace_themes),
                                 doc="Theme of the editor")

    value = param.String(doc="State of the current code in the editor")

    _rename = {"value": "code", "name": None}

    def __init__(self, **params):
        if 'readonly' in params:
            params['disabled'] = params['readonly']
        elif 'disabled' in params:
            params['readonly'] = params['disabled']
        super().__init__(**params)
        self.param.watch(self._update_disabled, ['disabled', 'readonly'])
        self.jslink(self, readonly='disabled', bidirectional=True)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if self._widget_type is None:
            self._widget_type = lazy_load(
                'panel.models.ace', 'AcePlot', isinstance(comm, JupyterComm)
            )
        return super()._get_model(doc, root, parent, comm)

    def _update_disabled(self, *events):
        for event in events:
            if event.name == 'disabled':
                self.readonly = event.new
            elif event.name == 'readonly':
                self.disabled = event.new
