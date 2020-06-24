"""
Defines various Select widgets which allow choosing one or more items
from a list of options.
"""
from __future__ import absolute_import, division, unicode_literals

import sys
import param

from pyviz_comms import JupyterComm

from ..models.enums import ace_themes
from .base import Widget



class Ace(Widget):
    """
    Ace widget allow editing text in an Ace editor.
    """

    value = param.String(doc="State of the current code in the editor")

    annotations = param.List(default=[], doc="""
        List of annotations to add to the editor.""")

    theme = param.ObjectSelector(default="chrome", objects=list(ace_themes),
                                 doc="Theme of the editor")

    filename = param.String(doc="Filename from which to deduce language")

    language = param.String(default='text', doc="Language of the editor")

    print_margin = param.Boolean(default=False, doc="""
        Whether to show the a print margin.""")

    readonly = param.Boolean(default=False, doc="""
        Define if editor content can be modified""")

    _rename = {"value": "code", "name": None}

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if self._widget_type is not None:
            pass
        elif "panel.models.ace" not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning(
                    "AcePlot was not imported on instantiation "
                    "and may not render in a notebook. Restart "
                    "the notebook kernel and ensure you load "
                    "it as part of the extension using:"
                    "\n\npn.extension('ace')\n"
                )
            from ..models.ace import AcePlot

            self._widget_type = AcePlot
        else:
            self._widget_type = getattr(sys.modules["panel.models.ace"], "AcePlot")

        return super(Ace, self)._get_model(doc, root, parent, comm)
