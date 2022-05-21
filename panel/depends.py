import param

from param.parameterized import iscoroutinefunction

from .widgets import Widget

ipywidget_classes = {}


def param_value_if_widget(arg):
    if isinstance(arg, Widget):
        return arg.param.value

    from .pane.ipywidget import IPyWidget
    if IPyWidget.applies(arg) and hasattr(arg, 'value'):
        name = type(arg).__name__
        if name in ipywidget_classes:
            ipy_param = ipywidget_classes[name]
        else:
            ipy_param = param.parameterized_class(name, {'value': param.Parameter()})
        ipywidget_classes[name] = ipy_param
        ipy_inst = ipy_param(value=arg.value)
        arg.observe(lambda event: ipy_inst.param.update(value=event['new']), 'value')
        return ipy_inst.param.value
    return arg


def depends(*args, **kwargs):
    """
    Python decorator annotating a function or `Parameterized` method to
    express its dependencies on a set of Parameters.

    Returns a "reactive" function that binds (some of) its arguments to
    Parameter values. This means that the "reactive" function can
    (or will if `watch=True`) be automatically invoked whenever the underlying
    parameter values change.

    See also `pn.bind`.

    Reference: https://panel.holoviz.org/user_guide/APIs.html#reactive-functions

    :Example:

    >>> widget = pn.widgets.IntSlider(value=1, start=1, end=5)
    >>> @pn.depends(a=widget)
    ... def add(a,b=1):
    ...     return a+b
    >>> pn.Column(widget, add)

    This function is the same as the corresponding `param.depends`
    decorator, but extended so that if widgets are provided as
    dependencies, the underlying `value` Parameter of the widget is
    extracted as the actual dependency.

    This extension is solely for syntactic convenience, allowing the widget to
    be passed in as a synonym for the underlying parameter. Apart from that
    extension, this decorator otherwise behaves the same as the underlying
    Param depends decorator.

    For the Panel version of the decorator, the specified dependencies
    can either be Parameter instances, Panel or ipywidgets widgets,
    or, if a Parameterized method is supplied rather than a function,
    they can be defined either as string names of Parameters of this
    object or as Parameter objects of this object's subobjects (i.e.,
    Parameterized objects that are values of this object's
    Parameters). See the docs for the corresponding param.depends
    decorator for further details.
    """
    updated_args = [param_value_if_widget(a) for a in  args]
    updated_kwargs = {k: param_value_if_widget(v) for k, v in kwargs.items()}
    return param.depends(*updated_args, **updated_kwargs)


def bind(function, *args, watch=False, **kwargs):
    """
    Returns a "reactive" function that binds (some of) its arguments to
    Parameter values. This means that the "reactive" function can
    (or will if `watch=True`) be automatically invoked whenever the underlying
    parameter values change.

    Reference: https://panel.holoviz.org/user_guide/APIs.html#reactive-functions

    :Example:

    >>> def add(a,b):
    ...     return a+b
    >>> widget = pn.widgets.IntSlider(value=1, start=1, end=5)
    >>> iadd = pn.bind(add, a=widget, b=1)
    >>> pn.Column(widget, iadd)

    This function is the same as `param.bind`, but extended so that if
    widgets are provided as values, the underlying `value` Parameter
    of the widget is extracted as the actual argument value and
    dependency. This extension is solely for syntactic convenience,
    allowing the widget to be passed in as a synonym for the
    underlying parameter. Apart from that extension, this function
    otherwise behaves the same as the corresponding Param function.

    This function allows dynamically recomputing the output of the
    provided function whenever one of the bound parameters
    changes. For Panel, the parameters are typically values of
    widgets, making it simple to have output that reacts to changes in
    the widgets. Arguments an also be bound to other parameters (not
    part of widgets) or even to constants.

    Arguments
    ---------
    function: callable
        The function to bind constant or dynamic args and kwargs to.
    args: object, param.Parameter, panel.widget.Widget, or ipywidget
        Positional arguments to bind to the function.
    watch: boolean
        Whether to evaluate the function automatically whenever one of
        the bound parameters changes.
    kwargs: object, param.Parameter, panel.widget.Widget, or ipywidget
        Keyword arguments to bind to the function.

    Returns
    -------
    Returns a new function with the args and kwargs bound to it and
    annotated with all dependencies.
    """
    updated_args = [param_value_if_widget(a) for a in args]
    updated_kwargs = {k: param_value_if_widget(v) for k, v in kwargs.items()}
    return _param_bind(function, *updated_args, watch=watch, **updated_kwargs)


# Temporary; to move to Param
def _param_bind(function, *args, watch=False, **kwargs):
    """
    Given a function, returns a wrapper function that binds the values
    of some or all arguments to Parameter values and expresses Param
    dependencies on those values, so that the function can be invoked
    whenever the underlying values change and the output will reflect
    those updated values.

    As for functools.partial, arguments can also be bound to constants,
    which allows all of the arguments to be bound, leaving a simple
    callable object.

    Arguments
    ---------
    function: callable
        The function to bind constant or dynamic args and kwargs to.
    args: object, param.Parameter
        Positional arguments to bind to the function.
    watch: boolean
        Whether to evaluate the function automatically whenever one of
        the bound parameters changes.
    kwargs: object, param.Parameter
        Keyword arguments to bind to the function.

    Returns
    -------
    Returns a new function with the args and kwargs bound to it and
    annotated with all dependencies.
    """
    dependencies = {}
    for i, arg in enumerate(args):
        p = param_value_if_widget(arg)
        if hasattr(p, '_dinfo'):
            for j, arg in enumerate(p._dinfo['dependencies']):
                dependencies[f'__arg{i}_arg{j}'] = arg
            for kw, kwarg in p._dinfo['kw'].items():
                dependencies[f'__arg{i}_arg_{kw}'] = kwarg
        elif isinstance(p, param.Parameter):
            dependencies[f'__arg{i}'] = p
    for kw, v in kwargs.items():
        p = param_value_if_widget(v)
        if hasattr(p, '_dinfo'):
            for j, arg in enumerate(p._dinfo['dependencies']):
                dependencies[f'__kwarg_{kw}_arg{j}'] = arg
            for pkw, kwarg in p._dinfo['kw'].items():
                dependencies[f'__kwarg_{kw}_{pkw}'] = kwarg
        elif isinstance(p, param.Parameter):
            dependencies[kw] = p

    def combine_arguments(wargs, wkwargs):
        combined_args = []
        for arg in args:
            if hasattr(arg, '_dinfo'):
                arg = arg()
            elif isinstance(arg, param.Parameter):
                arg = getattr(arg.owner, arg.name)
            combined_args.append(arg)
        combined_args += list(wargs)
        combined_kwargs = {}
        for kw, arg in kwargs.items():
            if hasattr(arg, '_dinfo'):
                arg = arg()
            elif isinstance(arg, param.Parameter):
                arg = getattr(arg.owner, arg.name)
            combined_kwargs[kw] = arg
        for kw, arg in wkwargs.items():
            if kw.startswith('__arg') or kw.startswith('__kwarg'):
                continue
            combined_kwargs[kw] = arg
        return combined_args, combined_kwargs

    if iscoroutinefunction(function):
        @depends(**dependencies, watch=watch)
        async def wrapped(*wargs, **wkwargs):
            combined_args, combined_kwargs = combine_arguments(wargs, wkwargs)
            return await function(*combined_args, **combined_kwargs)
    else:
        @depends(**dependencies, watch=watch)
        def wrapped(*wargs, **wkwargs):
            combined_args, combined_kwargs = combine_arguments(wargs, wkwargs)
            return function(*combined_args, **combined_kwargs)
    wrapped.__bound_function__ = function
    return wrapped

__all__ = ["bind", "depends"]
