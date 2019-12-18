"""
Defines Button and button-like widgets which allow triggering events
or merely toggling between on-off states.
"""
from __future__ import absolute_import, division, unicode_literals

import param

from bokeh.models import Button as _BkButton, Toggle as _BkToggle

from ..models import FontAwesomeIcon
from .base import Widget


class _ButtonBase(Widget):

    button_type = param.ObjectSelector(default='default', objects=[
        'default', 'primary', 'success', 'warning', 'danger'])

    icon = param.String(default=None, doc="""
        A FontAwesome icon specification.""")

    _rename = {'name': 'label'}

    __abstract = True

    def _process_param_change(self, msg):
        if msg.get('icon') is not None:
            icon = msg['icon']
            css_classes = [] if self.name else ['only-icon']
            if icon.startswith('fa-'):
                msg['icon'] = FontAwesomeIcon(icon=icon, css_classes=css_classes)
            else:
                raise ValueError('Icon is not a valid fontawesome icon.')
        if 'name' in msg and not msg['name']:
            msg['name'] = ' '
        return super(_ButtonBase, self)._process_param_change(msg)


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
