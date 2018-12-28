from __future__ import absolute_import

import pytest

from bokeh.plotting import Figure

from panel.layout import Column, Row
from panel.holoviews import HoloViews
from panel.widgets import FloatSlider
from panel.widgetlinks import WidgetLink 

try:
    import holoviews as hv
except:
    hv = None
hv_available = pytest.mark.skipif(hv is None, reason="requires holoviews")



@hv_available
def test_holoviews_axes_range_link(document, comm):
    from panel.holoviews import RangeAxesLink
    
    c1 = hv.Curve([])
    c2 = hv.Curve([])
    c3 = hv.Curve([])
    c4 = hv.Curve([])
    c5 = hv.Curve([])
    
    RangeAxesLink(c1,c2) #across pane
    hv_layout = c3+c4 #inner hv layout
    RangeAxesLink(c4,c5) #inner outter
    
    layout = Column(Row(c1,c2), Row(hv_layout, c5))
    column = layout._get_root(document, comm=comm)

    assert len(column.children) == 3
    r1, r2, _ = column.children

    assert (len(list(r1.select({'type': Figure}))) == 2)
    p1, p2 = r1.select({'type': Figure})
    
    assert p1.x_range == p2.x_range
    assert p1.y_range == p2.y_range
    
    assert (len(list(r2.select({'type': Figure}))) == 3)
    p3, p4, p5 = r2.select({'type': Figure})
    
    assert p3.x_range == p4.x_range == p5.x_range
    assert p3.y_range == p4.y_range == p5.y_range


@hv_available
def test_widget_links(document, comm):
    size_widget = FloatSlider(value=5, start=1, end=10)
    points1 = hv.Points([1,2,3])
    
    WidgetLink(size_widget, points1, target_model='glyph', target_property='size')
    
    row = Row(points1, size_widget)
    model = row._get_root(document, comm=comm)
    hv_views = row.select(HoloViews)
    widg_views = row.select(FloatSlider)
    
    assert len(hv_views) == 1
    assert len(widg_views) == 1
    slider = widg_views[0]._models[model.ref['id']]
    scatter = hv_views[0]._plots[model.ref['id']].handles['glyph']
    
    assert len(slider.js_property_callbacks['change:value']) == 2
    
    widgetlink_customjs = slider.js_property_callbacks['change:value'][-1]
    assert widgetlink_customjs.args['source'] is slider
    assert widgetlink_customjs.args['target'] is scatter
    assert widgetlink_customjs.args['target_model'] == 'glyph'
    assert widgetlink_customjs.args['target_property'] == 'size'
    
    