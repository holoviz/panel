"""
reactive API

`reactive` is a wrapper around a Python object that lets users create
reactive pipelines by calling existing APIs on an object with dynamic
parameters or widgets.

A `reactive` instance watches what operations are applied to the object
and records these on each instance, which are then strung together
into a chain.

The original input to a `reactive` is stored in a mutable list and can be
accessed via the `_obj` property. The shared mutable data structure
ensures that all `reactive` instances created from the same object can
hold a shared reference that can be updated, e.g. via the `.set`
method or because the input was itself a reference to some object that
can potentially be updated.

When an operation is applied to an `reactive` instance, it will
record the operation and create a new instance using `_clone` method,
e.g. `dfi.head()` first records that the `'head'` attribute is
accessed, this is achieved by overriding `__getattribute__`. A new
reactive object is returned, which will then record that it is
being called, and that new object will be itself called as
`reactive` implements `__call__`. `__call__` returns another
`reactive` instance. To be able to watch all the potential
operations that may be applied to an object, `reactive` implements:

- `__getattribute__`: Watching for attribute accesses
- `__call__`: Intercepting both actual calls or method calls if an
  attribute was previously accessed
- `__getitem__`: Intercepting indexing operations
- Operators: Implementing all valid operators `__gt__`, `__add__`, etc.
- `__array_ufunc__`: Intercepting numpy universal function calls

The `reactive` object evaluates operations lazily but whenever the
current value is needed the operations are automatically
evaluated. Note that even attribute access or tab-completion
operations can result in evaluation of the pipeline. This is very
useful in Notebook sessions, as this allows to inspect the transformed
object at any point of the pipeline, and as such provide correct
auto-completion and docstrings. E.g. executing `dfi.A.max?` in an
interactive REPL or notebook where it allows returning the docstring
of the method being accessed.

The actual operations are stored as a dictionary on the `_operation`
attribute of each instance. They contain 4 keys:

- `fn`: The function to apply (either an actual function or a string
        indicating the operation is a method on the object)
- `args`: Any arguments to supply to the `fn`.
- `kwargs`: Any keyword arguments to supply to the `fn`.
- `reverse`: If the function is not a method this indicates whether
             the first arg and the input object should be supplied in
             reverse order.

The `_depth` attribute starts at 0 and is incremented by 1 every time
a new `reactive` instance is created part of a chain.  The root
instance in an expression has a `_depth` of 0. An expression can
consist of multiple chains, such as `dfi[dfi.A > 1]`, as the
`reactive` instance is referenced twice in the expression. As a
consequence `_depth` is not the total count of `reactive` instance
creations of a pipeline, it is the count of instances created in the
outer chain. In the example, that would be `dfi[]`. Each `reactive`
instance keeps a reference to the previous instance in the chain and
each instance tracks whether its current value is up-to-date via the
`_dirty` attribute which is set to False if any dependency changes.

The `_method` attribute is a string that temporarily stores the
method/attr accessed on the object, e.g. `_method` is 'head' in
`dfi.head()`, until the `reactive` instance created in the pipeline
is called at which point `_method` is reset to None. In cases such as
`dfi.head` or `dfi.A`, `_method` is not (yet) reset to None. At this
stage the reactive instance returned has its `_current` attribute
not updated, e.g. `dfi.A._current` is still the original dataframe,
not the 'A' series. Keeping `_method` is thus useful for instance to
display `dfi.A`, as the evaluation of the object will check whether
`_method` is set or not, and if it's set it will use it to compute the
object returned, e.g. the series `df.A` or the method `df.head`, and
display its repr.
"""
from __future__ import annotations

import sys

import param

from param.reactive import reactive

from .layout import Column, HSpacer, Row
from .pane import DataFrame, panel
from .util.checks import is_dataframe, is_series
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
        if hasattr(op_arg, '_dinfo'):
            dinfo = op_arg._dinfo
            args = list(dinfo.get('dependencies', []))
            kwargs = dinfo.get('kw', {})
            nested_op = {"args": args, "kwargs": kwargs}
            for widget in _find_widgets(nested_op):
                if widget not in widgets:
                    widgets.append(widget)
        elif isinstance(op_arg, slice):
            nested_op = {"args": [op_arg.start, op_arg.stop, op_arg.step], "kwargs": {}}
        elif isinstance(op_arg, (list, tuple)):
            nested_op = {"args": op_arg, "kwargs": {}}
        elif isinstance(op_arg, dict):
            nested_op = {"args": (), "kwargs": op_arg}
        elif isinstance(op_arg, reactive):
            nested_op = {"args": op_arg._params, "kwargs": {}}
        else:
            continue
        for widget in _find_widgets(nested_op):
            if widget not in widgets:
                widgets.append(widget)
    return widgets


class FigureWrapper(param.Parameterized):

    figure = param.Parameter()

    def get_ax(self):
        from matplotlib.backends.backend_agg import FigureCanvas
        from matplotlib.pyplot import Figure
        self.figure = fig = Figure()
        FigureCanvas(fig)
        return fig.subplots()

    def _repr_mimebundle_(self, include=[], exclude=[]):
        return self.layout()._repr_mimebundle_()

    def __panel__(self):
        return self.layout()


class DisplayAccessor:

    __slots__ = ["_reactive"]

    def __init__(self, reactive):
        self._reactive = reactive


class Layout(DisplayAccessor):
    """
    Renders the output and widgets of the reactive expression using
    Panel.
    """

    def __call__(self, **kwargs):
        """
        Returns a layout of the widgets and output arranged according
        to the center and widget location specified in the `reactive`
        constructor.
        """
        widget_box = self._reactive.widgets()
        panel = self._reactive.output()
        loc = self._reactive._display_opts.get('loc', 'top_left')
        center = self._reactive._display_opts.get('center', False)
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


class Panel(DisplayAccessor):
    """
    Renders the output of the reactive expression using Panel.
    """

    def __call__(self, **kwargs):
        return panel(self._reactive._callback, inplace=True, lazy=True, **kwargs)


class Output(DisplayAccessor):
    """
    Renders the output of the reactive expression using Panel.
    """

    def __call__(self, **kwargs):
        return self._reactive.panel(**kwargs)


class Widgets(DisplayAccessor):
    """
    Returns all widgets referenced by the reactive expression.
    """

    def __call__(self):
        """
        Returns a Column of widgets which control the expression output.

        Returns
        -------
        A Column of widgets
        """
        widgets = []
        for p in self._reactive._fn_params:
            if (isinstance(p.owner, Widget) and
                p.owner not in widgets):
                widgets.append(p.owner)

        operations = []
        prev = self._reactive
        while prev is not None:
            if prev._operation:
                operations.append(prev._operation)
            prev = prev._prev

        for op in operations[::-1]:
            for w in _find_widgets(op):
                if w not in widgets:
                    widgets.append(w)
        return Column(*widgets)


reactive._display_options += ('center', 'loc',)
reactive.register_accessor('layout', Layout)
reactive.register_accessor('output', Output)
reactive.register_accessor('panel', Panel)
reactive.register_accessor('widgets', Widgets)
reactive.register_display_handler(is_dataframe, handler=DataFrame, max_rows=100)
reactive.register_display_handler(is_series, handler=DataFrame, max_rows=100)

def _plot_handler(reactive):
    fig_wrapper = FigureWrapper()
    def plot(obj, *args, **kwargs):
        if 'ax' not in kwargs:
            kwargs['ax'] = fig_wrapper.get_ax()
        obj.plot(*args, **kwargs)
        return fig_wrapper.figure
    return plot

reactive.register_method_handler('plot', _plot_handler)
