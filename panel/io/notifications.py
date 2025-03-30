from __future__ import annotations

from typing import TYPE_CHECKING

import param

from bokeh.models import CustomJS

from ..config import config
from ..reactive import ReactiveHTML
from ..util import classproperty
from .datamodel import _DATA_MODELS, construct_data_model
from .document import create_doc_if_none_exists
from .resources import CDN_DIST, CSS_URLS, bundled_files
from .state import state

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class Notification(param.Parameterized):

    background = param.Color(default=None)

    duration = param.Integer(default=3000, constant=True)

    icon = param.String(default=None)

    message = param.String(default='', constant=True)

    notification_area = param.Parameter(constant=True, precedence=-1)

    notification_type = param.String(default=None, constant=True, label='type')

    _rendered = param.Boolean(default=False)

    _destroyed = param.Boolean(default=False)

    def destroy(self) -> None:
        from .notebook import push_on_root
        self._destroyed = True
        for ref in self.notification_area._models:
            push_on_root(ref)


class NotificationAreaBase(param.Parameterized):

    js_events = param.Dict(default={}, doc="""
        A dictionary that configures notifications for specific Bokeh Document
        events, e.g.:

          {'connection_lost': {'type': 'error', 'message': 'Connection Lost!', 'duration': 5}}

        will trigger a warning on the Bokeh ConnectionLost event.""")

    max_notifications = param.Integer(default=5, doc="""
        The maximum number of notifications to display at once.""")

    notifications = param.List(item_type=Notification)

    position = param.Selector(default='bottom-right', objects=[
        'bottom-right', 'bottom-left', 'bottom-center', 'top-left',
        'top-right', 'top-center', 'center-center', 'center-left',
        'center-right'])

    __abstract = True

    def clear(self):
        raise NotImplementedError

    def send(self, message, duration=3000, type=None, background=None, icon=None):
        """
        Sends a notification to the frontend.

        Parameters
        ----------
        message: str
            The message to display in the notification.
        duration: int
            The duration of the notification in milliseconds.
        type: str
            The type of the notification.
        background: str
            The background color of the notification.
        icon: str
            The icon of the notification.
        """
        raise NotImplementedError

    def error(self, message, duration=3000):
        return self.send(message, duration, type='error')

    def info(self, message, duration=3000):
        return self.send(message, duration, type='info')

    def success(self, message, duration=3000):
        return self.send(message, duration, type='success')

    def warning(self, message, duration=3000):
        return self.send(message, duration, type='warning')


class NotificationArea(NotificationAreaBase, ReactiveHTML):
    """
    A notification area that displays notifications using the Notyf library.
    """

    _clear = param.Integer(default=0)

    types = param.List(default=[
        {'type': 'warning',
         'background': '#ffc107',
         'icon': {
             'className': 'fas fa-exclamation-triangle',
             'tagName': 'i',
             'color': 'white'
         }
        },
        {'type': 'info',
         'background': '#007bff',
         'icon': {
             'className': 'fas fa-info-circle',
             'tagName': 'i',
             'color': 'white'
         }
        },
    ])

    __javascript_raw__ = [f"{config.npm_cdn}/notyf@3/notyf.min.js"]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {'Notyf': cls.__javascript__}

    __js_require__ = {
        "paths": {"notyf": __javascript_raw__[0][:-3]}
    }

    __css_raw__ = [
        f"{config.npm_cdn}/notyf@3/notyf.min.css",
        CSS_URLS['font-awesome']
    ]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    _extension_name = 'notifications'

    _notification_type = Notification

    _stylesheets = [f"{CDN_DIST}css/notifications.css"]

    _template = ""

    _scripts = {
      "render": """
        var [y, x] = data.position.split('-')
        state.toaster = new Notyf({
          dismissible: true,
          position: {x: x, y: y},
          types: data.types
        })
      """,
      "notifications": """
      for (notification of [...data.notifications]) {
          if (notification._destroyed || notification._rendered) {
            continue
          }
          var config = {
            duration: notification.duration,
            type: notification.notification_type,
            message: notification.message
          }
          if (notification.background != null) {
            config.background = notification.background;
          }
          if (notification.icon != null) {
            config.icon = notification.icon;
          }
          let toast = state.toaster.open(config);
          function destroy() {
            notification._destroyed = true;
          }
          notification._rendered = true
          toast.on('dismiss', destroy)
          if (notification.duration) {
            setTimeout(destroy, notification.duration)
          }
          if (notification.properties === undefined)
            return
          view.connect(notification.properties._destroyed.change, function () {
            state.toaster.dismiss(toast)
          })
        }
      """,
      "_clear": "state.toaster.dismissAll()",
      "position": """
        script('_clear');
        script('render');
        for (notification of data.notifications) {
          notification._rendered = false;
        }
        script('notifications');
      """
    }

    def __init__(self, **params):
        super().__init__(**params)
        self._notification_watchers = {}

    def _remove_notification(self, event):
        if event.obj in self.notifications:
            self.notifications.remove(event.obj)
        event.obj.param.unwatch(self._notification_watchers.pop(event.obj))

    def get_root(
        self, doc: Document | None = None, comm: Comm | None = None,
        preprocess: bool = True
    ) -> Model:
        doc = create_doc_if_none_exists(doc)
        root = super().get_root(doc, comm, preprocess)
        for event, notification in self.js_events.items():
            doc.js_on_event(event, CustomJS(code=f"""
            var config = {{
              message: {notification['message']!r},
              duration: {notification.get('duration', 0)},
              notification_type: {notification['type']!r},
              _destroyed: false
            }}
            notifications.data.notifications.push(config)
            notifications.data.properties.notifications.change.emit()
            """, args={'notifications': root}))
        self._documents[doc] = root
        state._views[root.ref['id']] = (self, root, doc, comm)
        return root

    @classmethod
    def demo(cls, **params):
        """
        Generates a layout which allows demoing the component.

        Parameters
        ----------
        **params: dict
            Additional parameters to pass to the component.

        Returns
        -------
        layout: Layout
            A layout containing the demo components.
        """
        from ..layout import Column
        from ..widgets import (
            Button, ColorPicker, NumberInput, Select, TextInput,
        )

        msg = TextInput(name='Message', value='This is a message', **params)
        duration = NumberInput(name='Duration', value=0, end=10000, **params)
        ntype = Select(
            name='Type', options=['info', 'warning', 'error', 'success', 'custom'],
            value='info', **params
        )
        background = ColorPicker(name='Color', value='#000000', **params)
        button = Button(name='Notify', **params)
        notifications = cls()
        button.js_on_click(
            args={
                'notifications': notifications, 'msg': msg, 'duration': duration,
                'ntype': ntype, 'color': background
            }, code="""
            var config = {
              message: msg.value,
              duration: duration.value,
              notification_type: ntype.value,
              _destroyed: false
            }
            if (ntype.value === 'custom') {
              config.background = color.color
            }
            notifications.data.notifications.push(config)
            notifications.data.properties.notifications.change.emit()
            """
        )

        return Column(msg, duration, ntype, background, button, notifications)

    def clear(self):
        self._clear += 1
        self.notifications[:] = []

    def send(self, message, duration=3000, type=None, background=None, icon=None):
        """
        Sends a notification to the frontend.

        Parameters
        ----------
        message: str
            The message to display in the notification.
        duration: int
            The duration of the notification in milliseconds.
        type: str
            The type of the notification.
        background: str
            The background color of the notification.
        icon: str
            The icon of the notification.
        """
        notification = self._notification_type(
            message=message, duration=duration, notification_type=type,
            notification_area=self, background=background, icon=icon
        )
        self._notification_watchers[notification] = (
            notification.param.watch(self._remove_notification, '_destroyed')
        )
        self.notifications.append(notification)
        self.param.trigger('notifications')
        return notification

# Construct a DataModel for Notification
_DATA_MODELS[Notification] = construct_data_model(Notification)
