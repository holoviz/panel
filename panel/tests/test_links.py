from __future__ import absolute_import

import pytest

from panel.layout import Row
from panel.holoviews import HoloViews
from panel.widgets import FloatSlider
from panel.links import WidgetLink

try:
    import holoviews as hv
except:
    hv = None
hv_available = pytest.mark.skipif(hv is None, reason="requires holoviews")

 
@hv_available
def test_pnwidget_hvplot_links(document, comm):
    size_widget = FloatSlider(value=5, start=1, end=10)
    points1 = hv.Points([1, 2, 3])
      
    WidgetLink(size_widget, points1, target_model='glyph', target_property='size')
      
    row = Row(points1, size_widget)
    model = row._get_root(document, comm=comm)
    hv_views = row.select(HoloViews)
    widg_views = row.select(FloatSlider)
      
    assert len(hv_views) == 1
    assert len(widg_views) == 1
    slider = widg_views[0]._models[model.ref['id']]
    scatter = hv_views[0]._plots[model.ref['id']].handles['glyph']
      
    widgetlink_customjs = slider.js_property_callbacks['change:value'][-1]
    assert widgetlink_customjs.args['source'] is slider
    assert widgetlink_customjs.args['target'] is scatter
    assert widgetlink_customjs.args['target_model'] == 'glyph'
    assert widgetlink_customjs.args['target_property'] == 'size'
 
 
@hv_available 
def test_bkwidget_hvplot_links(document, comm):
    from bokeh.models import Slider
    bokeh_widget = Slider(value=5, start=1, end=10, step=1e-1)
    points1 = hv.Points([1, 2, 3])
       
    WidgetLink(bokeh_widget, points1, target_model='glyph', target_property='size')
       
    row = Row(points1, bokeh_widget)
    model = row._get_root(document, comm=comm)
    hv_views = row.select(HoloViews)
       
    assert len(hv_views) == 1
    slider = bokeh_widget
    scatter = hv_views[0]._plots[model.ref['id']].handles['glyph']
       
    widgetlink_customjs = slider.js_property_callbacks['change:value'][-1]
    assert widgetlink_customjs.args['source'] is slider
    assert widgetlink_customjs.args['target'] is scatter
    assert widgetlink_customjs.args['target_model'] == 'glyph'
    assert widgetlink_customjs.args['target_property'] == 'size'


def test_bkwidget_bkplot_links(document, comm):
    from bokeh.models import Slider
    from bokeh.plotting import figure
    bokeh_widget = Slider(value=5, start=1, end=10, step=1e-1)
    bokeh_fig = figure()
    scatter = bokeh_fig.scatter([1, 2, 3], [1, 2, 3])
      
    WidgetLink(bokeh_widget, scatter, target_model='glyph', target_property='size')
      
    row = Row(bokeh_fig, bokeh_widget)
    row._get_root(document, comm=comm)

    slider = bokeh_widget
      
    widgetlink_customjs = slider.js_property_callbacks['change:value'][-1]
    assert widgetlink_customjs.args['source'] is slider
    assert widgetlink_customjs.args['target'] is scatter.glyph
    assert widgetlink_customjs.args['target_property'] == 'size'
