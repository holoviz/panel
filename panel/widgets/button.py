"""
Defines Button and button-like widgets which allow triggering events
or merely toggling between on-off states.
"""
from __future__ import absolute_import, division, unicode_literals

import param

from bokeh.models import Button as _BkButton, Toggle as _BkToggle

from .base import Widget


class _ButtonBase(Widget):

    button_type = param.ObjectSelector(default='default', objects=[
        'default', 'primary', 'success', 'warning', 'danger'])

    _rename = {'name': 'label'}

    __abstract = True


class Button(_ButtonBase):

    clicks = param.Integer(default=0)

    _widget_type = _BkButton

    def on_click(self, callback):
        self.param.watch(callback, 'clicks')

    def js_on_click(self, args={}, code=""):
        """
        Allows defining a JS callback to be triggered when the button
        is clicked.

        Arguments
        ----------
        args: dict
          A mapping of objects to make available to the JS callback
        code: str
          The Javascript code to execute when the button is clicked.

        Returns
        -------
        callback: Callback
          The Callback which can be used to disable the callback.
        """
        from ..links import Callback
        return Callback(self, code={'clicks': code}, args=args)



class Toggle(_ButtonBase):

    value = param.Boolean(default=False, doc="""
        Whether the button is currently toggled.""")

    _rename = {'value': 'active', 'name': 'label'}

    _supports_embed = True

    _widget_type = _BkToggle

    def _get_embed_state(self, root, max_opts=3):
        return (self, self._models[root.ref['id']][0], [False, True],
                lambda x: x.active, 'active', 'cb_obj.active')
