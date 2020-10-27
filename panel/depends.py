from __future__ import absolute_import, division, unicode_literals

import param

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
        arg.observe(lambda event: ipy_inst.param.set_param(value=event['new']), 'value')
        return ipy_inst.param.value
    return arg


def depends(*args, **kwargs):
    """
    Annotates a function or Parameterized method to express its
    dependencies on a set of parameters. This allows libraries
    such as Panel to watch those dependencies for changes and update
    the output of the annotated function when one of the dependencies
    changes.

    The specified dependencies can be either be Parameter instances,
    widgets, or, if a method is supplied, they can be defined
    as strings referring to Parameters of the class, or Parameters of
    subobjects (Parameterized objects that are values of this object's
    parameters).
    """
    updated_args = [param_value_if_widget(a) for a in  args]
    updated_kwargs = {k: param_value_if_widget(v) for k, v in kwargs.items()}
    return param.depends(*updated_args, **updated_kwargs)


def bind(function, *args, **kwargs):
    """
    The bind function allows binding dynamic widget parameters to a
    function, such that when it is evaluated it will automatically
    reflect the current value of those parameters, e.g. when binding
    a Panel widget to a function the current widget value will be
    bound to the function. Constant values can also be bound to a
    function just like using functools.partial. In addition to binding
    the parameters to the function the returned function is also
    annotated with the parameter dependencies allowing libraries
    such as Panel to watch those dependencies for changes and update
    the output of the annotated function when one of the dependencies
    changes.

    Arguments
    ---------
    function: The function to bind constant or dynamic args and kwargs to.
    args: The arguments to bind to the function.
    kwargs: The keyword arguments to bind to the function.

    Returns
    -------
    Returns a new function with the args and kwargs bound to it and
    annotated with all dependencies.
    """
    updated_args = [param_value_if_widget(a) for a in args]
    updated_kwargs = {k: param_value_if_widget(v) for k, v in kwargs.items()}

    dependencies = {}
    for i, arg in enumerate(updated_args):
        p = param_value_if_widget(arg)
        if isinstance(p, param.Parameter):
            dependencies[f'__arg{i}'] = p
    for kw, v in updated_kwargs.items():
        p = param_value_if_widget(v)
        if isinstance(p, param.Parameter):
            dependencies[kw] = p

    @depends(**dependencies)
    def wrapped(*args, **kwargs):
        combined_args = []
        for arg in updated_args:
            if isinstance(arg, param.Parameter):
                combined_args.append(getattr(arg.owner, arg.name))
            else:
                combined_args.append(arg)
        combined_args += list(args)
        combined_kwargs = {}
        for kw, arg in updated_kwargs.items():
            if kw.startswith('__arg'):
                continue
            elif isinstance(arg, param.Parameter):
                arg = getattr(arg.owner, arg.name)
            combined_kwargs[kw] = arg
        combined_kwargs.update(kwargs)
        return function(*combined_args, **combined_kwargs)
    return wrapped
