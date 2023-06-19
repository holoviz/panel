"""
interactive API

How Interactive works
---------------------

`Interactive` is a wrapper around a Python object that lets users create
interactive pipelines by calling existing APIs on an object with dynamic
parameters or widgets.

An `Interactive` instance watches what operations are applied to the object.

To do so, each operation returns a new `Interactive` instance - the creation
of a new instance being taken care of by the `_clone` method - which allows
the next operation to be recorded, and so on and so forth. E.g. `dfi.head()`
first records that the `'head'` attribute is accessed, this is achieved
by overriding `__getattribute__`. A new interactive object is returned,
which will then record that it is being called, and that new object will be
itself called as `Interactive` implements `__call__`. `__call__`  returns
another `Interactive` instance.

Note that under the hood even more `Interactive` instances may be created,
but this is the gist of it.

To be able to watch all the potential operations that may be applied to an
object, `Interactive` implements on top of `__getattribute__` and
`__call__`:

- operators such as `__gt__`, `__add__`, etc.
- the builtin functions `__abs__` and `__round__`
- `__getitem__`
- `__array_ufunc__`

The `_depth` attribute starts at 0 and is incremented by 1 every time
a new `Interactive` instance is created part of a chain.
The root instance in an expression has a `_depth` of 0. An expression can
consist of multiple chains, such as `dfi[dfi.A > 1]`, as the `Interactive`
instance is referenced twice in the expression. As a consequence `_depth`
is not the total count of `Interactive` instance creations of a pipeline,
it is the count of instances created in the outer chain. In the example, that
would be `dfi[]`. `Interactive` instances don't have references about
the instances that created them or that they create, they just know their
current location in a chain thanks to `_depth`. However, as some parameters
need to be passed down the whole pipeline, they do have to propagate. E.g.
in `dfi.interactive(width=200)`, `width=200` will be propagated as `kwargs`.

Recording the operations applied to an object in a pipeline is done
by gradually building a so-called "dim expression", or "dim transform",
which is an expression language provided by HoloViews. dim transform
objects are a way to express transforms on `Dataset`s, a `Dataset` being
another HoloViews object that is a wrapper around common data structures
such as Pandas/Dask/... Dataframes/Series, Xarray Dataset/DataArray, etc.
For instance a Python expression such as `(series + 2).head()` can be
expressed with a dim transform whose repr will be `(dim('*').pd+2).head(2)`,
effectively showing that the dim transform has recorded the different
operations that are meant to be applied to the data.
The `_transform` attribute stores the dim transform.

The `_obj` attribute holds the original data structure that feeds the
pipeline. All the `Interactive` instances created while parsing the
pipeline share the same `_obj` object. And they all wrap it in a `Dataset`
instance, and all apply the current dim transform they are aware of to
the original data structure to compute the intermediate state of the data,
that is stored it in the `_current_` attribute. Doing so is particularly
useful in Notebook sessions, as this allows to inspect the transformed
object at any point of the pipeline, and as such provide correct
auto-completion and docstrings. E.g. executing `dfi.A.max?` in a Notebook
will correctly return the docstring of the Pandas Series `.max()` method,
as the pipeline evaluates `dfi.A` to hold a current object `_current` that
is a Pandas Series, and no longer and DataFrame.

The `_obj` attribute is implemented as a property which gets/sets the value
from a list that contains the shared attribute. This is required for the
"function as input" to be able to update the object from a callback set up
on the root Interactive instance.

Internally interactive holds the current evaluated state on the `_current_`
attribute, when some parameter in the interactive pipeline is changed
the pipeline is marked as `_dirty`. This means that the next time `_current`
is accessed the pipeline will be re-evaluated to get the up-to-date
current value.

The `_method` attribute is a string that temporarily stores the method/attr
accessed on the object, e.g. `_method` is 'head' in `dfi.head()`, until the
Interactive instance created in the pipeline is called at which point `_method`
is reset to None. In cases such as `dfi.head` or `dfi.A`, `_method` is not
(yet) reset to None. At this stage the Interactive instance returned has
its `_current` attribute not updated, e.g. `dfi.A._current` is still the
original dataframe, not the 'A' series. Keeping `_method` is thus useful for
instance to display `dfi.A`, as the evaluation of the object will check
whether `_method` is set or not, and if it's set it will use it to compute
the object returned, e.g. the series `df.A` or the method `df.head`, and
display its repr.
"""

import operator
import sys

from types import FunctionType, MethodType

import holoviews as hv
import pandas as pd
import param

from .depends import bind, depends, param_value_if_widget
from .layout import Column, HSpacer, Row
from .pane import DataFrame, panel
from .param import ParamFunction
from .util import eval_function, full_groupby, get_method_owner
from .widgets.base import Widget


def _flatten(line):
    """
    Flatten an arbitrarily nested sequence.

    Inspired by: pd.core.common.flatten

    Parameters
    ----------
    line : sequence
        The sequence to flatten

    Notes
    -----
    This only flattens list, tuple, and dict sequences.

    Returns
    -------
    flattened : generator
    """

    for element in line:
        if any(isinstance(element, tp) for tp in (list, tuple, dict)):
            yield from _flatten(element)
        else:
            yield element

def _find_widgets(op):
    widgets = []
    op_args = list(op['args']) + list(op['kwargs'].values())
    op_args = _flatten(op_args)
    for op_arg in op_args:
        # Find widgets introduced as `widget` in an expression
        if isinstance(op_arg, Widget) and op_arg not in widgets:
            widgets.append(op_arg)
        # TODO: Find how to execute this path?
        if isinstance(op_arg, hv.dim):
            for nested_op in op_arg.ops:
                for widget in _find_widgets(nested_op):
                    if widget not in widgets:
                        widgets.append(widget)
        # Find Ipywidgets
        if 'ipywidgets' in sys.modules:
            from ipywidgets import Widget as IPyWidget
            if isinstance(op_arg, IPyWidget) and op_arg not in widgets:
                widgets.append(op_arg)
        # Find widgets introduced as `widget.param.value` in an expression
        if (isinstance(op_arg, param.Parameter) and
            isinstance(op_arg.owner, Widget) and
            op_arg.owner not in widgets):
            widgets.append(op_arg.owner)
        if isinstance(op_arg, slice):
            nested_op = {"args": [op_arg.start, op_arg.stop, op_arg.step], "kwargs": {}}
            for widget in _find_widgets(nested_op):
                if widget not in widgets:
                    widgets.append(widget)
    return widgets


class Wrapper(param.Parameterized):

    object = param.Parameter()


class interactive:
    """
    The `.interactive` API enhances the API of data analysis libraries
    like Pandas, Dask, and Xarray, by allowing to replace in a pipeline
    static values by dynamic widgets. When displayed, an interactive
    pipeline will incorporate the dynamic widgets that control it, as long
    as its normal output that will automatically be updated as soon as a
    widget value is changed.

    `Interactive` can be instantiated with an object. However the recommended
    approach is to instantiate it via the `.interactive` accessor that is
    available on a data structure when it has been patched, e.g. after
    executing `import hvplot.pandas`. The accessor can also be called which
    allows to pass down kwargs.

    A pipeline can then be created from this object, the pipeline will render
    with its widgets and its interactive output.

    Reference: https://hvplot.holoviz.org/user_guide/Interactive.html

    Parameters
    ----------
    obj: DataFrame, Series, DataArray, DataSet
        A supported data structure object
    loc : str, optional
        Widget(s) location, one of 'bottom_left', 'bottom_right', 'right'
        'top-right', 'top-left' and 'left'. By default 'top_left'
    center : bool, optional
        Whether to center to pipeline output, by default False
    max_rows : int, optional
        Maximum number of rows displayed, only used when the output is a
        dataframe, by default 100
    kwargs: optional
        Optional kwargs that are passed down to customize the displayed
        object. E.g. if the output is a DataFrame `width=200` will set
        the size of the DataFrame Pane that renders it.

    Examples
    --------
    Instantiate it from an object:
    >>> dfi = Interactive(df)

    Or with the `.interactive` accessor when the object is patched:
    >>> import hvplot.pandas
    >>> dfi = df.interactive
    >>> dfi = df.interactive(width=200)

    Create interactive pipelines from the `Interactive` object:
    >>> widget = panel.widgets.IntSlider(value=1, start=1, end=5)
    >>> dfi.head(widget)
    """

    # Hackery to support calls to the classic `.plot` API, see `_get_ax_fn`
    # for more hacks!
    _fig = None

    def __new__(cls, obj, **kwargs):
        # __new__ implemented to support functions as input, e.g.
        # hvplot.find(foo, widget).interactive().max()
        wrapper = None
        if 'fn' in kwargs:
            fn = kwargs.pop('fn')
        elif isinstance(obj, (FunctionType, MethodType)):
            fn = panel(obj, lazy=True)
            obj = fn.eval(obj)
        elif isinstance(obj, param.Parameter):
            fn = panel(bind(lambda obj: obj, obj), lazy=True)
            obj = getattr(obj.owner, obj.name)
        elif isinstance(obj, Widget):
            fn = panel(bind(lambda obj: obj, obj), lazy=True)
            obj = obj.value
        else:
            wrapper = Wrapper(object=obj)
            fn = panel(bind(lambda obj: obj, wrapper.param.object), lazy=True)
        clss = cls
        for subcls in cls.__subclasses__():
            if subcls.applies(obj):
                clss = subcls
        inst = super(interactive, cls).__new__(clss)
        inst._shared_obj = kwargs.get('_shared_obj', [obj])
        inst._fn = fn
        inst._wrapper = wrapper
        return inst

    @classmethod
    def applies(cls, obj):
        """
        Subclasses must implement applies and return a boolean to indicate
        whether the subclass should apply or not to the obj.
        """
        return True

    def __init__(self, obj, transform=None, fn=None, plot=False, depth=0,
                 loc='top_left', center=False, dmap=False, inherit_kwargs={},
                 max_rows=100, method=None, _shared_obj=None, _current=None,
                 prev=None, **kwargs):

        # _init is used to prevent to __getattribute__ to execute its
        # specialized code.
        self._init = False
        self._method = method
        self._transform = transform
        self._plot = plot
        self._depth = depth
        self._loc = loc
        self._center = center
        self._dmap = dmap
        self._prev = prev
        # TODO: What's the real use of inherit_kwargs? So far I've only seen
        # it containing 'ax'
        self._inherit_kwargs = inherit_kwargs
        self._max_rows = max_rows
        self._kwargs = kwargs
        self._init = True
        self._dirty = True
        self._current_ = None
        #self.hvplot = _hvplot(self)
        self._setup_invalidations(depth)

    @property
    def _obj(self):
        return self._shared_obj[0]

    @_obj.setter
    def _obj(self, obj):
        if self._shared_obj is None:
            self._shared_obj = [obj]
        else:
            self._shared_obj[0] = obj

    @property
    def _current(self):
        if self._dirty:
            self.eval()
        return self._current_

    @property
    def _fn_params(self):
        if self._fn is None:
            deps = []
        elif isinstance(self._fn, ParamFunction):
            dinfo = getattr(self._fn.object, '_dinfo', {})
            deps = list(dinfo.get('dependencies', [])) + list(dinfo.get('kw', {}).values())
        else:
            # TODO: Find how to execute that path?
            parameterized = get_method_owner(self._fn.object)
            deps = parameterized.param.method_dependencies(self._fn.object.__name__)
        return deps

    @property
    def _params(self):
        ps = self._fn_params
        prev = self._prev
        while prev is not None:
            ps.extend(prev._params)
            prev = prev._prev
        if self._transform is None:
            return ps
        for arg in self._transform['args']:
            if isinstance(arg, interactive):
                for p in  arg._params:
                    if p not in ps:
                        ps.append(p)
                continue
            parg = param_value_if_widget(arg)

            if parg and isinstance(parg, param.Parameter) and parg not in ps:
                ps.append(parg)
        for k, arg in self._transform['kwargs'].items():
            if isinstance(arg, interactive):
                for p in  arg._params:
                    if p not in ps:
                        ps.append(p)
                continue
            parg = param_value_if_widget(arg)
            if parg is None or k == 'ax' or not isinstance(parg, param.Parameter) or parg in ps:
                continue
            ps.append(parg)
        return ps

    def _setup_invalidations(self, depth=0):
        """
        Since the parameters of the pipeline can change at any time
        we have to invalidate the internal state of the pipeline.
        To handle both invalidations of the inputs of the pipeline
        and the pipeline itself we set up watchers on both.

        1. The first invalidation we have to set up is to re-evaluate
           the function that feeds the pipeline. Only the root node of
           a pipeline has to perform this invalidation because all
           leaf nodes inherit the same shared_obj. This avoids
           evaluating the same function for every branch of the pipeline.
        2. The second invalidation is for the pipeline itself, i.e.
           if any parameter changes we have to notify the pipeline that
           it has to re-evaluate the pipeline. This is done by marking
           the pipeline as `_dirty`. The next time the `_current` value
           is requested we then run and `.eval()` pass that re-executes
           the pipeline.
        """
        if self._fn is not None and depth == 0:
            for _, params in full_groupby(self._fn_params, lambda x: id(x.owner)):
                params[0].owner.param.watch(self._update_obj, [p.name for p in params])
        for _, params in full_groupby(self._params, lambda x: id(x.owner)):
            params[0].owner.param.watch(self._invalidate_current, [p.name for p in params])

    def _invalidate_current(self, *events):
        self._dirty = True

    def _update_obj(self, *args):
        self._obj = self._fn.eval(self._fn.object)

    @property
    def _callback(self):
        def evaluate_inner():
            obj = self.eval()
            if isinstance(obj, pd.DataFrame):
                return DataFrame(obj, max_rows=self._max_rows, **self._kwargs)
            return obj
        params = self._params
        if params:
            @depends(*params)
            def evaluate(*args, **kwargs):
                return evaluate_inner()
        else:
            def evaluate():
                return evaluate_inner()
        return evaluate

    def _clone(self, transform=None, plot=None, loc=None, center=None,
               dmap=None, copy=False, max_rows=None, **kwargs):
        plot = self._plot or plot
        transform = transform or self._transform
        loc = self._loc if loc is None else loc
        center = self._center if center is None else center
        dmap = self._dmap if dmap is None else dmap
        max_rows = self._max_rows if max_rows is None else max_rows
        depth = self._depth + 1
        if copy:
            kwargs = dict(self._kwargs, _current=self._current, inherit_kwargs=self._inherit_kwargs, method=self._method, fn=self._fn, prev=self._prev, **kwargs)
        else:
            kwargs = dict(self._inherit_kwargs, prev=self, **dict(self._kwargs, **kwargs))
        return type(self)(self._obj, transform=transform, plot=plot, depth=depth,
                         loc=loc, center=center, dmap=dmap, _shared_obj=self._shared_obj,
                         max_rows=max_rows, **kwargs)

    def _repr_mimebundle_(self, include=[], exclude=[]):
        return self.layout()._repr_mimebundle_()

    def __dir__(self):
        current = self._current
        if self._method:
            current = getattr(current, self._method)
        extras = {attr for attr in dir(current) if not attr.startswith('_')}
        try:
            return sorted(set(super().__dir__()) | extras)
        except Exception:
            return sorted(set(dir(type(self))) | set(self.__dict__) | extras)

    def _resolve_accessor(self):
        if not self._method:
            # No method is yet set, as in `dfi.A`, so return a copied clone.
            return self._clone(copy=True)
        # This is executed when one runs e.g. `dfi.A > 1`, in which case after
        # dfi.A the _method 'A' is set (in __getattribute__) which allows
        # _resolve_accessor to keep building the transform dim expression.
        transform = {
            'fn': operator.getitem,
            'args': self._method,
            'kwargs': {},
            'reverse': False
        }
        inherit_kwargs = {}
        if self._method == 'plot':
            inherit_kwargs['ax'] = self._get_ax_fn()
        try:
            new = self._clone(transform, inherit_kwargs=inherit_kwargs)
        finally:
            # Reset _method for whatever happens after the accessor has been
            # fully resolved, e.g. whatever happens `dfi.A > 1`.
            self._method = None
        return new

    def __getattribute__(self, name):
        self_dict = super().__getattribute__('__dict__')
        if not self_dict.get('_init') or name in ('eval', '_dirty', '_prev', '_transform', '_obj', '_shared_obj', '_method', '_plot', '_eval_transform'):
            return super().__getattribute__(name)

        current = self_dict['_current_']
        dirty = self_dict['_dirty']
        if dirty:
            self.eval()
            current = self_dict['_current_']

        method = self_dict['_method']
        if method:
            current = getattr(current, method)
        # Getting all the public attributes available on the current object,
        # e.g. `sum`, `head`, etc.
        extras = [d for d in dir(current) if not d.startswith('_')]
        if name in extras and name not in super().__dir__():
            new = self._resolve_accessor()
            # Setting the method name for a potential use later by e.g. an
            # operator or method, as in `dfi.A > 2`. or `dfi.A.max()`
            new._method = name
            try:
                new.__doc__ = getattr(current, name).__doc__
            except Exception:
                pass
            return new
        return super().__getattribute__(name)

    @staticmethod
    def _get_ax_fn():
        @depends()
        def get_ax():
            from matplotlib.backends.backend_agg import FigureCanvas
            from matplotlib.pyplot import Figure
            interactive._fig = fig = Figure()
            FigureCanvas(fig)
            return fig.subplots()
        return get_ax

    def __call__(self, *args, **kwargs):
        """
        The `.interactive` API enhances the API of data analysis libraries
        like Pandas, Dask, and Xarray, by allowing to replace in a pipeline
        static values by dynamic widgets. When displayed, an interactive
        pipeline will incorporate the dynamic widgets that control it, as long
        as its normal output that will automatically be updated as soon as a
        widget value is changed.

        Reference: https://hvplot.holoviz.org/user_guide/interactive.html

        Parameters
        ----------
        loc : str, optional
            Widget(s) location, one of 'bottom_left', 'bottom_right', 'right'
            'top-right', 'top-left' and 'left'. By default 'top_left'
        center : bool, optional
            Whether to center to pipeline output, by default False
        max_rows : int, optional
            Maximum number of rows displayed, only used when the output is a
            dataframe, by default 100
        kwargs: optional
            Optional kwargs that are passed down to customize the displayed
            object. E.g. if the output is a DataFrame `width=200` will set
            the size of the DataFrame Pane that renders it.

        Returns
        -------
        interactive
            The next `interactive` object of the pipeline.

        Examples
        --------
        >>> widget = panel.wid7ugets.IntSlider(value=1, start=1, end=5)
        >>> dfi = df.interactive(width=200)
        >>> dfi.head(widget)
        """

        if self._method is None:
            if self._depth == 0:
                # This code path is entered when initializing an interactive
                # class from the accessor, e.g. with df.interactive(). As
                # calling the accessor df.interactive already returns an
                # interactive instance.
                return self._clone(*args, **kwargs)
            # TODO: When is this error raised?
            raise AttributeError
        elif self._method == 'plot':
            # This - {ax: get_ax} - is passed as kwargs to the plot method in
            # the dim expression.
            kwargs['ax'] = self._get_ax_fn()
        new = self._clone(copy=True)
        try:
            kwargs = dict(new._inherit_kwargs, **kwargs)
            transform = {
                'fn': new._method,
                'args': args,
                'kwargs': kwargs,
                'reverse': False
            }
            clone = new._clone(transform, plot=new._method == 'plot')
        finally:
            # If an error occurs reset _method anyway so that, e.g. the next
            # attempt in a Notebook, is set appropriately.
            new._method = None
        return clone

    def __panel__(self):
        return self.layout()

    #----------------------------------------------------------------
    # interactive pipeline APIs
    #----------------------------------------------------------------

    def __array_ufunc__(self, *args, **kwargs):
        new = self._resolve_accessor()
        transform = {
            'fn': args[0],
            'args': args[3:],
            'kwargs': kwargs,
            'reverse': False
        }
        return new._clone(transform)

    def _apply_operator(self, operator, *args, reverse=False, **kwargs):
        new = self._resolve_accessor()
        transform = {
            'fn': operator,
            'args': args,
            'kwargs': kwargs,
            'reverse': reverse
        }
        return new._clone(transform)

    # Builtin functions

    def __abs__(self):
        return self._apply_operator(abs)

    def __round__(self, ndigits=None):
        args = () if ndigits is None else (ndigits,)
        return self._apply_operator(round, *args)

    # Unary operators
    def __neg__(self):
        return self._apply_operator(operator.neg)
    def __not__(self):
        return self._apply_operator(operator.not_)
    def __invert__(self):
        return self._apply_operator(operator.inv)
    def __pos__(self):
        return self._apply_operator(operator.pos)

    # Binary operators
    def __add__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.add, other)
    def __and__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.and_, other)
    def __eq__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.eq, other)
    def __floordiv__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.floordiv, other)
    def __ge__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.ge, other)
    def __gt__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.gt, other)
    def __le__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.le, other)
    def __lt__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.lt, other)
    def __lshift__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.lshift, other)
    def __mod__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.mod, other)
    def __mul__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.mul, other)
    def __ne__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.ne, other)
    def __or__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.or_, other)
    def __rshift__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.rshift, other)
    def __pow__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.pow, other)
    def __sub__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.sub, other)
    def __truediv__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.truediv, other)

    # Reverse binary operators
    def __radd__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.add, other, reverse=True)
    def __rand__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.and_, other, reverse=True)
    def __rdiv__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.div, other, reverse=True)
    def __rfloordiv__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.floordiv, other, reverse=True)
    def __rlshift__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.rlshift, other)
    def __rmod__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.mod, other, reverse=True)
    def __rmul__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.mul, other, reverse=True)
    def __ror__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.or_, other, reverse=True)
    def __rpow__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.pow, other, reverse=True)
    def __rrshift__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.rrshift, other)
    def __rsub__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.sub, other, reverse=True)
    def __rtruediv__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.truediv, other, reverse=True)

    def __getitem__(self, other):
        other = other._transform if isinstance(other, interactive) else other
        return self._apply_operator(operator.getitem, other)

    def _plot(self, *args, **kwargs):
        # TODO: Seems totally unused to me, as self._plot is set to a boolean in __init__
        @depends()
        def get_ax():
            from matplotlib.backends.backend_agg import FigureCanvas
            from matplotlib.pyplot import Figure
            interactive._fig = fig = Figure()
            FigureCanvas(fig)
            return fig.subplots()
        kwargs['ax'] = get_ax
        new = self._resolve_accessor()
        transform = {
            'fn': 'plot',
            'args': args,
            'kwargs': kwargs,
            'reverse': False
        }
        return new._clone(transform, plot=True)

    def _eval_transform(self, obj, transform):
        fn, args, kwargs = transform['fn'], transform['args'], transform['kwargs']
        resolved_args = []
        for arg in args:
            arg = param_value_if_widget(arg)
            if isinstance(arg, interactive):
                arg = arg.eval()
            elif hasattr(arg, '_dinfo'):
                arg = eval_function(arg)
            elif isinstance(arg, param.Parameter):
                arg = getattr(arg.owner, arg.name)
            resolved_args.append(arg)
        resolved_kwargs = {}
        for k, arg in kwargs.items():
            arg = param_value_if_widget(arg)
            if isinstance(arg, interactive):
                arg = arg.eval()
            elif hasattr(arg, '_dinfo'):
                arg = eval_function(arg)
            elif isinstance(arg, param.Parameter):
                arg = getattr(arg.owner, arg.name)
            resolved_kwargs[k] = arg
        if isinstance(fn, str):
            obj = getattr(obj, fn)(*resolved_args, **resolved_kwargs)
        else:
            if transform.get('reverse'):
                obj = fn(resolved_args[0], obj, *resolved_args[1:], **resolved_kwargs)
            else:
                obj = fn(obj, *resolved_args, **resolved_kwargs)
        return obj

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def dmap(self):
        """
        Wraps the output in a DynamicMap. Only valid if the output
        is a HoloViews object.
        """
        return hv.DynamicMap(self._callback)

    def eval(self):
        """
        Returns the current state of the interactive expression. The
        returned object is no longer interactive.
        """
        if not self._dirty:
            return self._current_
        obj = self._obj if self._prev is None else self._prev.eval()
        transform = self._transform
        if transform:
            obj = self._eval_transform(obj, transform)
        self._current_ = obj
        self._dirty = False
        if self._method:
            # E.g. `pi = dfi.A` leads to `pi._method` equal to `'A'`.
            obj = getattr(obj, self._method, obj)
        if self._plot:
            obj = interactive._fig
        return obj

    def layout(self, **kwargs):
        """
        Returns a layout of the widgets and output arranged according
        to the center and widget location specified in the
        interactive call.
        """
        widget_box = self.widgets()
        panel = self.output()
        loc = self._loc
        center = self._center
        alignments = {
            'left': (Row, ('start', 'center'), True),
            'right': (Row, ('end', 'center'), False),
            'top': (Column, ('center', 'start'), True),
            'bottom': (Column, ('center', 'end'), False),
            'top_left': (Column, 'start', True),
            'top_right': (Column, ('end', 'start'), True),
            'bottom_left': (Column, ('start', 'end'), False),
            'bottom_right': (Column, 'end', False),
            'left_top': (Row, 'start', True),
            'left_bottom': (Row, ('start', 'end'), True),
            'right_top': (Row, ('end', 'start'), False),
            'right_bottom': (Row, 'end', False)
        }
        layout, align, widget_first = alignments[loc]
        widget_box.align = align
        if not len(widget_box):
            if center:
                components = [HSpacer(), panel, HSpacer()]
            else:
                components = [panel]
            return Row(*components, **kwargs)

        items = (widget_box, panel) if widget_first else (panel, widget_box)
        sizing_mode = kwargs.get('sizing_mode')
        if not center:
            if layout is Row:
                components = list(items)
            else:
                components = [layout(*items, sizing_mode=sizing_mode)]
        elif layout is Column:
            components = [HSpacer(), layout(*items, sizing_mode=sizing_mode), HSpacer()]
        elif loc.startswith('left'):
            components = [widget_box, HSpacer(), panel, HSpacer()]
        else:
            components = [HSpacer(), panel, HSpacer(), widget_box]
        return Row(*components, **kwargs)

    def holoviews(self):
        """
        Returns a HoloViews object to render the output of this
        pipeline. Only works if the output of this pipeline is a
        HoloViews object, e.g. from an .hvplot call.
        """
        return hv.DynamicMap(self._callback)

    def output(self):
        """
        Returns the output of the interactive pipeline, which is
        either a HoloViews DynamicMap or a Panel object.

        Returns
        -------
        DynamicMap or Panel object wrapping the interactive output.
        """
        return self.holoviews() if self._dmap else self.panel(**self._kwargs)

    def panel(self, **kwargs):
        """
        Wraps the output in a Panel component.
        """
        return panel(self._callback, **kwargs)

    def set(self, new):
        prev = self
        while prev is not None:
            prev._dirty = True
            if prev._prev is None:
                if prev._wrapper is None:
                    raise ValueError(
                        'Cannot set value on interactive with a function at its root.'
                    )
                else:
                    prev._wrapper.object = new
            prev = prev._prev

    def widgets(self):
        """
        Returns a Column of widgets which control the interactive output.

        Returns
        -------
        A Column of widgets
        """
        widgets = []
        for p in self._fn_params:
            if (isinstance(p.owner, Widget) and
                p.owner not in widgets):
                widgets.append(p.owner)
        prev = self
        while prev is not None:
            if prev._transform:
                for w in _find_widgets(prev._transform):
                    if w not in widgets:
                        widgets.append(w)
            prev = prev._prev
        return Column(*widgets)
