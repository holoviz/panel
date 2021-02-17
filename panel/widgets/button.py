"""
Defines Button and button-like widgets which allow triggering events
or merely toggling between on-off states.
"""
from functools import partial

import param

from bokeh.models import (
    Button as _BkButton, Toggle as _BkToggle, Dropdown as _BkDropdown
)

from bokeh.events import (MenuItemClick, ButtonClick)

from .base import Widget


BUTTON_TYPES = ['default', 'primary', 'success', 'warning', 'danger']

class _ButtonBase(Widget):

    button_type = param.ObjectSelector(default='default', objects=BUTTON_TYPES)

    _rename = {'name': 'label'}

    __abstract = True


class _ClickButton(_ButtonBase):

    __abstract = True

    _event = 'button_click'

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = super()._get_model(doc, root, parent, comm)
        ref = (root or model).ref['id']
        model.on_click(partial(self._server_click, doc, ref))
        return model

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
        return Callback(self, code={'event:'+self._event: code}, args=args)

    def jscallback(self, args={}, **callbacks):
        """
        Allows defining a JS callback to be triggered when a property
        changes on the source object. The keyword arguments define the
        properties that trigger a callback and the JS code that gets
        executed.

        Arguments
        ----------
        args: dict
          A mapping of objects to make available to the JS callback
        **callbacks: dict
          A mapping between properties on the source model and the code
          to execute when that property changes

        Returns
        -------
        callback: Callback
          The Callback which can be used to disable the callback.
        """
        from ..links import Callback
        for k, v in list(callbacks.items()):
            if k == 'clicks':
                k = 'event:'+self._event
            callbacks[k] = self._rename.get(v, v)
        return Callback(self, code=callbacks, args=args)


class Button(_ClickButton):

    clicks = param.Integer(default=0)

    value = param.Event()

    _rename = {'clicks': None, 'name': 'label', 'value': None}

    _widget_type = _BkButton

    def _server_click(self, doc, ref, event):
        processing = bool(self._events)
        self._events.update({"clicks": self.clicks+1})
        self.param.trigger('value')
        if not processing:
            if doc.session_context:
                doc.add_timeout_callback(partial(self._change_coroutine, doc), self._debounce)
            else:
                self._change_event(doc)

    def _process_property_change(self, msg):
        msg = super()._process_property_change(msg)
        if 'clicks' in msg:
            msg['clicks'] = self.clicks + 1
        return msg

    def on_click(self, callback):
        self.param.watch(callback, 'clicks', onlychanged=False)


class Toggle(_ButtonBase):

    value = param.Boolean(default=False, doc="""
        Whether the button is currently toggled.""")

    _rename = {'value': 'active', 'name': 'label'}

    _supports_embed = True

    _widget_type = _BkToggle

    def _get_embed_state(self, root, values=None, max_opts=3):
        return (self, self._models[root.ref['id']][0], [False, True],
                lambda x: x.active, 'active', 'cb_obj.active')


class MenuButton(_ClickButton):

    clicked = param.String(default=None, doc="""
      Last menu item that was clicked.""")

    items = param.List(default=[], doc="""
      Menu items in the dropdown. Allows strings, tuples of the form
      (title, value) or Nones to separate groups of items.""")

    split = param.Boolean(default=False, doc="""
      Whether to add separate dropdown area to button.""")

    _widget_type = _BkDropdown

    _rename = {'name': 'label', 'items': 'menu', 'clicked': None}

    _event = 'menu_item_click'

    def on_click(self, callback):
        self.param.watch(callback, 'clicked', onlychanged=False)

    def _server_click(self, doc, ref, event):
        processing = bool(self._events)
        if isinstance(event, MenuItemClick):
            self._events.update({"clicked": event.item})
        elif isinstance(event, ButtonClick):
            self._events.update({"clicked": self.name})
        if not processing:
            if doc.session_context:
                doc.add_timeout_callback(partial(self._change_coroutine, doc), self._debounce)
            else:
                self._change_event(doc)
