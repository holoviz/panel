"""
Defines a PyDeck Pane which renders a PyDeck plot using a PyDeckPlot
bokeh model.
"""
from __future__ import annotations

import json
import sys

from collections import defaultdict
from typing import (
    TYPE_CHECKING, Any, ClassVar, Dict, Mapping, Optional,
)

import numpy as np
import param

from bokeh.core.serialization import Serializer
from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

from ..util import is_dataframe, lazy_load
from .base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


def lower_camel_case_keys(attrs):
    """
    Makes all the keys in a dictionary camel-cased and lower-case

    Parameters
    ----------
    attrs : dict
        Dictionary for which all the keys should be converted to camel-case
    """
    for snake_key in list(attrs.keys()):
        if '_' not in snake_key:
            continue
        camel_key = lower_first_letter(to_camel_case(snake_key))
        attrs[camel_key] = attrs.pop(snake_key)


def to_camel_case(snake_case: str) -> str:
    """
    Makes a snake case string into a camel case one

    Parameters
    -----------
    snake_case : str
        Snake-cased string (e.g., "snake_cased") to be converted to camel-case (e.g., "camelCase")
    """
    output_str = ''
    should_upper_case = False
    for c in snake_case:
        if c == '_':
            should_upper_case = True
            continue
        output_str = output_str + c.upper() if should_upper_case else output_str + c
        should_upper_case = False
    return output_str


def lower_first_letter(s: str) -> str:
    return s[:1].lower() + s[1:] if s else ''


def recurse_data(data):
    if hasattr(data, 'to_json'):
        data = data.__dict__
    if isinstance(data, dict):
        data = dict(data)
        lower_camel_case_keys(data)
        data = {k: recurse_data(v) if k != 'data' else v
                for k, v in data.items()}
    elif isinstance(data, list):
        data = [recurse_data(d) for d in data]
    return data


class DeckGL(ModelPane):
    """
    The `DeckGL` pane renders the Deck.gl
    JSON specification as well as PyDeck plots inside a panel.

    Deck.gl is a very powerful WebGL-powered framework for visual exploratory
    data analysis of large datasets.

    Reference: https://panel.holoviz.org/reference/panes/DeckGL.html

    :Example:

    >>> pn.extension('deckgl')
    >>> DeckGL(
    ...    some_deckgl_dict_or_pydeck_object,
    ...    mapbox_api_key=MAPBOX_KEY, height=600
    ... )
    """

    mapbox_api_key = param.String(default=None, doc="""
        The MapBox API key if not supplied by a PyDeck object.""")

    tooltips = param.ClassSelector(default=True, class_=(bool, dict), doc="""
        Whether to enable tooltips""")

    click_state = param.Dict(default={}, doc="""
        Contains the last click event on the DeckGL plot.""")

    hover_state = param.Dict(default={}, doc="""
        The current hover state of the DeckGL plot.""")

    view_state = param.Dict(default={}, doc="""
        The current view state of the DeckGL plot.""")

    throttle = param.Dict(default={'view': 200, 'hover': 200}, doc="""
        Throttling timeout (in milliseconds) for view state and hover
        events sent from the frontend.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'click_state': 'clickState', 'hover_state': 'hoverState',
        'view_state': 'viewState', 'tooltips': 'tooltip'
    }

    _pydeck_encoders_are_added: ClassVar[bool] = False

    _updates: ClassVar[bool] = True

    priority: ClassVar[float | bool | None] = None

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if cls.is_pydeck(obj):
            return 0.8
        elif isinstance(obj, (dict, str)):
            return 0
        return False

    @classmethod
    def is_pydeck(cls, obj):
        if 'pydeck' in sys.modules:
            import pydeck
            return isinstance(obj, pydeck.bindings.deck.Deck)
        return False

    @classmethod
    def _process_data(cls, data):
        columns = defaultdict(list)
        for d in data:
            for col, val in d.items():
                columns[col].append(val)
        return {col: np.asarray(vals) for col, vals in columns.items()}

    @classmethod
    def _update_sources(cls, json_data, sources):
        layers = json_data.get('layers', [])

        # Create index of sources by columns
        source_columns = defaultdict(list)
        for i, source in enumerate(sources):
            key = tuple(sorted(source.data.keys()))
            source_columns[key].append((i, source))

        # Process
        unprocessed, unused = [], list(sources)
        for layer in layers:
            data = layer.get('data')
            if is_dataframe(data):
                data = ColumnDataSource.from_df(data)
            elif (isinstance(data, list) and data
                  and isinstance(data[0], dict)):
                data = cls._process_data(data)
            else:
                continue

            key = tuple(sorted(data.keys()))
            existing = source_columns.get(key)
            if existing:
                index, cds = existing.pop()
                layer['data'] = index
                updates = {}
                for col, values in data.items():
                    if not np.array_equal(data[col], cds.data[col]):
                        updates[col] = values
                if updates:
                    cds.data.update(updates)
                unused.remove(cds)
            else:
                unprocessed.append((layer, data))

        for layer, data in unprocessed:
            if unused:
                cds = unused.pop()
                cds.data = data
            else:
                cds = ColumnDataSource(data)
                sources.append(cds)
            layer['data'] = sources.index(cds)

    @classmethod
    def _add_pydeck_encoders(cls):
        if cls._pydeck_encoders_are_added or 'pydeck' not in sys.modules:
            return

        from pydeck.types import String
        def pydeck_string_encoder(obj, serializer):
            return obj.value

        Serializer._encoders[String] = pydeck_string_encoder

    def _transform_deck_object(self, obj):
        data = dict(obj.__dict__)
        mapbox_api_key = data.pop('mapbox_key', "") or self.mapbox_api_key
        deck_widget = data.pop('deck_widget', None)
        if isinstance(self.tooltips, dict) or deck_widget is None:
            tooltip = self.tooltips
        else:
            tooltip = deck_widget.tooltip
        data = {k: v for k, v in recurse_data(data).items() if v is not None}

        if "initialViewState" in data:
            data["initialViewState"]={
                k:v for k, v in data["initialViewState"].items() if v is not None
            }

        self._add_pydeck_encoders()

        return data, tooltip, mapbox_api_key

    def _transform_object(self, obj) -> Dict[str, Any]:
        if self.object is None:
            data, mapbox_api_key, tooltip = {}, self.mapbox_api_key, self.tooltips
        elif isinstance(self.object, (str, dict)):
            if isinstance(self.object, str):
                data = json.loads(self.object)
            else:
                data = dict(self.object)
                data['layers'] = [dict(layer) for layer in data.get('layers', [])]
            mapbox_api_key = self.mapbox_api_key
            tooltip = self.tooltips
        else:
            data, tooltip, mapbox_api_key = self._transform_deck_object(self.object)

        # Delete undefined width and height
        for view in data.get('views', []):
            if view.get('width', False) is None:
                view.pop('width')
            if view.get('height', False) is None:
                view.pop('height')

        return dict(data=data, tooltip=tooltip, mapbox_api_key=mapbox_api_key or "")

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        self._bokeh_model = DeckGLPlot = lazy_load(
            'panel.models.deckgl', 'DeckGLPlot', isinstance(comm, JupyterComm), root
        )
        properties = self._get_properties(doc)
        data = properties.pop('data')
        properties['data_sources'] = sources = []
        self._update_sources(data, sources)
        properties['layers'] = data.pop('layers', [])
        properties['initialViewState'] = data.pop('initialViewState', {})
        model = DeckGLPlot(data=data, **properties)
        root = root or model
        self._link_props(model, ['clickState', 'hoverState', 'viewState'], doc, root, comm)
        self._models[root.ref["id"]] = (model, parent)
        return model

    def _update(self, ref: str, model: Model) -> None:
        properties = self._get_properties(model.document)
        data = properties.pop('data')
        self._update_sources(data, model.data_sources)
        properties['data'] = data
        properties['layers'] = data.pop('layers', [])
        properties['initialViewState'] = data.pop('initialViewState', {})
        model.update(**properties)
