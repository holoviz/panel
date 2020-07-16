import param

from ..models import HTML
from .base import Widget


class Indicator(Widget):
    """
    Indicator is a baseclass for widgets which indicate some state.
    """

    sizing_mode = param.ObjectSelector(default='fixed', objects=[
        'fixed', 'stretch_width', 'stretch_height', 'stretch_both',
        'scale_width', 'scale_height', 'scale_both', None])

    __abstract = True


class Busy(Indicator):

    height = param.Integer(default=20, doc="""
        height of the circle.""")

    width = param.Integer(default=20, doc="""
        Width of the circle.""")

    value = param.Boolean(default=False, doc="""
        Whether the indicator is active or not.""")

    _widget_type = HTML

    def _process_param_change(self, msg):
        value = msg.pop('value', None)
        if value is None:
            return msg
        msg['css_classes'] = ['dot-filled'] if value else ['dot']
        return msg


class Spinner(Indicator):

    height = param.Integer(default=125, doc="""
        height of the circle.""")

    width = param.Integer(default=125, doc="""
        Width of the circle.""")

    value = param.Boolean(default=False, doc="""
        Whether the indicator is active or not.""")

    _widget_type = HTML

    def _process_param_change(self, msg):
        value = msg.pop('value', None)
        if value is None:
            return msg
        msg['css_classes'] = ['loader', 'spin'] if value else ['loader']
        return msg
