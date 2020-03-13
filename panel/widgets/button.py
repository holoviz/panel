"""
Defines Button and button-like widgets which allow triggering events
or merely toggling between on-off states.
"""
from __future__ import absolute_import, division, unicode_literals

from functools import partial

import param

from bokeh.models import Button as _BkButton, Toggle as _BkToggle

from ..config import config
from ..io.notebook import get_comm_customjs
from ..io.state import state
from .base import Widget


class _ButtonBase(Widget):

    button_type = param.ObjectSelector(default='default', objects=[
        'default', 'primary', 'success', 'warning', 'danger'])

    _rename = {'name': 'label'}

    __abstract = True


class Button(_ButtonBase):

    clicks = param.Integer(default=0)

    _rename = {'clicks': None, 'name': 'label'}

    _widget_type = _BkButton

    def _link_clicks(self, model, doc, root, comm=None):
        ref = root.ref['id']
        if comm is None:
            model.on_click(partial(self._server_click, doc, ref))
        elif config.embed:
            pass
        else:
            on_msg = partial(self._comm_change, ref=ref)
            client_comm = state._comm_manager.get_client_comm(
                on_msg=on_msg, on_error=partial(self._on_error, ref),
                on_stdout=partial(self._on_stdout, ref)
            )
            customjs = get_comm_customjs(
                'clicks', client_comm, ref, "value = 1;",
                self._timeout, self._debounce
            )
            model.js_on_click(customjs)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = super(Button, self)._get_model(doc, root, parent, comm)
        self._link_clicks(model, doc, root or model, comm)
        return model

    def _server_click(self, doc, ref, event):
        self._events.update({"clicks": 1})
        if not self._processing:
            self._processing = True
            if doc.session_context:
                doc.add_timeout_callback(partial(self._change_event, doc), self._debounce)
            else:
                self._change_event(doc)

    def _process_property_change(self, msg):
        msg = super(Button, self)._process_property_change(msg)
        if 'clicks' in msg:
            msg['clicks'] = self.clicks + 1
        return msg

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
        return Callback(self, code={'event:button_click': code}, args=args)



class Toggle(_ButtonBase):

    value = param.Boolean(default=False, doc="""
        Whether the button is currently toggled.""")

    _rename = {'value': 'active', 'name': 'label'}

    _supports_embed = True

    _widget_type = _BkToggle

    def _get_embed_state(self, root, max_opts=3):
        return (self, self._models[root.ref['id']][0], [False, True],
                lambda x: x.active, 'active', 'cb_obj.active')
