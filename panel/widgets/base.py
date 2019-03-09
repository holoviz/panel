"""
Defines the Widget base class which provides bi-directional
communication between the rendered dashboard and the Widget
parameters.
"""
from __future__ import absolute_import, division, unicode_literals

import param

from ..viewable import Reactive


class Widget(Reactive):
    """
    Widgets allow syncing changes in bokeh widget models with the
    parameters on the Widget instance.
    """

    disabled = param.Boolean(default=False, doc="""
       Whether the widget is disabled.""")

    name = param.String(default='')

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    __abstract = True

    _widget_type = None

    _rename = {'name': 'title'}

    def __init__(self, **params):
        if 'name' not in params:
            params['name'] = ''
        super(Widget, self).__init__(**params)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = self._widget_type(**self._process_param_change(self._init_properties()))
        if root is None:
            root = model
        # Link parameters and bokeh model
        values = dict(self.get_param_values())
        properties = list(self._process_param_change(values))
        self._models[root.ref['id']] = (model, parent)
        self._link_props(model, properties, doc, root, comm)
        return model
