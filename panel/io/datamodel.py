import weakref

from functools import partial

import bokeh
import bokeh.core.properties as bp
import param as pm

from bokeh.model import DataModel
from bokeh.models import ColumnDataSource

from ..reactive import Syncable
from .document import unlocked
from .notebook import push
from .state import state


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


_DATA_MODELS = weakref.WeakKeyDictionary()

# The Bokeh Color property has `_default_help` set which causes
# an error to be raise when Nullable is called on it. This converter
# overrides the Bokeh _help to set it to None and avoid the error.
# See https://github.com/holoviz/panel/issues/3058
def color_param_to_ppt(p, kwargs):
    ppt = bp.Color(**kwargs)
    ppt._help = None
    return ppt


def list_param_to_ppt(p, kwargs):
    if isinstance(p.item_type, type) and issubclass(p.item_type, pm.Parameterized):
        return bp.List(bp.Instance(DataModel)), [(ParameterizedList, lambda ps: [create_linked_datamodel(p) for p in ps])]
    return bp.List(bp.Any, **kwargs)


PARAM_MAPPING = {
    pm.Array: lambda p, kwargs: bp.Array(bp.Any, **kwargs),
    pm.Boolean: lambda p, kwargs: bp.Bool(**kwargs),
    pm.CalendarDate: lambda p, kwargs: bp.Date(**kwargs),
    pm.CalendarDateRange: lambda p, kwargs: bp.Tuple(bp.Date, bp.Date, **kwargs),
    pm.ClassSelector: lambda p, kwargs: (
        (bp.Instance(DataModel, **kwargs), [(Parameterized, create_linked_datamodel)])
        if isinstance(p.class_, type) and issubclass(p.class_, pm.Parameterized) else
        bp.Any(**kwargs)
    ),
    pm.Color: color_param_to_ppt,
    pm.DataFrame: lambda p, kwargs: (
        bp.ColumnData(bp.Any, bp.Seq(bp.Any), **kwargs),
        [(bp.PandasDataFrame, lambda x: ColumnDataSource._data_from_df(x))]
    ),
    pm.DateRange: lambda p, kwargs: bp.Tuple(bp.Datetime, bp.Datetime, **kwargs),
    pm.Date: lambda p, kwargs: bp.Datetime(**kwargs),
    pm.Dict: lambda p, kwargs: bp.Dict(bp.String, bp.Any, **kwargs),
    pm.Event: lambda p, kwargs: bp.Bool(**kwargs),
    pm.Integer: lambda p, kwargs: bp.Int(**kwargs),
    pm.List: list_param_to_ppt,
    pm.Number: lambda p, kwargs: bp.Float(**kwargs),
    pm.NumericTuple: lambda p, kwargs: bp.Tuple(*(bp.Float for p in range(p.length)), **kwargs),
    pm.Range: lambda p, kwargs: bp.Tuple(bp.Float, bp.Float, **kwargs),
    pm.String: lambda p, kwargs: bp.String(**kwargs),
    pm.Tuple: lambda p, kwargs: bp.Tuple(*(bp.Any for p in range(p.length)), **kwargs),
}



def construct_data_model(parameterized, name=None, ignore=[], types={}):
    """
    Dynamically creates a Bokeh DataModel class from a Parameterized
    object.

    Arguments
    ---------
    parameterized: param.Parameterized
        The Parameterized class or instance from which to create the
        DataModel
    name: str or None
        Name of the dynamically created DataModel class
    ignore: list(str)
        List of parameters to ignore.
    types: dict
        A dictionary mapping from parameter name to a Parameter type,
        making it possible to override the default parameter types.

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
        if isinstance(parameterized, Syncable):
            pname = parameterized._rename.get(pname, pname)
        if pname == 'name' or pname is None:
            continue
        nullable = getattr(p, 'allow_None', False)
        kwargs = {'default': p.default, 'help': p.doc}
        if prop is None:
            bk_prop, accepts = bp.Any(**kwargs), []
        else:
            bkp = prop(p, {} if nullable else kwargs)
            bk_prop, accepts = bkp if isinstance(bkp, tuple) else (bkp, [])
            if nullable:
                bk_prop = bp.Nullable(bk_prop, **kwargs)
        for bkp, convert in accepts:
            bk_prop = bk_prop.accepts(bkp, convert)
        properties[pname] = bk_prop
    name = name or parameterized.name
    return type(name, (DataModel,), properties)


def create_linked_datamodel(obj, root=None):
    """
    Creates a Bokeh DataModel from a Parameterized class or instance
    which automatically links the parameters bi-directionally.

    Arguments
    ---------
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
    model = model(**{k: v for k, v in obj.param.values().items() if k in properties})
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
                _, _, doc, comm = state._views[ref]
                if comm or state._unblocked(doc):
                    with unlocked():
                        model.update(**update)
                    if comm and 'embedded' not in root.tags:
                        push(doc, comm)
                else:
                    cb = partial(model.update, **update)
                    if doc.session_context:
                        doc.add_next_tick_callback(cb)
                    else:
                        cb()
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
