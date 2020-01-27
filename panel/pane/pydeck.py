"""
Defines a PyDeck Pane which renders a PyDeck plot using a PyDeckPlot
bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

import sys

import param
from pyviz_comms import JupyterComm

from ..viewable import Layoutable
from .base import PaneBase


class PyDeck(PaneBase):
    """
    PyDeck panes allow rendering Deck.Gl/ PyDeck plots in Panel.
    """

    _render_count = param.Integer(default=0, doc="""
        Number of renders, increment to trigger re-render""")

    _updates = True

    priority = 0.8

    @classmethod
    def applies(cls, obj):
        return (
            hasattr(obj, "to_json") and hasattr(obj, "mapbox_key")
            and hasattr(obj, "deck_widget")
        )

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Should return the bokeh model to be rendered.
        """
        if "panel.models.pydeck" not in sys.modules:
            if isinstance(comm, JupyterComm):
                self.param.warning(
                    "PyDeckPlot was not imported on instantiation "
                    "and may not render in a notebook. Restart "
                    "the notebook kernel and ensure you load "
                    "it as part of the extension using:"
                    "\n\npn.extension('pydeck')\n"
                )
            from ..models.pydeck import PyDeckPlot
        else:
            PyDeckPlot = getattr(sys.modules["panel.models.pydeck"], "PyDeckPlot")

        if self.object is None:
            json_input, mapbox_api_key, tooltip = {}, "", False
        else:
            json_input = self.object.to_json()
            mapbox_api_key = self.object.mapbox_key
            tooltip = self.object.deck_widget.tooltip

        properties = {p: getattr(self, p) for p in Layoutable.param if getattr(self, p) is not None}
        model = PyDeckPlot(json_input=json_input, mapbox_api_key=mapbox_api_key,
                           tooltip=tooltip, _render_count=0, **properties)

        if root is None:
            root = model

        if root is None:
            root = model
        self._models[root.ref["id"]] = (model, parent)
        return model

    def _update(self, model):
        if self.object is None:
            model.update(
                json_input={}, mapbox_api_key="", tooltip=False,
            )
            model._render_count += 1
            return

        json_input = self.object.to_json()
        mapbox_api_key = self.object.mapbox_key
        tooltip = self.object.deck_widget.tooltip

        update_json_input = json_input != model.json_input
        update_mapbox_api_key = mapbox_api_key != model.mapbox_api_key
        update_tooltip = tooltip != model.tooltip

        if update_json_input:
            model.json_input = json_input
        if update_mapbox_api_key:
            model.mapbox_api_key = mapbox_api_key
        if update_tooltip:
            model.tooltip = tooltip

        if update_json_input or update_mapbox_api_key or update_tooltip:
            model._render_count += 1
