from __future__ import absolute_import, division, unicode_literals

import param

from .widgets import Widget

def param_value_if_widget(arg):
    if isinstance(arg, Widget):
        return arg.param.value
    return arg

def depends(*args, **kwargs):
    updated_args = [param_value_if_widget(a) for a in  args]
    updated_kwargs = {k: param_value_if_widget(v) for k, v in kwargs.items()}

    return param.depends(*updated_args, **updated_kwargs)
