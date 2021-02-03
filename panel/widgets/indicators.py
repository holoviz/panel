import sys

from math import pi

import numpy as np
import param

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

from ..models import HTML, Progress as _BkProgress
from ..util import escape
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


class ValueIndicator(Indicator):
    """
    A ValueIndicator provides a visual representation for a numeric
    value.
    """

    value = param.Number(default=None, allow_None=True)

    __abstract = True


class Progress(ValueIndicator):

    active = param.Boolean(default=True, doc="""
        If no value is set the active property toggles animation of the
        progress bar on and off.""")

    bar_color = param.ObjectSelector(default='success', objects=[
        'primary', 'secondary', 'success', 'info', 'danger', 'warning',
        'light', 'dark'])

    max = param.Integer(default=100, doc="The maximum value of the progress bar.")

    value = param.Integer(default=None, bounds=(0, None), doc="""
        The current value of the progress bar. If set to None the progress
        bar will be indeterminate and animate depending on the active
        parameter.""")

    _rename = {'name': None}

    _widget_type = _BkProgress

    @param.depends('max', watch=True)
    def _update_value_bounds(self):
        self.param.value.bounds = (0, self.max)
               
    def __init__(self,**params):
        super().__init__(**params)
        self._update_value_bounds()


class Number(ValueIndicator):
    """
    The Number indicator renders the value as text optionally colored
    according to the color thresholds.
    """

    default_color = param.String(default='black')

    colors = param.List(default=None)

    format = param.String(default='{value}')

    font_size = param.String(default='54pt')

    nan_format = param.String(default='-', doc="""
      How to format nan values.""")

    title_size = param.String(default='18pt')

    _rename = {}

    _widget_type = HTML

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        font_size = msg.pop('font_size', self.font_size)
        title_font_size = msg.pop('title_size', self.title_size)
        name = msg.pop('name', self.name)
        format = msg.pop('format', self.format)
        value = msg.pop('value', self.value)
        nan_format = msg.pop('nan_format', self.nan_format)
        color = msg.pop('default_color', self.default_color)
        colors = msg.pop('colors', self.colors)
        for val, clr in (colors or [])[::-1]:
            if value is not None and value <= val:
                color = clr
        if value is None:
            value = float('nan')
        value = format.format(value=value).replace('nan', nan_format)
        text = f'<div style="font-size: {font_size}; color: {color}">{value}</div>'
        if self.name:
            title_font_size = msg.pop('title_size', self.title_size)
            text = f'<div style="font-size: {title_font_size}; color: {color}">{name}</div>\n{text}'
        msg['text'] = escape(text)
        return msg


class String(ValueIndicator):
    """
    The String indicator renders a string with a title.
    """

    default_color = param.String(default='black')

    font_size = param.String(default='54pt')

    title_size = param.String(default='18pt')

    value = param.String(default=None, allow_None=True)

    _rename = {}

    _widget_type = HTML

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        font_size = msg.pop('font_size', self.font_size)
        title_font_size = msg.pop('title_size', self.title_size)
        name = msg.pop('name', self.name)
        value = msg.pop('value', self.value)
        color = msg.pop('default_color', self.default_color)
        text = f'<div style="font-size: {font_size}; color: {color}">{value}</div>'
        if self.name:
            title_font_size = msg.pop('title_size', self.title_size)
            text = f'<div style="font-size: {title_font_size}; color: {color}">{name}</div>\n{text}'
        msg['text'] = escape(text)
        return msg


class Gauge(ValueIndicator):
    """
    A Gauge represents a value in some range as a position on
    speedometer or gauge. It is similar to a Dial but visually a lot
    busier.
    """

    annulus_width = param.Integer(default=10, doc="""
      Width of the gauge annulus.""")

    bounds = param.Range(default=(0, 100), doc="""
      The upper and lower bound of the dial.""")

    colors = param.List(default=None, doc="""
      Color thresholds for the Gauge, specified as a list of tuples
      of the fractional threshold and the color to switch to.""")

    custom_opts = param.Dict(doc="""
      Additional options to pass to the ECharts Gauge definition.""")

    height = param.Integer(default=300, bounds=(0, None))

    end_angle = param.Number(default=-45, doc="""
      Angle at which the gauge ends.""")

    format = param.String(default='{value}%', doc="""
      Formatting string for the value indicator.""")

    num_splits = param.Integer(default=10, doc="""
      Number of splits along the gauge.""")

    show_ticks = param.Boolean(default=True, doc="""
      Whether to show ticks along the dials.""")

    show_labels = param.Boolean(default=True, doc="""
      Whether to show tick labels along the dials.""")

    start_angle = param.Number(default=225, doc="""
      Angle at which the gauge starts.""")

    tooltip_format = param.String(default='{b} : {c}%', doc="""
      Formatting string for the hover tooltip.""")

    title_size = param.Integer(default=18, doc="""
      Size of title font.""")

    value = param.Number(default=25, doc="""
      Value to indicate on the gauge a value within the declared bounds.""")

    width = param.Integer(default=300, bounds=(0, None))

    _rename = {}

    @property
    def _widget_type(self):
        if 'panel.models.echarts' not in sys.modules:
            from ..models.echarts import ECharts
        else:
            ECharts = getattr(sys.modules['panel.models.echarts'], 'ECharts')
        return ECharts

    def __init__(self, **params):
        super().__init__(**params)
        self._update_value_bounds()

    @param.depends('bounds', watch=True)
    def _update_value_bounds(self):
        self.param.value.bounds = self.bounds

    def _process_param_change(self, msg):
        msg = super()._process_param_change(msg)
        vmin, vmax = msg.pop('bounds', self.bounds)
        msg['data'] = {
            'tooltip': {
                'formatter': msg.pop('tooltip_format', self.tooltip_format)
            },
            'series': [{
                'name': 'Gauge',
                'type': 'gauge',
                'axisTick': {'show': msg.pop('show_ticks', self.show_ticks)},
                'axisLabel': {'show': msg.pop('show_labels', self.show_labels)},
                'title': {'fontWeight': 'bold', 'fontSize': msg.pop('title_size', self.title_size)},
                'splitLine': {'show': True},
                'radius': '100%',
                'detail': {'formatter': msg.pop('format', self.format)},
                'min': vmin,
                'max': vmax,
                'startAngle': msg.pop('start_angle', self.start_angle),
                'endAngle': msg.pop('end_angle', self.end_angle),
                'splitNumber': msg.pop('num_splits', self.num_splits),
                'data': [{'value': msg.pop('value', self.value), 'name': self.name}],
                'axisLine': {
                    'lineStyle': {
                        'width': msg.pop('annulus_width', self.annulus_width),
                    }
                }
            }]
        }
        colors = msg.pop('colors', self.colors)
        if colors:
            msg['data']['series'][0]['axisLine']['lineStyle']['color'] = colors
        custom_opts = msg.pop('custom_opts', self.custom_opts)
        if custom_opts:
            gauge = msg['data']['series'][0]
            for k, v in custom_opts.items():
                if k not in gauge or not isinstance(gauge[k], dict):
                    gauge[k] = v
                else:
                    gauge[k].update(v)
        return msg


class Dial(ValueIndicator):
    """
    A Dial represents a value in some range as a position on an
    annular dial. It is similar to a Gauge but more minimal visually.
    """

    annulus_width = param.Number(default=0.2, doc="""
      Width of the radial annulus as a fraction of the total.""")

    bounds = param.Range(default=(0, 100), doc="""
      The upper and lower bound of the dial.""")

    colors = param.List(default=None, doc="""
      Color thresholds for the Dial, specified as a list of tuples
      of the fractional threshold and the color to switch to.""")

    default_color = param.String(default='lightblue', doc="""
      Color of the radial annulus if not color thresholds are supplied.""")

    end_angle = param.Number(default=25, doc="""
      Angle at which the dial ends.""")

    format = param.String(default='{value}%', doc="""
      Formatting string for the value indicator and lower/upper bounds.""")

    height = param.Integer(default=250, bounds=(1, None))

    nan_format = param.String(default='-', doc="""
      How to format nan values.""")

    needle_color = param.String(default='black', doc="""
      Color of the Dial needle.""")

    needle_width = param.Number(default=0.1, doc="""
      Radial width of the needle.""")

    start_angle = param.Number(default=-205, doc="""
      Angle at which the dial starts.""")

    tick_size = param.String(default=None, doc="""
      Font size of the Dial min/max labels.""")

    title_size = param.String(default=None, doc="""
      Font size of the Dial title.""")

    unfilled_color = param.String(default='whitesmoke', doc="""
      Color of the unfilled region of the Dial.""")

    value_size = param.String(default=None, doc="""
      Font size of the Dial value label.""")

    value = param.Number(default=25, allow_None=True, doc="""
      Value to indicate on the dial a value within the declared bounds.""")

    width = param.Integer(default=250, bounds=(1, None))

    _manual_params = [
        'value', 'start_angle', 'end_angle', 'bounds',
        'annulus_width', 'format', 'background', 'needle_width',
        'tick_size', 'title_size', 'value_size', 'colors',
        'default_color', 'unfilled_color', 'height',
        'width', 'nan_format', 'needle_color'
    ]

    _data_params = _manual_params

    _rename = {'background': 'background_fill_color'}

    def __init__(self, **params):
        super().__init__(**params)
        self._update_value_bounds()

    @param.depends('bounds', watch=True)
    def _update_value_bounds(self):
        self.param.value.bounds = self.bounds

    def _get_data(self):
        vmin, vmax = self.bounds
        value = self.value
        if value is None:
            value = float('nan')
        fraction = (value-vmin)/(vmax-vmin)
        start = (np.radians(360-self.start_angle) - pi % (2*pi)) + pi
        end = (np.radians(360-self.end_angle) - pi % (2*pi)) + pi
        distance = (abs(end-start) % (pi*2))
        if end>start:
            distance = (pi*2)-distance
        radial_fraction = distance*fraction
        angle = start if np.isnan(fraction) else (start-radial_fraction)
        inner_radius = 1-self.annulus_width

        color = self.default_color
        for val, clr in (self.colors or [])[::-1]:
            if fraction <= val:
                color = clr

        annulus_data = {
            'starts': np.array([start, angle]),
            'ends' :  np.array([angle, end]),
            'color':  [color, self.unfilled_color],
            'radius': np.array([inner_radius, inner_radius])
        }

        x0s, y0s, x1s, y1s, clrs = [], [], [], [], []
        colors = self.colors or []
        for (val, _), (_, clr) in zip(colors[:-1], colors[1:]):
            tangle = start-(distance*val)
            if (vmin + val * (vmax-vmin)) <= value:
                continue
            x0, y0 = np.cos(tangle), np.sin(tangle)
            x1, y1 = x0*inner_radius, y0*inner_radius
            x0s.append(x0)
            y0s.append(y0)
            x1s.append(x1)
            y1s.append(y1)
            clrs.append(clr)

        threshold_data = {
            'x0': x0s, 'y0': y0s, 'x1': x1s, 'y1': y1s, 'color': clrs
        }

        center_radius = 1-self.annulus_width/2.
        x, y = np.cos(angle)*center_radius, np.sin(angle)*center_radius
        needle_start = pi+angle-(self.needle_width/2.)
        needle_end = pi+angle+(self.needle_width/2.)
        needle_data = {
            'x':      np.array([x]),
            'y':      np.array([y]),
            'start':  np.array([needle_start]),
            'end':    np.array([needle_end]),
            'radius': np.array([center_radius])
        }

        value = self.format.format(value=value).replace('nan', self.nan_format)
        min_value = self.format.format(value=vmin)
        max_value = self.format.format(value=vmax)
        tminx, tminy = np.cos(start)*center_radius, np.sin(start)*center_radius
        tmaxx, tmaxy = np.cos(end)*center_radius, np.sin(end)*center_radius
        tmin_angle, tmax_angle = start+pi, end+pi % pi
        scale = (self.height/400)
        title_size = self.title_size if self.title_size else '%spt' % (scale*32)
        value_size = self.value_size if self.value_size else '%spt' % (scale*48)
        tick_size = self.tick_size if self.tick_size else '%spt' % (scale*18)

        text_data= {
            'x':    np.array([0, 0, tminx, tmaxx]),
            'y':    np.array([-.2, -.5, tminy, tmaxy]),
            'text': [self.name, value, min_value, max_value],
            'rot':  np.array([0, 0, tmin_angle, tmax_angle]),
            'size': [title_size, value_size, tick_size, tick_size],
            'color': ['black', color, 'black', 'black']
        }
        return annulus_data, needle_data, threshold_data, text_data

    def _get_model(self, doc, root=None, parent=None, comm=None):
        params = self._process_param_change(self._init_params())
        model = figure(
            x_range=(-1,1), y_range=(-1,1), tools=[],
            outline_line_color=None, toolbar_location=None,
            width=self.width, height=self.height, **params
        )
        model.xaxis.visible = False
        model.yaxis.visible = False
        model.grid.visible = False

        annulus, needle, threshold, text = self._get_data()

        # Draw annulus
        annulus_source = ColumnDataSource(data=annulus, name='annulus_source')
        model.annular_wedge(
            x=0, y=0, inner_radius='radius', outer_radius=1, start_angle='starts',
            end_angle='ends', line_color='gray', color='color', direction='clock',
            source=annulus_source
        )

        # Draw needle
        needle_source = ColumnDataSource(data=needle, name='needle_source')
        model.wedge(
            x='x', y='y', radius='radius', start_angle='start', end_angle='end',
            fill_color=self.needle_color, line_color=self.needle_color,
            source=needle_source, name='needle_renderer'
        )

        # Draw thresholds
        threshold_source = ColumnDataSource(data=threshold, name='threshold_source')
        model.segment(
            x0='x0', x1='x1', y0='y0', y1='y1', line_color='color', source=threshold_source,
            line_width=2
        )

        # Draw labels
        text_source = ColumnDataSource(data=text, name='label_source')
        model.text(
            x='x', y='y', text='text', font_size='size', text_align='center',
            text_color='color', source=text_source, text_baseline='top',
            angle='rot'
        )

        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _manual_update(self, events, model, doc, root, parent, comm):
        update_data = False
        for event in events:
            if event.name in ('width', 'height'):
                model.update(**{event.name: event.new})
            if event.name in self._data_params:
                update_data = True
            elif event.name == 'needle_color':
                needle_r = model.select(name='needle_renderer')
                needle_r.glyph.line_color = event.new
                needle_r.glyph.fill_color = event.new
        if not update_data:
            return
        annulus, needle, threshold, labels = self._get_data()
        model.select(name='annulus_source').data.update(annulus)
        model.select(name='needle_source').data.update(needle)
        model.select(name='threshold_source').data.update(threshold)
        model.select(name='label_source').data.update(labels)
