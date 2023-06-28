from inspect import isasyncgenfunction

import param

from packaging.version import Version
from param.parameterized import iscoroutinefunction

from .config import __version__
from .util import eval_function
from .util.warnings import deprecated

_dependency_transforms = []

def register_depends_transform(transform):
    """
    Appends a transform to extract potential parameter dependencies
    from an object.

    Arguments
    ---------
    transform: Callable[Any, Any]
    """
    return _dependency_transforms.append(transform)

def transform_dependency(arg):
    """
    Transforms arguments for depends and bind functions applying any
    registered transform. This makes it possible to depend on objects
    other than simple Parameters or functions with dependency
    definitions.
    """
    for transform in _dependency_transforms:
        if isinstance(arg, param.Parameter) or hasattr(arg, '_dinfo'):
            break
        arg = transform(arg)
    return arg

# Alias for backward compatibility
def param_value_if_widget(*args, **kwargs):
    if Version(Version(__version__).base_version) > '1.2':
        deprecated("1.4", "param_value_if_widget", "transform_dependency")
    return transform_dependency(*args, **kwargs)

def depends(*args, **kwargs):
    """
    Python decorator annotating a function or `Parameterized` method to
    express its dependencies on a set of Parameters.

    Despite still being available, usage of `pn.depends` is no longer
    recommended, in favor of the less intrusive `pn.bind`.

    Returns a "reactive" function that binds (some of) its arguments to
    Parameter values. This means that the "reactive" function can
    (or will if `watch=True`) be automatically invoked whenever the underlying
    parameter values change.

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
    updated_args = [transform_dependency(a) for a in  args]
    updated_kwargs = {k: transform_dependency(v) for k, v in kwargs.items()}
    return param.depends(*updated_args, **updated_kwargs)


def bind(function, *args, watch=False, **kwargs):
    """
    Returns a "reactive" function that binds (some of) its arguments to
    Parameter values. This means that the "reactive" function can
    (or will if `watch=True`) be automatically invoked whenever the underlying
    parameter values change.

    How-to: https://panel.holoviz.org/how_to/interactivity/bind_function.html

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
    updated_args = [transform_dependency(a) for a in args]
    updated_kwargs = {k: transform_dependency(v) for k, v in kwargs.items()}
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
    fn_deps = transform_dependency(function)
    if isinstance(fn_deps, param.Parameter) or hasattr(fn_deps, '_dinfo'):
        dependencies['__fn'] = fn_deps
    for i, p in enumerate(args):
        if hasattr(p, '_dinfo'):
            for j, arg in enumerate(p._dinfo['dependencies']):
                dependencies[f'__arg{i}_arg{j}'] = arg
            for kw, kwarg in p._dinfo['kw'].items():
                dependencies[f'__arg{i}_arg_{kw}'] = kwarg
        elif isinstance(p, param.Parameter):
            dependencies[f'__arg{i}'] = p
    for kw, v in kwargs.items():
        if hasattr(v, '_dinfo'):
            for j, arg in enumerate(v._dinfo['dependencies']):
                dependencies[f'__kwarg_{kw}_arg{j}'] = arg
            for pkw, kwarg in v._dinfo['kw'].items():
                dependencies[f'__kwarg_{kw}_{pkw}'] = kwarg
        elif isinstance(v, param.Parameter):
            dependencies[kw] = v

    def combine_arguments(wargs, wkwargs, asynchronous=False):
        combined_args = []
        for arg in args:
            if hasattr(arg, '_dinfo'):
                arg = eval_function(arg)
            elif isinstance(arg, param.Parameter):
                arg = getattr(arg.owner, arg.name)
            combined_args.append(arg)
        combined_args += list(wargs)
        combined_kwargs = {}
        for kw, arg in kwargs.items():
            if hasattr(arg, '_dinfo'):
                arg = eval_function(arg)
            elif isinstance(arg, param.Parameter):
                arg = getattr(arg.owner, arg.name)
            combined_kwargs[kw] = arg
        for kw, arg in wkwargs.items():
            if asynchronous:
                if kw.startswith('__arg'):
                    combined_args[int(kw[5:])] = arg
                elif kw.startswith('__kwarg'):
                    combined_kwargs[kw[8:]] = arg
                continue
            elif kw.startswith('__arg') or kw.startswith('__kwarg') or kw.startswith('__fn'):
                continue
            combined_kwargs[kw] = arg
        return combined_args, combined_kwargs

    def eval_fn():
        if callable(function):
            fn = function
        else:
            p = transform_dependency(function)
            if isinstance(p, param.Parameter):
                fn = getattr(p.owner, p.name)
            else:
                fn = eval_function(p)
        return fn

    if isasyncgenfunction(function):
        async def wrapped(*wargs, **wkwargs):
            combined_args, combined_kwargs = combine_arguments(
                wargs, wkwargs, asynchronous=True
            )
            evaled = eval_fn()(*combined_args, **combined_kwargs)
            async for val in evaled:
                yield val
        wrapper_fn = depends(**dependencies, watch=watch)(wrapped)
        wrapped._dinfo = wrapper_fn._dinfo
    elif iscoroutinefunction(function):
        @depends(**dependencies, watch=watch)
        async def wrapped(*wargs, **wkwargs):
            combined_args, combined_kwargs = combine_arguments(
                wargs, wkwargs, asynchronous=True
            )
            evaled = eval_fn()(*combined_args, **combined_kwargs)
            return await evaled
    else:
        @depends(**dependencies, watch=watch)
        def wrapped(*wargs, **wkwargs):
            combined_args, combined_kwargs = combine_arguments(wargs, wkwargs)
            return eval_fn()(*combined_args, **combined_kwargs)
    wrapped.__bound_function__ = function
    return wrapped

__all__ = ["bind", "depends"]
