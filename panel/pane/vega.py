import sys

import param
import numpy as np

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

from ..viewable import Layoutable
from ..util import lazy_load, string_types
from .base import PaneBase


def ds_as_cds(dataset):
    """
    Converts Vega dataset into Bokeh ColumnDataSource data
    """
    if len(dataset) == 0:
        return {}
    data = {k: [] for k, v in dataset[0].items()}
    for item in dataset:
        for k, v in item.items():
            data[k].append(v)
    data = {k: np.asarray(v) for k, v in data.items()}
    return data


class Vega(PaneBase):
    """
    Vega panes allow rendering Vega plots and traces.

    For efficiency any array objects found inside a Figure are added
    to a ColumnDataSource which allows using binary transport to sync
    the figure on bokeh server and via Comms.
    """

    margin = param.Parameter(default=(5, 5, 30, 5), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    priority = 0.8

    _updates = True

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
            if p not in view or isinstance(view[p], string_types):
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

    def _get_model(self, doc, root=None, parent=None, comm=None):
        VegaPlot = lazy_load('panel.models.vega', 'VegaPlot', isinstance(comm, JupyterComm))
        sources = {}
        if self.object is None:
            json = None
        else:
            json = self._to_json(self.object)
            self._get_sources(json, sources)
        props = self._process_param_change(self._init_params())
        self._get_dimensions(json, props)
        model = VegaPlot(data=json, data_sources=sources, **props)
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
        self._get_dimensions(json, props)
        props['data'] = json
        model.update(**props)
