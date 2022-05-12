import sys

from functools import partial

import param
import numpy as np

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

from ..viewable import Layoutable
from ..util import lazy_load
from .base import PaneBase


def ds_as_cds(dataset):
    """
    Converts Vega dataset into Bokeh ColumnDataSource data
    """
    if len(dataset) == 0:
        return {}
    # create a list of unique keys from all items as some items may not include optional fields
    keys = sorted(set(k for d in dataset for k in d.keys()))
    data = {k: [] for k in keys}
    for item in dataset:
        for k in keys:
            data[k].append(item.get(k))
    data = {k: np.asarray(v) for k, v in data.items()}
    return data


_containers = ['hconcat', 'vconcat', 'layer']

def _isin(obj, attr):
    if isinstance(obj, dict):
        return attr in obj
    else:
        return hasattr(obj, attr)

def _get_type(spec):
    if isinstance(spec, dict):
        return spec.get('type', 'interval')
    else:
        return getattr(spec, 'type', 'interval')


def _get_selections(obj):
    selections = {}
    if _isin(obj, 'selection'):
        try:
            selections.update({
                name: _get_type(spec)
                for name, spec in obj['selection'].items()
            })
        except (AttributeError, TypeError):
            pass
    for c in _containers:
        if _isin(obj, c):
            for subobj in obj[c]:
                selections.update(_get_selections(subobj))
    return selections


class Vega(PaneBase):
    """
    The Vega pane renders Vega-lite based plots (including those from Altair)
    inside a panel.

    Note

    - to use the `Vega` pane, the Panel `extension` has to be
    loaded with 'vega' as an argument to ensure that vega.js is initialized.
    - it supports selection events
    - it optimizes the plot rendering by using binary serialization for any
    array data found on the Vega/Altair object, providing huge speedups over
    the standard JSON serialization employed by Vega natively.

    Reference: https://panel.holoviz.org/reference/panes/Vega.html

    :Example:

    >>> pn.extension('vega')
    >>> Vega(some_vegalite_dict_or_altair_object, height=240)
    """

    debounce = param.ClassSelector(default=20, class_=(int, dict), doc="""
        Declares the debounce time in milliseconds either for all
        events or if a dictionary is provided for individual events.""")

    margin = param.Parameter(default=(5, 5, 30, 5), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    selection = param.ClassSelector(class_=param.Parameterized, doc="""
        The Selection object reflects any selections available on the
        supplied vega plot into Python.""")

    show_actions = param.Boolean(default=False, doc="""
        Whether to show Vega actions.""")

    theme = param.ObjectSelector(default=None, allow_None=True, objects=[
        'excel', 'ggplot2', 'quartz', 'vox', 'fivethirtyeight', 'dark',
        'latimes', 'urbaninstitute', 'googlecharts'])

    priority = 0.8

    _rename = {'selection': None, 'debounce': None}

    _updates = True

    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self.param.watch(self._update_selections, ['object'])
        self._update_selections()

    @property
    def _selections(self):
        return _get_selections(self.object)

    @property
    def _throttle(self):
        default = self.param.debounce.default
        if isinstance(self.debounce, dict):
            throttle = {
                sel: self.debounce.get(sel, default)
                for sel in self._selections
            }
        else:
            throttle = {sel: self.debounce or default for sel in self._selections}
        return throttle

    def _update_selections(self, *args):
        params = {
            e: param.Dict() if stype == 'interval' else param.List()
            for e, stype in self._selections.items()
        }
        self.selection = type('Selection', (param.Parameterized,), params)()

    @classmethod
    def is_altair(cls, obj):
        if 'altair' in sys.modules:
            import altair as alt
            return isinstance(obj, alt.api.TopLevelMixin)
        return False

    @classmethod
    def applies(cls, obj):
        if isinstance(obj, dict) and 'vega' in obj.get('$schema', '').lower():
            return True
        return cls.is_altair(obj)

    @classmethod
    def _to_json(cls, obj):
        if isinstance(obj, dict):
            json = dict(obj)
            if 'data' in json:
                data = json['data']
                if isinstance(data, dict):
                    json['data'] = dict(data)
                elif isinstance(data, list):
                    json['data'] = [dict(d) for d in data]
            return json
        return obj.to_dict()

    def _get_sources(self, json, sources):
        datasets = json.get('datasets', {})
        for name in list(datasets):
            if name in sources or isinstance(datasets[name], dict):
                continue
            data = datasets.pop(name)
            if isinstance(data, list) and any(isinstance(d, dict) and 'geometry' in d for d in data):
                # Handle geometry records types
                datasets[name] = data
                continue
            columns = set(data[0]) if data else []
            if self.is_altair(self.object):
                import altair as alt
                if (not isinstance(self.object.data, (alt.Data, alt.UrlData, type(alt.Undefined))) and
                    columns == set(self.object.data)):
                    data = ColumnDataSource.from_df(self.object.data)
                else:
                    data = ds_as_cds(data)
                sources[name] = ColumnDataSource(data=data)
            else:
                sources[name] = ColumnDataSource(data=ds_as_cds(data))
        data = json.get('data', {})
        if isinstance(data, dict):
            data = data.pop('values', {})
            if data:
                sources['data'] = ColumnDataSource(data=ds_as_cds(data))
        elif isinstance(data, list):
            for d in data:
                if 'values' in d:
                    sources[d['name']] = ColumnDataSource(data=ds_as_cds(d.pop('values')))

    @classmethod
    def _get_dimensions(cls, json, props):
        if json is None:
            return

        if 'config' in json and 'view' in json['config']:
            size_config = json['config']['view']
        else:
            size_config = json

        view = {}
        for w in ('width', 'continuousWidth'):
            if w in size_config:
                view['width'] = size_config[w]
        for h in ('height', 'continuousHeight'):
            if h in size_config:
                view['height'] = size_config[h]

        for p in ('width', 'height'):
            if p not in view or isinstance(view[p], str):
                continue
            if props.get(p) is None or p in view and props.get(p) < view[p]:
                v = view[p]
                props[p] = v+22 if isinstance(v, int) else v

        responsive_height = json.get('height') == 'container'
        responsive_width = json.get('width') == 'container'
        if responsive_height and responsive_width:
            props['sizing_mode'] = 'stretch_both'
        elif responsive_width:
            props['sizing_mode'] = 'stretch_width'
        elif responsive_height:
            props['sizing_mode'] = 'stretch_height'

    def _process_event(self, event):
        name = event.data['type']
        stype = self._selections.get(name)
        value = event.data['value']
        if stype != 'interval':
            value = list(value)
        self.selection.param.update(**{name: value})

    def _get_model(self, doc, root=None, parent=None, comm=None):
        VegaPlot = lazy_load('panel.models.vega', 'VegaPlot', isinstance(comm, JupyterComm), root)
        sources = {}
        if self.object is None:
            json = None
        else:
            json = self._to_json(self.object)
            self._get_sources(json, sources)
        props = self._process_param_change(self._init_params())
        self._get_dimensions(json, props)
        model = VegaPlot(
            data=json, data_sources=sources, events=list(self._selections),
            throttle=self._throttle, **props
        )
        if comm:
            model.on_event('vega_event', self._comm_event)
        else:
            model.on_event('vega_event', partial(self._server_event, doc))
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _update(self, ref=None, model=None):
        if self.object is None:
            json = None
        else:
            json = self._to_json(self.object)
            self._get_sources(json, model.data_sources)
        props = {p : getattr(self, p) for p in list(Layoutable.param)
                 if getattr(self, p) is not None}
        props['throttle'] = self._throttle
        props['events'] = list(self._selections)
        self._get_dimensions(json, props)
        props['data'] = json
        model.update(**props)
