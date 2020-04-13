from __future__ import absolute_import, division, unicode_literals

import param

from .widgets import Widget

ipywidget_classes = {}


def param_value_if_widget(arg, throttled):
    if isinstance(arg, Widget):
        if throttled is True and hasattr(arg, 'value_throttled'):
            arg.value = arg.value_throttled
            return arg.param.value_throttled
        else:
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
        arg.observe(lambda event: ipy_inst.set_param(value=event['new']), 'value')
        return ipy_inst.param.value
    return arg


def depends(*args, throttled=False, **kwargs):
    updated_args = [param_value_if_widget(a, throttled) for a in args]
    updated_kwargs = {k: param_value_if_widget(v, throttled) for k, v in kwargs.items()}

    return param.depends(*updated_args, **updated_kwargs)
