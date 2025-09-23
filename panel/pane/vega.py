from __future__ import annotations

import re
import sys

from collections.abc import Mapping
from copy import deepcopy
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np
import param
import requests

from bokeh.models import ColumnDataSource
from pyviz_comms import JupyterComm

from ..io import cache
from ..util import lazy_load
from .base import ModelPane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

SCHEMA_URL = "https://vega.github.io/schema/vega-lite/v5.json"

_VEGA_ZOOMABLE_MAP_ITEMS = {
    "params": [
        {"name": "tx", "update": "width / 2"},
        {"name": "ty", "update": "height / 2"},
        {
            "name": "scale",
            "value": 300,
            "on": [{"events": {"type": "wheel", "consume": True}, "update": "clamp(scale * pow(1.003, -event.deltaY * pow(16, event.deltaMode)), 150, 50000)"}],
        },
        {"name": "angles", "value": [0, 0], "on": [{"events": "pointerdown", "update": "[rotateX, centerY]"}]},
        {"name": "cloned", "value": None, "on": [{"events": "pointerdown", "update": "copy('projection')"}]},
        {"name": "start", "value": None, "on": [{"events": "pointerdown", "update": "invert(cloned, xy())"}]},
        {"name": "drag", "value": None, "on": [{"events": "[pointerdown, window:pointerup] > window:pointermove", "update": "invert(cloned, xy())"}]},
        {"name": "delta", "value": None, "on": [{"events": {"signal": "drag"}, "update": "[drag[0] - start[0], start[1] - drag[1]]"}]},
        {"name": "rotateX", "value": -240, "on": [{"events": {"signal": "delta"}, "update": "angles[0] + delta[0]"}]},
        {"name": "centerY", "value": 40, "on": [{"events": {"signal": "delta"}, "update": "clamp(angles[1] + delta[1], -60, 60)"}]},
    ],
    "projection": {
        "scale": {"signal": "scale"},
        "rotate": [{"signal": "rotateX"}, 0, 0],
        "center": [0, {"signal": "centerY"}],
        "translate": [{"signal": "tx"}, {"signal": "ty"}]
    }
}


def ds_as_cds(dataset):
    """
    Converts Vega dataset into Bokeh ColumnDataSource data
    """
    import pandas as pd
    if isinstance(dataset, pd.DataFrame):
        return {k: dataset[k].values for k in dataset.columns}
    if len(dataset) == 0:
        return {}
    # create a list of unique keys from all items as some items may not include optional fields
    keys = sorted({k for d in dataset for k in d.keys()})
    data = {k: [] for k in keys}
    for item in dataset:
        for k in keys:
            data[k].append(item.get(k))
    data = {k: np.asarray(v) for k, v in data.items()}
    return data


_containers = ['hconcat', 'vconcat', 'layer']

SCHEMA_REGEX = re.compile(r'^v(\d+)\.\d+\.\d+.json')

def _isin(obj, attr):
    if isinstance(obj, dict):
        return attr in obj
    else:
        return hasattr(obj, attr)

def _get_type(spec, version):
    if version >= 5:
        if isinstance(spec, dict):
            return spec.get('select', {}).get('type', 'interval')
        elif isinstance(spec.select, dict):
            return spec.select.get('type', 'interval')
        else:
            return getattr(spec.select, 'type', 'interval')
    else:
        if isinstance(spec, dict):
            return spec.get('type', 'interval')
        else:
            return getattr(spec, 'type', 'interval')

def _get_dimensions(spec, props):
    dimensions = {}
    responsive_height = spec.get('height') == 'container' and props.get('height') is None
    responsive_width = spec.get('width') == 'container' and props.get('width') is None
    if responsive_height and responsive_width:
        dimensions['sizing_mode'] = 'stretch_both'
    elif responsive_width:
        dimensions['sizing_mode'] = 'stretch_width'
    elif responsive_height:
        dimensions['sizing_mode'] = 'stretch_height'
    return dimensions

def _get_schema_version(obj, default_version: int = 5) -> int:
    if Vega.is_altair(obj):
        schema = obj.to_dict().get('$schema', '')
    else:
        schema = obj.get('$schema', '')
    version = schema.split('/')[-1]
    match = SCHEMA_REGEX.fullmatch(version)
    if match is None or not match.groups():
        return default_version
    return int(match.groups()[0])

def _get_selections(obj, version=None):
    if obj is None:
        return {}
    elif version is None:
        version = _get_schema_version(obj)
    key = 'params' if version >= 5 else 'selection'
    selections = {}
    if _isin(obj, key):
        params = obj[key]
        if version >= 5 and isinstance(params, list):
            params = {
                p.name if hasattr(p, 'name') else p['name']: p for p in params
                if getattr(p, 'param_type', None) == 'selection' or _isin(p, 'select')
            }
        try:
            selections.update({
                name: _get_type(spec, version) for name, spec in params.items()
            })
        except (AttributeError, TypeError):
            pass
    for c in _containers:
        if _isin(obj, c):
            for subobj in obj[c]:
                selections.update(_get_selections(subobj, version=version))
    return selections

def _to_json(obj):
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


class Vega(ModelPane):
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

    selection = param.ClassSelector(class_=param.Parameterized, doc="""
        The Selection object reflects any selections available on the
        supplied vega plot into Python.""")

    show_actions = param.Boolean(default=False, doc="""
        Whether to show Vega actions.""")

    theme = param.Selector(default=None, allow_None=True, objects=[
        'excel', 'ggplot2', 'quartz', 'vox', 'fivethirtyeight', 'dark',
        'latimes', 'urbaninstitute', 'googlecharts'], doc="""
        A theme to apply to the plot. Must be one of 'excel', 'ggplot2',
        'quartz', 'vox', 'fivethirtyeight', 'dark', 'latimes',
        'urbaninstitute', or 'googlecharts'.
        """)

    validate = param.Boolean(default=True, doc="""
        Whether to validate the Vega specification against the schema.""")

    priority: ClassVar[float | bool | None] = 0.8

    _rename: ClassVar[Mapping[str, str | None]] = {
        'selection': None, 'debounce': None, 'object': 'data', 'validate': None}

    _updates: ClassVar[bool] = True

    def __init__(self, object=None, **params):
        if isinstance(object, dict) and "$schema" not in object:
            self.param.warning(f"No $schema found; using {SCHEMA_URL} by default. Specify the schema explicitly to avoid this warning.")
            object["$schema"] = SCHEMA_URL
        super().__init__(object, **params)
        self.param.watch(self._update_selections, ['object'])
        self._update_selections()

    @cache
    def _download_vega_lite_schema(self, schema_url: str | bytes) -> dict:
        response = requests.get(schema_url, timeout=5)
        return response.json()

    @staticmethod
    def _format_validation_error(error: Exception) -> str:
        """Format JSONSchema validation errors into a readable message."""
        errors: dict[str, str] = {}
        last_path = ""
        rejected_paths = set()

        def process_error(err):
            nonlocal last_path
            path = err.json_path
            if errors and path == "$":
                return  # these $ downstream errors are due to upstream errors
            if err.validator != "anyOf":
                # other downstream errors that are due to upstream errors
                # $.encoding.x.sort: '-host_count' is not one of ..
                #$.encoding.x: 'value' is a required property
                if (
                    (last_path != path
                    and last_path.split(path)[-1].count(".") <= 1)
                    or path in rejected_paths
                ):
                    rejected_paths.add(path)
                # if we have a more specific error message, e.g. enum, don't overwrite it
                elif path in errors and err.validator in ("const", "type"):
                    pass
                else:
                    errors[path] = f"{path}: {err.message}"
            last_path = path
            if err.context:
                for e in err.context:
                    process_error(e)

        process_error(error)
        return "\n".join(errors.values())

    @param.depends("object", watch=True, on_init=True)
    def _validate_object(self):
        try:
            from jsonschema import (  # type: ignore[import-untyped]
                Draft7Validator, ValidationError,
            )
        except ImportError:
            return  # Skip validation if jsonschema is not available

        object = self.object
        if not self.validate or not object or not isinstance(object, dict):
            return

        schema = object.get('$schema', '')
        if not schema:
            raise ValidationError("No $schema found on Vega object")

        try:
            schema = self._download_vega_lite_schema(schema)
        except Exception as e:
            self.param.warning(f"Skipping validation because could not load Vega schema at {schema}: {e}")
            return

        try:
            vega_validator = Draft7Validator(schema)
            # the zoomable params work, but aren't officially valid
            # so we need to remove them for validation
            # https://stackoverflow.com/a/78342773/9324652
            object_copy = deepcopy(object)
            for key in _VEGA_ZOOMABLE_MAP_ITEMS.get("projection", {}):
                object_copy.get("projection", {}).pop(key, None)
            object_copy.pop("params", None)
            # Use dummy URL to avoid $.data: 'url' is a required property
            # when data is an inline dict / dataframe
            object_copy["data"] = {"url": "dummy_url"}
            vega_validator.validate(object_copy)
        except ValidationError as e:
            raise ValidationError(self._format_validation_error(e)) from e

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
            e: param.Dict(allow_refs=False) if stype == 'interval' else param.List(allow_refs=False)
            for e, stype in self._selections.items()
        }
        if self.selection and (set(self.selection.param) - {'name'}) == set(params):
            self.selection.param.update({p: None for p in params})
            return
        self.selection = type('Selection', (param.Parameterized,), params)()

    @classmethod
    def is_altair(cls, obj):
        if 'altair' in sys.modules:
            import altair as alt
            return isinstance(obj, alt.api.TopLevelMixin)
        return False

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        if isinstance(obj, dict) and 'vega' in obj.get('$schema', '').lower():
            return True
        return cls.is_altair(obj)

    def _get_sources(self, json, sources=None):
        sources = {} if sources is None else dict(sources)
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
            if data is not None and not (isinstance(data, dict) and not data):
                sources['data'] = ColumnDataSource(data=ds_as_cds(data))
        elif isinstance(data, list):
            for d in data:
                if 'values' in d:
                    sources[d['name']] = ColumnDataSource(data=ds_as_cds(d.pop('values')))
        return sources

    def _process_event(self, event):
        name = event.data['type']
        stype = self._selections.get(name)
        value = event.data['value']
        if stype != 'interval':
            value = list(value)
        self.selection.param.update(**{name: value})

    def _process_param_change(self, params):
        props = super()._process_param_change(params)
        if 'data' in props and props['data'] is not None:
            props['data'] = _to_json(props['data'])
        return props

    def _get_properties(self, doc, sources={}):
        props = super()._get_properties(doc)
        data = props['data']
        if data is not None:
            sources = self._get_sources(data, sources)
        if self.sizing_mode and data:
            if 'both' in self.sizing_mode:
                if 'width' in data:
                    data['width'] = 'container'
                if 'height' in data:
                    data['height'] = 'container'
            elif 'width' in self.sizing_mode and 'width' in data:
                data['width'] = 'container'
            elif 'height' in self.sizing_mode and 'height' in data:
                data['height'] = 'container'
        dimensions = _get_dimensions(data, props) if data else {}
        props['data'] = data
        props['data_sources'] = sources
        props['events'] = list(self._selections)
        props['throttle'] = self._throttle
        props.update(dimensions)
        return props

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        Vega._bokeh_model = lazy_load(
            'panel.models.vega', 'VegaPlot', isinstance(comm, JupyterComm), root
        )
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('vega_event', model=model, doc=doc, comm=comm)
        return model

    def _update(self, ref: str, model: Model) -> None:
        props = self._get_properties(model.document, sources=dict(model.data_sources))
        model.update(**props)
