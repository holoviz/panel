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
    updated_args = [param_value_if_widget(a) for a in  args]
    updated_kwargs = {k: param_value_if_widget(v) for k, v in kwargs.items()}

    return param.depends(*updated_args, **updated_kwargs)
