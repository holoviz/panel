"""
Bootstrap template based on the bootstrap.css library.
"""
import pathlib

import param

from ...io.notifications import Notification, NotificationArea
from ...layout import Card
from ...reactive import ReactiveHTML
from ..base import BasicTemplate
from ..theme import DarkTheme, DefaultTheme


class BootstrapNotification(Notification, ReactiveHTML):

    _template = """
    <div id="toast" class="toast">
      <div class="toast-header">
      ${header}
      <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
        <span aria-hidden="true">×</span>
      </button>
      </div>
      <div class="toast-body">
      ${body}
      </div>
    </div>
    """

    _scripts = {
        'render': """
      $(toast).toast({autohide: data.autohide, delay: data.duration})
      $(toast).toast("show")
      $(toast).on("hidden.bs.toast", function () {
        data._destroyed = true;
      })
    """,
        '_destroyed': """
      $(toast).toast("dispose")
    """}


class BootstrapNotificationArea(NotificationArea):

    _notification_type = BootstrapNotification


class BootstrapTemplate(BasicTemplate):
    """
    BootstrapTemplate
    """

    notifications = param.ClassSelector(default=BootstrapNotificationArea(),
                                        class_=NotificationArea)

    sidebar_width = param.Integer(350, doc="""
        The width of the sidebar in pixels. Default is 350.""")

    _css = pathlib.Path(__file__).parent / 'bootstrap.css'

    _template = pathlib.Path(__file__).parent / 'bootstrap.html'

    _modifiers = {
        Card: {
            'children': {'margin': (10, 10)},
            'button_css_classes': ['card-button'],
            'margin': (10, 5)
        },
    }

    _resources = {
        'css': {
            'bootstrap': "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
        },
        'js': {
            'jquery': "https://code.jquery.com/jquery-3.5.1.slim.min.js",
            'bootstrap': "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"
        }
    }


class BootstrapDefaultTheme(DefaultTheme):

    _template = BootstrapTemplate


class BootstrapDarkTheme(DarkTheme):

    css = param.Filename(default=pathlib.Path(__file__).parent / 'dark.css')

    _template = BootstrapTemplate
