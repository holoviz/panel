"""
Defines a PyDeck Pane which renders a PyDeck plot using a PyDeckPlot
bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

import json
import sys

import param
from pyviz_comms import JupyterComm

from ..util import string_types
from ..viewable import Layoutable
from .base import PaneBase


class DeckGL(PaneBase):
    """
    DeckGL panes allow rendering Deck.Gl/ PyDeck plots in Panel.
    """

    mapbox_api_key = param.String(default=None, doc="""
        The MapBox API key if not supplied by a PyDeck object.""")

    tooltips = param.Boolean(default=True, doc="""
        Whether to enable tooltips""")

    _updates = True

    priority = None

    @classmethod
    def applies(cls, obj):
        if (hasattr(obj, "to_json") and hasattr(obj, "mapbox_key")
            and hasattr(obj, "deck_widget")):
            return 0.8
        elif isinstance(obj, (dict, string_types)):
            return 0
        return False

    def _get_properties(self, layout=True):
        if self.object is None:
            json_input, mapbox_api_key, tooltip = "{}", "", False
        elif isinstance(self.object, (string_types, dict)):
            if isinstance(self.object, string_types):
                json_input = self.object
            else:
                json_input = json.dumps(self.object)
            mapbox_api_key = self.mapbox_api_key
            tooltip = self.tooltips
        else:
            json_input = self.object.to_json()
            mapbox_api_key = self.object.mapbox_key
            tooltip = self.object.deck_widget.tooltip
        if layout:
            properties = {p: getattr(self, p) for p in Layoutable.param
                          if getattr(self, p) is not None}
        else:
            properties = {}
        return dict(properties, json_input=json_input, tooltip=tooltip,
                    mapbox_api_key=mapbox_api_key, **properties)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if "panel.models.deckgl" not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning(
                    "DeckGLPlot was not imported on instantiation "
                    "and may not render in a notebook. Restart "
                    "the notebook kernel and ensure you load "
                    "it as part of the extension using:"
                    "\n\npn.extension('pydeck')\n"
                )
            from ..models.deckgl import DeckGLPlot
        else:
            DeckGLPlot = getattr(sys.modules["panel.models.deckgl"], "DeckGLPlot")
        properties = self._get_properties()
        model = DeckGLPlot(**properties)
        root = root or model
        self._models[root.ref["id"]] = (model, parent)
        return model

    def _update(self, model):
        model.update(**self._get_properties(layout=False))
