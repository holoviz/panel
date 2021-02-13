"""
Spacer components to add horizontal or vertical space to a layout. 
"""

import param

from bokeh.models import Div as BkDiv, Spacer as BkSpacer

from ..reactive import Reactive


class Spacer(Reactive):
    """Empty object used to control formatting (using positive or negative space)"""

    _bokeh_model = BkSpacer

    def _get_model(self, doc, root=None, parent=None, comm=None):
        properties = self._process_param_change(self._init_params())
        model = self._bokeh_model(**properties)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model


class VSpacer(Spacer):
    """
    Spacer which automatically fills all available vertical space.
    """

    sizing_mode = param.Parameter(default='stretch_height', readonly=True)


class HSpacer(Spacer):
    """
    Spacer which automatically fills all available horizontal space.
    """

    sizing_mode = param.Parameter(default='stretch_width', readonly=True)


class Divider(Reactive):
    """A Divider line"""

    width_policy = param.ObjectSelector(default="fit", readonly=True)

    _bokeh_model = BkDiv

    def _get_model(self, doc, root=None, parent=None, comm=None):
        properties = self._process_param_change(self._init_params())
        properties['style'] = {'width': '100%', 'height': '100%'}
        model = self._bokeh_model(text='<hr style="margin: 0px">', **properties)
        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model
