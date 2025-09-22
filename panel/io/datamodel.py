from __future__ import annotations

import sys

from functools import partial
from typing import Any
from weakref import WeakKeyDictionary

import bokeh
import bokeh.core.properties as bp
import param as pm

from bokeh.model import DataModel, Model
from bokeh.models import ColumnDataSource

from ..reactive import Syncable
from ..viewable import Child, Children, Viewable
from .document import unlocked
from .notebook import push
from .state import set_curdoc, state


class Parameterized(bokeh.core.property.bases.Property):
    """ Accept a Parameterized object.

    This property only exists to support type validation, e.g. for "accepts"
    clauses. It is not serializable itself, and is not useful to add to
    Bokeh models directly.

    """
    def validate(self, value, detail=True):
        super().validate(value, detail)

        if isinstance(value, pm.Parameterized):
            return

        msg = "" if not detail else f"expected param.Parameterized, got {value!r}"
        raise ValueError(msg)


class PolarsDataFrame(bokeh.core.property.bases.Property):
    """ Accept Polars DataFrame values.

    This property only exists to support type validation, e.g. for "accepts"
    clauses. It is not serializable itself, and is not useful to add to
    Bokeh models directly.

    """

    def validate(self, value: Any, detail: bool = True) -> None:
        super().validate(value, detail)

        import polars as pl
        if isinstance(value, (pl.DataFrame, pl.LazyFrame)):
            return

        msg = "" if not detail else f"expected Pandas DataFrame, got {value!r}"
        raise ValueError(msg)


class ParameterizedList(bokeh.core.property.bases.Property):
    """ Accept a list of Parameterized objects.

    This property only exists to support type validation, e.g. for "accepts"
    clauses. It is not serializable itself, and is not useful to add to
    Bokeh models directly.

    """

    def validate(self, value, detail=True):
        super().validate(value, detail)

        if isinstance(value, list) and all(isinstance(v, pm.Parameterized) for v in value):
            return

        msg = "" if not detail else f"expected list of param.Parameterized, got {value!r}"
        raise ValueError(msg)


_DATA_MODELS: WeakKeyDictionary[type[pm.Parameterized], type[DataModel]] = WeakKeyDictionary()

# The Bokeh Color property has `_default_help` set which causes
# an error to be raise when Nullable is called on it. This converter
# overrides the Bokeh _help to set it to None and avoid the error.
# See https://github.com/holoviz/panel/issues/3058
def color_param_to_ppt(p, kwargs):
    ppt = bp.Color(**kwargs)
    ppt._help = None
    return ppt


def list_param_to_ppt(p, kwargs):
    item_type = bp.Any
    if isinstance(p.item_type, tuple) and all(issubclass(t, pm.Parameterized) or t is dict for t in p.item_type):
        return bp.List(bp.Either(bp.Dict(bp.String, bp.Any), bp.Instance(DataModel))), [(ParameterizedList, lambda ps: [create_linked_datamodel(p) for p in ps])]
    elif not isinstance(p.item_type, type):
        pass
    elif issubclass(p.item_type, Viewable):
        item_type = bp.Instance(Model)
    elif issubclass(p.item_type, pm.Parameterized):
        return bp.List(bp.Instance(DataModel)), [(ParameterizedList, lambda ps: [create_linked_datamodel(p) for p in ps])]
    return bp.List(item_type, **kwargs)

def class_selector_to_model(p, kwargs):
    if isinstance(p.class_, type) and issubclass(p.class_, Viewable):
        return bp.Nullable(bp.Instance(Model), **kwargs)
    elif isinstance(p.class_, type) and issubclass(p.class_, pm.Parameterized):
        return (bp.Instance(DataModel, **kwargs), [(Parameterized, create_linked_datamodel)])
    else:
        return bp.Any(**kwargs)

def bytes_param(p, kwargs):
    kwargs['default'] = None
    return bp.Nullable(bp.Bytes, **kwargs)

def df_to_dict(df):
    if 'polars' in sys.modules:
        import polars as pl
        if isinstance(df, pl.LazyFrame):
            df = df.collect()
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()
    return ColumnDataSource._data_from_df(df)

PARAM_MAPPING = {
    pm.Array: lambda p, kwargs: bp.Array(bp.Any, **kwargs),
    pm.Boolean: lambda p, kwargs: bp.Bool(**kwargs),
    pm.Bytes: lambda p, kwargs: bytes_param(p, kwargs),
    pm.CalendarDate: lambda p, kwargs: bp.Date(**kwargs),
    pm.CalendarDateRange: lambda p, kwargs: bp.Tuple(bp.Date, bp.Date, **kwargs),
    pm.ClassSelector: class_selector_to_model,
    pm.Color: color_param_to_ppt,
    pm.DataFrame: lambda p, kwargs: (
        bp.ColumnData(bp.Any, bp.Seq(bp.Any), **kwargs),
        [(bp.PandasDataFrame, df_to_dict), (PolarsDataFrame, df_to_dict)]
    ),
    pm.DateRange: lambda p, kwargs: bp.Tuple(bp.Datetime, bp.Datetime, **kwargs),
    pm.Date: lambda p, kwargs: bp.Datetime(**kwargs),
    pm.Dict: lambda p, kwargs: bp.Dict(bp.String, bp.Any, **kwargs),
    pm.Event: lambda p, kwargs: bp.Bool(**kwargs),
    pm.Integer: lambda p, kwargs: bp.Int(**kwargs),
    pm.List: list_param_to_ppt,
    pm.Number: lambda p, kwargs: bp.Either(bp.Float, bp.Bool, **kwargs),
    pm.NumericTuple: lambda p, kwargs: bp.Tuple(*(bp.Float for p in range(p.length)), **kwargs),
    pm.Range: lambda p, kwargs: bp.Tuple(bp.Float, bp.Float, **kwargs),
    pm.String: lambda p, kwargs: bp.String(**kwargs),
    pm.Tuple: lambda p, kwargs: bp.Tuple(*(bp.Any for p in range(p.length)), **kwargs),
    Child: lambda p, kwargs: bp.Nullable(bp.Instance(Model), **kwargs),
    Children: lambda p, kwargs: bp.List(bp.Instance(Model), **kwargs),
}


def construct_data_model(parameterized, name=None, ignore=[], types={}, extras={}):
    """
    Dynamically creates a Bokeh DataModel class from a Parameterized
    object.

    Parameters
    ----------
    parameterized: param.Parameterized | type[param.Parameterized]
        The Parameterized class or instance from which to create the
        DataModel
    name: str or None
        Name of the dynamically created DataModel class
    ignore: list(str)
        List of parameters to ignore.
    types: dict
        A dictionary mapping from parameter name to a Parameter type,
        making it possible to override the default parameter types.
    extras: dict
        Additional properties to define on the DataModel.

    Returns
    -------
    DataModel
    """
    properties = {}
    for pname in parameterized.param:
        if pname in ignore:
            continue
        p = parameterized.param[pname]
        if p.precedence and p.precedence < 0:
            continue
        ptype = types.get(pname, type(p))
        prop = PARAM_MAPPING.get(ptype)
        if isinstance(parameterized, Syncable) or (isinstance(parameterized, type) and issubclass(parameterized, Syncable)):
            pname = parameterized._property_mapping.get(pname, pname)
        if pname == 'name' or pname is None:
            continue
        nullable = getattr(p, 'allow_None', False)
        default = p.default
        kwargs = {'default': default, 'help': p.doc}
        if prop is None:
            bk_prop, accepts = bp.Any(**kwargs), []
        else:
            bkp = prop(p, {} if nullable else kwargs)
            bk_prop, accepts = bkp if isinstance(bkp, tuple) else (bkp, [])
            if nullable:
                bk_prop = bp.Nullable(bk_prop, **kwargs)
        is_valid = bk_prop.is_valid(default)
        for bkp, convert in accepts:
            bk_prop = bk_prop.accepts(bkp, convert)
        properties[pname] = bk_prop
        if not is_valid:
            for tp, converter in bk_prop.alternatives:
                if tp.is_valid(default):
                    bk_prop._default = default = converter(default)
    for pname, ptype in extras.items():
        if issubclass(ptype, pm.Parameter):
            ptype = PARAM_MAPPING.get(ptype)(None, {})
        properties[pname] = ptype
    name = name or parameterized.name
    return type(name, (DataModel,), properties)


def create_linked_datamodel(obj, root=None):
    """
    Creates a Bokeh DataModel from a Parameterized class or instance
    which automatically links the parameters bi-directionally.

    Parameters
    ----------
    obj: param.Parameterized
       The Parameterized class to create a linked DataModel for.

    Returns
    -------
    DataModel instance linked to the Parameterized object.
    """
    if isinstance(obj, type) and issubclass(obj, pm.Parameterized):
        cls = obj
    elif isinstance(obj, pm.Parameterized):
        cls = type(obj)
    else:
        raise TypeError('Can only create DataModel for Parameterized class or instance.')
    if cls in _DATA_MODELS:
        model = _DATA_MODELS[cls]
    else:
        _DATA_MODELS[cls] = model = construct_data_model(obj)
    properties = model.properties()
    props = {k: v for k, v in obj.param.values().items() if k in properties}
    if root:
        props['name'] = f"{root.ref['id']}-{id(obj)}"
    model = model(**props)
    _changing = []

    def cb_bokeh(attr, old, new):
        if attr in _changing:
            return
        try:
            _changing.append(attr)
            obj.param.update(**{attr: new})
        finally:
            _changing.remove(attr)

    def cb_param(*events):
        update = {
            event.name: event.new for event in events
            if event.name not in _changing
        }
        try:
            _changing.extend(list(update))

            tags = [tag for tag in model.tags if tag.startswith('__ref:')]
            if root:
                ref = root.ref['id']
            elif tags:
                ref = tags[0].split('__ref:')[-1]
            else:
                ref = None

            if ref and ref in state._views:
                _, root_model, doc, comm = state._views[ref]
                if comm or state._unblocked(doc) or not doc.session_context:
                    with unlocked():
                        model.update(**update)
                    if comm and 'embedded' not in root_model.tags:
                        push(doc, comm)
                else:
                    cb = partial(model.update, **update)
                    with set_curdoc(doc):
                        state.execute(cb, schedule=True)
            else:
                model.update(**update)
        finally:
            for attr in update:
                _changing.remove(attr)

    for p in obj.param:
        if p in properties:
            model.on_change(p, cb_bokeh)

    obj.param.watch(cb_param, list(set(properties) & set(obj.param)))

    return model
