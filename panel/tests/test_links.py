from __future__ import absolute_import

import pytest

from panel.layout import Row
from panel.holoviews import HoloViews
from panel.widgets import FloatSlider, RangeSlider
from panel.links import GenericLink

try:
    import holoviews as hv
except:
    hv = None
hv_available = pytest.mark.skipif(hv is None, reason="requires holoviews")


@hv_available
def test_pnwidget_hvplot_links(document, comm):
    size_widget = FloatSlider(value=5, start=1, end=10)
    points1 = hv.Points([1, 2, 3])

    size_widget.jslink(points1, value='glyph.size')

    row = Row(points1, size_widget)
    model = row._get_root(document, comm=comm)
    hv_views = row.select(HoloViews)
    widg_views = row.select(FloatSlider)

    assert len(hv_views) == 1
    assert len(widg_views) == 1
    slider = widg_views[0]._models[model.ref['id']]
    scatter = hv_views[0]._plots[model.ref['id']].handles['glyph']

    link_customjs = slider.js_property_callbacks['change:value'][-1]
    assert link_customjs.args['source'] is slider
    assert link_customjs.args['target'] is scatter

    
    code = ("value = source['value'];"
            "try { property = target.properties['size'];"
            "if (property !== undefined) { property.validate(value); } }"
            "catch(err) { console.log('WARNING: Could not set size on target, raised error: ' + err); return; }"
            "target['size'] = value")
    assert link_customjs.code == code


@hv_available
def test_bkwidget_hvplot_links(document, comm):
    from bokeh.models import Slider
    bokeh_widget = Slider(value=5, start=1, end=10, step=1e-1)
    points1 = hv.Points([1, 2, 3])

    GenericLink(bokeh_widget, points1, properties={'value': 'glyph.size'})

    row = Row(points1, bokeh_widget)
    model = row._get_root(document, comm=comm)
    hv_views = row.select(HoloViews)

    assert len(hv_views) == 1
    slider = bokeh_widget
    scatter = hv_views[0]._plots[model.ref['id']].handles['glyph']

    link_customjs = slider.js_property_callbacks['change:value'][-1]
    assert link_customjs.args['source'] is slider
    assert link_customjs.args['target'] is scatter

    code = ("value = source['value'];"
            "try { property = target.properties['size'];"
            "if (property !== undefined) { property.validate(value); } }"
            "catch(err) { console.log('WARNING: Could not set size on target, raised error: ' + err); return; }"
            "target['size'] = value")
    assert link_customjs.code == code

def test_bkwidget_bkplot_links(document, comm):
    from bokeh.models import Slider
    from bokeh.plotting import figure
    bokeh_widget = Slider(value=5, start=1, end=10, step=1e-1)
    bokeh_fig = figure()
    scatter = bokeh_fig.scatter([1, 2, 3], [1, 2, 3])

    GenericLink(bokeh_widget, scatter, properties={'value': 'glyph.size'})

    row = Row(bokeh_fig, bokeh_widget)
    row._get_root(document, comm=comm)

    slider = bokeh_widget

    link_customjs = slider.js_property_callbacks['change:value'][-1]
    assert link_customjs.args['source'] is slider
    assert link_customjs.args['target'] is scatter.glyph
    code = ("value = source['value'];"
            "try { property = target.properties['size'];"
            "if (property !== undefined) { property.validate(value); } }"
            "catch(err) { console.log('WARNING: Could not set size on target, raised error: ' + err); return; }"
            "target['size'] = value")
    assert link_customjs.code == code

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
    model = row._get_root(document, comm=comm)
    hv_views = row.select(HoloViews)
    widg_views = row.select(RangeSlider)

    assert len(hv_views) == 1
    assert len(widg_views) == 1
    range_slider = widg_views[0]._models[model.ref['id']]
    x_range = hv_views[0]._plots[model.ref['id']].handles['x_range']

    link_customjs = range_slider.js_property_callbacks['change:value'][-1]
    assert link_customjs.args['source'] is range_slider
    assert link_customjs.args['x_range'] is x_range
    assert link_customjs.code == code
