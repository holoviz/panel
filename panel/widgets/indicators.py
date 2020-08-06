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


class BooleanIndicator(Indicator):

    value = param.Boolean(default=False, doc="""
        Whether the indicator is active or not.""")

    __abstract = True


class BooleanStatus(BooleanIndicator):

    color = param.ObjectSelector(default='dark', objects=[
        'primary', 'secondary', 'success', 'info', 'danger', 'warning',
        'light', 'dark'])

    height = param.Integer(default=20, doc="""
        height of the circle.""")

    width = param.Integer(default=20, doc="""
        Width of the circle.""")

    value = param.Boolean(default=False, doc="""
        Whether the indicator is active or not.""")

    _widget_type = HTML

    _rename = {'color': None}

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        value = msg.pop('value', None)
        if value is None:
            return msg
        msg['css_classes'] = ['dot-filled', self.color] if value else ['dot']
        return msg


class LoadingSpinner(BooleanIndicator):

    bgcolor = param.ObjectSelector(default='light', objects=['dark', 'light'])

    color = param.ObjectSelector(default='dark', objects=[
        'primary', 'secondary', 'success', 'info', 'danger', 'warning',
        'light', 'dark'])

    height = param.Integer(default=125, doc="""
        height of the circle.""")

    width = param.Integer(default=125, doc="""
        Width of the circle.""")

    value = param.Boolean(default=False, doc="""
        Whether the indicator is active or not.""")

    _widget_type = HTML

    _rename = {'color': None, 'bgcolor': None}

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        value = msg.pop('value', None)
        if value is None:
            return msg
        color_cls = f'{self.color}-{self.bgcolor}'
        msg['css_classes'] = ['loader', 'spin', color_cls] if value else ['loader', self.bgcolor]
        return msg
