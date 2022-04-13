"""
Defines a PyDeck Pane which renders a PyDeck plot using a PyDeckPlot
bokeh model.
"""
import json

from collections import defaultdict

import numpy as np
import param

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

from ..util import is_dataframe, lazy_load
from ..viewable import Layoutable
from .base import PaneBase


def lower_camel_case_keys(attrs):
    """Makes all the keys in a dictionary camel-cased and lower-case

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


def to_camel_case(snake_case):
    """Makes a snake case string into a camel case one

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


def lower_first_letter(s):
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


class DeckGL(PaneBase):
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

    _rename = {
        'click_state': 'clickState', 'hover_state': 'hoverState',
        'view_state': 'viewState', 'tooltips': 'tooltip'
    }

    _updates = True

    priority = None

    @classmethod
    def applies(cls, obj):
        if (hasattr(obj, "to_json") and hasattr(obj, "mapbox_key")
            and hasattr(obj, "deck_widget")):
            return 0.8
        elif isinstance(obj, (dict, str)):
            return 0
        return False

    def _get_properties(self, layout=True):
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
            data = dict(self.object.__dict__)
            mapbox_api_key = data.pop('mapbox_key', self.mapbox_api_key)
            deck_widget = data.pop('deck_widget', None)
            tooltip = self.tooltips if isinstance(self.tooltips, dict) else deck_widget.tooltip
            data = {k: v for k, v in recurse_data(data).items() if v is not None}

        # Delete undefined width and height
        for view in data.get('views', []):
            if view.get('width', False) is None:
                view.pop('width')
            if view.get('height', False) is None:
                view.pop('height')

        if layout:
            properties = {p: getattr(self, p) for p in Layoutable.param
                          if getattr(self, p) is not None}
        else:
            properties = {}
        return data, dict(properties, tooltip=tooltip, mapbox_api_key=mapbox_api_key or "")

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

    def _get_model(self, doc, root=None, parent=None, comm=None):
        DeckGLPlot = lazy_load(
            'panel.models.deckgl', 'DeckGLPlot', isinstance(comm, JupyterComm), root
        )
        data, properties = self._get_properties()
        properties['data_sources'] = sources = []
        self._update_sources(data, sources)
        properties['layers'] = data.pop('layers', [])
        properties['initialViewState'] = data.pop('initialViewState', {})
        model = DeckGLPlot(data=data, **properties)
        root = root or model
        self._link_props(model, ['clickState', 'hoverState', 'viewState'], doc, root, comm)
        self._models[root.ref["id"]] = (model, parent)
        return model

    def _update(self, ref=None, model=None):
        data, properties = self._get_properties(layout=False)
        self._update_sources(data, model.data_sources)
        properties['data'] = data
        properties['layers'] = data.pop('layers', [])
        properties['initialViewState'] = data.pop('initialViewState', {})
        model.update(**properties)
