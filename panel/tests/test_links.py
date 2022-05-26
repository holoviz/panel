try:
    import holoviews as hv
except ImportError:
    hv = None

import pytest

from bokeh.plotting import figure

from panel.layout import Row
from panel.links import Link
from panel.pane import Bokeh, HoloViews
from panel.tests.util import hv_available
from panel.widgets import (
    ColorPicker, DatetimeInput, FloatSlider, RangeSlider, TextInput,
)


def test_widget_link_bidirectional():
    t1 = TextInput()
    t2 = TextInput()

    t1.link(t2, value='value', bidirectional=True)

    t1.value = 'ABC'
    assert t1.value == 'ABC'
    assert t2.value == 'ABC'

    t2.value = 'DEF'
    assert t1.value == 'DEF'
    assert t2.value == 'DEF'


def test_widget_jslink_bidirectional(document, comm):
    t1 = TextInput()
    t2 = TextInput()

    t1.jslink(t2, value='value', bidirectional=True)

    row = Row(t1, t2)

    model = row.get_root(document, comm)

    tm1, tm2 = model.children

    link1_customjs = tm1.js_property_callbacks['change:value'][-1]
    link2_customjs = tm2.js_property_callbacks['change:value'][-1]

    assert link1_customjs.args['source'] is tm1
    assert link2_customjs.args['source'] is tm2
    assert link1_customjs.args['target'] is tm2
    assert link2_customjs.args['target'] is tm1


def test_widget_link_source_param_not_found():
    t1 = TextInput()
    t2 = TextInput()

    with pytest.raises(ValueError) as excinfo:
        t1.jslink(t2, value1='value')
    assert "Could not jslink \'value1\' parameter" in str(excinfo)


def test_widget_link_target_param_not_found():
    t1 = TextInput()
    t2 = TextInput()

    with pytest.raises(ValueError) as excinfo:
        t1.jslink(t2, value='value1')
    assert "Could not jslink \'value1\' parameter" in str(excinfo)


def test_widget_link_no_transform_error():
    t1 = DatetimeInput()
    t2 = TextInput()

    with pytest.raises(ValueError) as excinfo:
        t1.jslink(t2, value='value')
    assert "Cannot jslink \'value\' parameter on DatetimeInput object" in str(excinfo)


def test_widget_link_no_target_transform_error():
    t1 = DatetimeInput()
    t2 = TextInput()

    with pytest.raises(ValueError) as excinfo:
        t2.jslink(t1, value='value')
    assert ("Cannot jslink 'value' parameter on TextInput object to 'value' parameter on DatetimeInput") in str(excinfo)


@hv_available
def test_pnwidget_hvplot_links(document, comm):
    size_widget = FloatSlider(value=5, start=1, end=10)
    points1 = hv.Points([1, 2, 3])

    size_widget.jslink(points1, value='glyph.size')

    row = Row(points1, size_widget)
    model = row.get_root(document, comm=comm)
    hv_views = row.select(HoloViews)
    widg_views = row.select(FloatSlider)

    assert len(hv_views) == 1
    assert len(widg_views) == 1
    slider = widg_views[0]._models[model.ref['id']][0]
    scatter = hv_views[0]._plots[model.ref['id']][0].handles['glyph']

    link_customjs = slider.js_property_callbacks['change:value'][-1]
    assert link_customjs.args['source'] is slider
    assert link_customjs.args['target'] is scatter

    code = """
    var value = source['value'];
    value = value;
    value = value;
    try {
      var property = target.properties['size'];
      if (property !== undefined) { property.validate(value); }
    } catch(err) {
      console.log('WARNING: Could not set size on target, raised error: ' + err);
      return;
    }
    try {
      target['size'] = value;
    } catch(err) {
      console.log(err)
    }
    """
    assert link_customjs.code == code


@hv_available
def test_bkwidget_hvplot_links(document, comm):
    from bokeh.models import Slider
    bokeh_widget = Slider(value=5, start=1, end=10, step=1e-1)
    points1 = hv.Points([1, 2, 3])

    Link(bokeh_widget, points1, properties={'value': 'glyph.size'})

    row = Row(points1, bokeh_widget)
    model = row.get_root(document, comm=comm)
    hv_views = row.select(HoloViews)

    assert len(hv_views) == 1
    slider = bokeh_widget
    scatter = hv_views[0]._plots[model.ref['id']][0].handles['glyph']

    link_customjs = slider.js_property_callbacks['change:value'][-1]
    assert link_customjs.args['source'] is slider
    assert link_customjs.args['target'] is scatter

    code = """
    var value = source['value'];
    value = value;
    value = value;
    try {
      var property = target.properties['size'];
      if (property !== undefined) { property.validate(value); }
    } catch(err) {
      console.log('WARNING: Could not set size on target, raised error: ' + err);
      return;
    }
    try {
      target['size'] = value;
    } catch(err) {
      console.log(err)
    }
    """
    assert link_customjs.code == code


def test_bkwidget_bkplot_links(document, comm):
    from bokeh.models import Slider
    bokeh_widget = Slider(value=5, start=1, end=10, step=1e-1)
    bokeh_fig = figure()
    scatter = bokeh_fig.scatter([1, 2, 3], [1, 2, 3])

    Link(bokeh_widget, scatter, properties={'value': 'glyph.size'})

    row = Row(bokeh_fig, bokeh_widget)
    row.get_root(document, comm=comm)

    slider = bokeh_widget

    link_customjs = slider.js_property_callbacks['change:value'][-1]
    assert link_customjs.args['source'] is slider
    assert link_customjs.args['target'] is scatter.glyph

    code = """
    var value = source['value'];
    value = value;
    value = value;
    try {
      var property = target.properties['size'];
      if (property !== undefined) { property.validate(value); }
    } catch(err) {
      console.log('WARNING: Could not set size on target, raised error: ' + err);
      return;
    }
    try {
      target['size'] = value;
    } catch(err) {
      console.log(err)
    }
    """
    assert link_customjs.code == code


def test_widget_bkplot_link(document, comm):
    widget = ColorPicker(value='#ff00ff')
    bokeh_fig = figure()
    scatter = bokeh_fig.scatter([1, 2, 3], [1, 2, 3])

    widget.jslink(scatter.glyph, value='fill_color')

    row = Row(bokeh_fig, widget)
    model = row.get_root(document, comm=comm)

    link_customjs = model.children[1].js_property_callbacks['change:color'][-1]
    assert link_customjs.args['source'] is model.children[1]
    assert link_customjs.args['target'] is scatter.glyph
    assert scatter.glyph.fill_color == '#ff00ff'

    code = """
    var value = source['color'];
    value = value;
    value = value;
    try {
      var property = target.properties['fill_color'];
      if (property !== undefined) { property.validate(value); }
    } catch(err) {
      console.log('WARNING: Could not set fill_color on target, raised error: ' + err);
      return;
    }
    try {
      target['fill_color'] = value;
    } catch(err) {
      console.log(err)
    }
    """
    assert link_customjs.code == code


def test_bokeh_figure_jslink(document, comm):
    fig = figure()

    pane = Bokeh(fig)
    t1 = TextInput()

    pane.jslink(t1, **{'x_range.start': 'value'})
    row = Row(pane, t1)

    model = row.get_root(document, comm)

    link_customjs = fig.x_range.js_property_callbacks['change:start'][-1]
    assert link_customjs.args['source'] == fig.x_range
    assert link_customjs.args['target'] == model.children[1]
    assert link_customjs.code == """
    var value = source['start'];
    value = value;
    value = value;
    try {
      var property = target.properties['value'];
      if (property !== undefined) { property.validate(value); }
    } catch(err) {
      console.log('WARNING: Could not set value on target, raised error: ' + err);
      return;
    }
    try {
      target['value'] = value;
    } catch(err) {
      console.log(err)
    }
    """

def test_widget_jscallback(document, comm):
    widget = ColorPicker(value='#ff00ff')

    widget.jscallback(value='some_code')

    model = widget.get_root(document, comm=comm)

    customjs = model.js_property_callbacks['change:color'][-1]
    assert customjs.args['source'] is model
    assert customjs.code == "try { some_code } catch(err) { console.log(err) }"


def test_widget_jscallback_args_scalar(document, comm):
    widget = ColorPicker(value='#ff00ff')

    widget.jscallback(value='some_code', args={'scalar': 1})

    model = widget.get_root(document, comm=comm)

    customjs = model.js_property_callbacks['change:color'][-1]
    assert customjs.args['scalar'] == 1


def test_widget_jscallback_args_model(document, comm):
    widget = ColorPicker(value='#ff00ff')
    widget2 = ColorPicker(value='#ff00ff')

    widget.jscallback(value='some_code', args={'widget': widget2})

    model = Row(widget, widget2).get_root(document, comm=comm)

    customjs = model.children[0].js_property_callbacks['change:color'][-1]
    assert customjs.args['source'] is model.children[0]
    assert customjs.args['widget'] is model.children[1]
    assert customjs.code == "try { some_code } catch(err) { console.log(err) }"


@hv_available
def test_hvplot_jscallback(document, comm):
    points1 = hv.Points([1, 2, 3])

    hvplot = HoloViews(points1)

    hvplot.jscallback(**{'x_range.start': "some_code"})

    model = hvplot.get_root(document, comm=comm)
    x_range = hvplot._plots[model.ref['id']][0].handles['x_range']

    customjs = x_range.js_property_callbacks['change:start'][-1]
    assert customjs.args['source'] is x_range
    assert customjs.code == "try { some_code } catch(err) { console.log(err) }"


@hv_available
def test_link_with_customcode(document, comm):
    range_widget = RangeSlider(start=0., end=1.)
    curve = hv.Curve([])
    code = """
      x_range.start = source.value[0]
      x_range.end = source.value[1]
    """
    range_widget.jslink(curve, code={'value': code})
    row = Row(curve, range_widget)

    range_widget.value = (0.5, 0.7)
    model = row.get_root(document, comm=comm)
    hv_views = row.select(HoloViews)
    widg_views = row.select(RangeSlider)

    assert len(hv_views) == 1
    assert len(widg_views) == 1
    range_slider = widg_views[0]._models[model.ref['id']][0]
    x_range = hv_views[0]._plots[model.ref['id']][0].handles['x_range']

    link_customjs = range_slider.js_property_callbacks['change:value'][-1]
    assert link_customjs.args['source'] is range_slider
    assert link_customjs.args['x_range'] is x_range
    assert link_customjs.code == "try { %s } catch(err) { console.log(err) }" % code
