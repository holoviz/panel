from __future__ import absolute_import

from base64 import b64decode
from collections import OrderedDict
import pytest

from bokeh.models import (Div, Row as BkRow, WidgetBox as BkWidgetBox,
                          GlyphRenderer, Circle, Line)
from bokeh.plotting import Figure
from panel.layout import Column
from panel.pane import (Pane, PaneBase, Bokeh, HoloViews, Matplotlib,
                        HTML, Str, PNG, JPG, GIF)
from panel.widgets import FloatSlider, DiscreteSlider, Select

try:
    import holoviews as hv
except:
    hv = None
hv_available = pytest.mark.skipif(hv is None, reason="requires holoviews")

try:
    import matplotlib as mpl
    mpl.use('Agg')
except:
    mpl = None
mpl_available = pytest.mark.skipif(mpl is None, reason="requires matplotlib")

from .fixtures import mpl_figure
from .test_layout import get_div


def test_get_bokeh_pane_type():
    div = Div()
    assert PaneBase.get_pane_type(div) is Bokeh


def test_bokeh_pane(document, comm):
    div = Div()
    pane = Pane(div)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert model.ref['id'] in pane._callbacks
    assert get_div(model) is div

    # Replace Pane.object
    div2 = Div()
    pane.object = div2
    new_model = row.children[0]
    assert get_div(new_model) is div2
    assert new_model.ref['id'] in pane._callbacks
    assert model.ref['id'] not in pane._callbacks

    # Cleanup
    pane._cleanup(new_model)
    assert pane._callbacks == {}


@hv_available
def test_get_holoviews_pane_type():
    curve = hv.Curve([1, 2, 3])
    assert PaneBase.get_pane_type(curve) is HoloViews


@pytest.mark.usefixtures("hv_mpl")
@mpl_available
@hv_available
def test_holoviews_pane_mpl_renderer(document, comm):
    curve = hv.Curve([1, 2, 3])
    pane = Pane(curve)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    assert len(pane._callbacks) == 1
    model = row.children[0]
    assert isinstance(model, BkWidgetBox)
    div = model.children[0]
    assert isinstance(div, Div)
    assert '<img' in div.text

    # Replace Pane.object
    scatter = hv.Scatter([1, 2, 3])
    pane.object = scatter
    model = row.children[0]
    assert isinstance(model, BkWidgetBox)
    div2 = model.children[0]
    assert isinstance(div2, Div)
    assert div2.text != div.text

    # Cleanup
    pane._cleanup(model)
    assert pane._callbacks == {}


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_pane_bokeh_renderer(document, comm):
    curve = hv.Curve([1, 2, 3])
    pane = Pane(curve)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    assert len(pane._callbacks) == 1
    model = row.children[0]
    assert isinstance(model, Figure)
    renderers = [r for r in model.renderers if isinstance(r, GlyphRenderer)]
    assert len(renderers) == 1
    assert isinstance(renderers[0].glyph, Line)

    # Replace Pane.object
    scatter = hv.Scatter([1, 2, 3])
    pane.object = scatter
    model = row.children[0]
    assert isinstance(model, Figure)
    renderers = [r for r in model.renderers if isinstance(r, GlyphRenderer)]
    assert len(renderers) == 1
    assert isinstance(renderers[0].glyph, Circle)
    assert len(pane._callbacks) == 1

    # Cleanup
    pane._cleanup(model)
    assert pane._callbacks == {}


@hv_available
def test_holoviews_widgets_from_dynamicmap(document, comm):
    range_dim = hv.Dimension('A', range=(0, 10.))
    range_step_dim = hv.Dimension('B', range=(0, 10.), step=0.2)
    range_default_dim = hv.Dimension('C', range=(0, 10.), default=3)
    value_dim = hv.Dimension('D', values=['a', 'b', 'c'])
    value_default_dim = hv.Dimension('E', values=['a', 'b', 'c', 'd'], default='b')
    value_numeric_dim = hv.Dimension('F', values=[1, 3, 10], default=3)
    kdims = [range_dim, range_step_dim, range_default_dim,
             value_dim, value_default_dim, value_numeric_dim]
    dmap = hv.DynamicMap(lambda A, B, C, D, E, F: hv.Curve([]), kdims=kdims)
    widgets = HoloViews.widgets_from_dimensions(dmap)

    assert len(widgets) == len(kdims)

    assert isinstance(widgets[0], FloatSlider)
    assert widgets[0].name == 'A'
    assert widgets[0].start == range_dim.range[0]
    assert widgets[0].end == range_dim.range[1]
    assert widgets[0].value == range_dim.range[0]
    assert widgets[0].step == 0.1

    assert isinstance(widgets[1], FloatSlider)
    assert widgets[1].name == 'B'
    assert widgets[1].start == range_step_dim.range[0]
    assert widgets[1].end == range_step_dim.range[1]
    assert widgets[1].value == range_step_dim.range[0]
    assert widgets[1].step == range_step_dim.step

    assert isinstance(widgets[2], FloatSlider)
    assert widgets[2].name == 'C'
    assert widgets[2].start == range_default_dim.range[0]
    assert widgets[2].end == range_default_dim.range[1]
    assert widgets[2].value == range_default_dim.default
    assert widgets[2].step == 0.1

    assert isinstance(widgets[3], Select)
    assert widgets[3].name == 'D'
    assert widgets[3].options == OrderedDict(zip(value_dim.values, value_dim.values))
    assert widgets[3].value == value_dim.values[0]

    assert isinstance(widgets[4], Select)
    assert widgets[4].name == 'E'
    assert widgets[4].options == OrderedDict(zip(value_default_dim.values, value_default_dim.values))
    assert widgets[4].value == value_default_dim.default

    assert isinstance(widgets[5], DiscreteSlider)
    assert widgets[5].name == 'F'
    assert widgets[5].options == OrderedDict([(str(v), v) for v in value_numeric_dim.values])
    assert widgets[5].value == value_numeric_dim.default


@hv_available
def test_holoviews_with_widgets(document, comm):
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    hv_pane = HoloViews(hmap)
    layout = hv_pane._get_root(document, comm)
    model = layout.children[0]
    assert len(hv_pane.widget_box.objects) == 2
    assert hv_pane.widget_box.objects[0].name == 'X'
    assert hv_pane.widget_box.objects[1].name == 'Y'

    assert model.ref['id'] in hv_pane._callbacks

    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['A', 'B'])
    hv_pane.object = hmap
    assert model.ref['id'] not in hv_pane._callbacks
    assert len(hv_pane.widget_box.objects) == 2
    assert hv_pane.widget_box.objects[0].name == 'A'
    assert hv_pane.widget_box.objects[1].name == 'B'


@hv_available
def test_holoviews_with_widgets_not_shown(document, comm):
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    hv_pane = HoloViews(hmap, show_widgets=False)
    layout_obj = Column(hv_pane, hv_pane.widget_box)
    layout = layout_obj._get_root(document, comm)
    model = layout.children[0]
    assert len(hv_pane.widget_box.objects) == 2
    assert hv_pane.widget_box.objects[0].name == 'X'
    assert hv_pane.widget_box.objects[1].name == 'Y'

    assert model.ref['id'] in hv_pane._callbacks

    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['A', 'B'])
    hv_pane.object = hmap
    assert model.ref['id'] not in hv_pane._callbacks
    assert len(hv_pane.widget_box.objects) == 2
    assert hv_pane.widget_box.objects[0].name == 'A'
    assert hv_pane.widget_box.objects[1].name == 'B'

    
@hv_available
def test_holoviews_widgets_from_holomap():
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    widgets = HoloViews.widgets_from_dimensions(hmap)

    assert isinstance(widgets[0], DiscreteSlider)
    assert widgets[0].name == 'X'
    assert widgets[0].options == OrderedDict([(str(i), i) for i in range(3)])
    assert widgets[0].value == 0

    assert isinstance(widgets[1], Select)
    assert widgets[1].name == 'Y'
    assert widgets[1].options == OrderedDict([(i, i) for i in ['A', 'B', 'C']])
    assert widgets[1].value == 'A'


@hv_available
def test_holoviews_widgets_explicit_widget_type_override():
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    widgets = HoloViews.widgets_from_dimensions(hmap, widget_types={'X': Select})

    assert isinstance(widgets[0], Select)
    assert widgets[0].name == 'X'
    assert widgets[0].options == OrderedDict([(str(i), i) for i in range(3)])
    assert widgets[0].value == 0


@hv_available
def test_holoviews_widgets_invalid_widget_type_override():
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    with pytest.raises(ValueError):
        HoloViews.widgets_from_dimensions(hmap, widget_types={'X': 1})


@hv_available
def test_holoviews_widgets_explicit_widget_instance_override():
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    widget = Select(options=[1, 2, 3], value=3)
    widgets = HoloViews.widgets_from_dimensions(hmap, widget_types={'X': widget})

    assert widgets[0] is widget

    
@mpl_available
def test_get_matplotlib_pane_type():
    assert PaneBase.get_pane_type(mpl_figure()) is Matplotlib


@mpl_available
def test_matplotlib_pane(document, comm):
    pane = Pane(mpl_figure())

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    assert len(pane._callbacks) == 1
    model = row.children[0]
    assert isinstance(model, BkWidgetBox)
    div = model.children[0]
    assert isinstance(div, Div)
    assert '<img' in div.text
    text = div.text

    # Replace Pane.object
    pane.object = mpl_figure()
    model = row.children[0]
    assert isinstance(model, BkWidgetBox)
    div2 = model.children[0]
    assert div is div2
    assert div.text != text

    # Cleanup
    pane._cleanup(model)
    assert pane._callbacks == {}


def test_get_html_pane_type():
    assert PaneBase.get_pane_type("<h1>Test</h1>") is HTML


def test_html_pane(document, comm):
    pane = Pane("<h1>Test</h1>")

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert model.ref['id'] in pane._callbacks
    div = get_div(model)
    assert div.text == "<h1>Test</h1>"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    model = row.children[0]
    assert div is get_div(model)
    assert model.ref['id'] in pane._callbacks
    assert div.text == "<h2>Test</h2>"

    # Cleanup
    pane._cleanup(model)
    assert pane._callbacks == {}


def test_string_pane(document, comm):
    pane = Str("<h1>Test</h1>")

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert model.ref['id'] in pane._callbacks
    div = get_div(model)
    assert div.text == "<pre>&lt;h1&gt;Test&lt;/h1&gt;</pre>"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    model = row.children[0]
    assert div is get_div(model)
    assert model.ref['id'] in pane._callbacks
    assert div.text == "<pre>&lt;h2&gt;Test&lt;/h2&gt;</pre>"

    # Cleanup
    pane._cleanup(model)
    assert pane._callbacks == {}


twopixel = dict(\
    gif = b'R0lGODlhAgABAPAAAEQ6Q2NYYCH5BAAAAAAAIf8LSW1hZ2VNYWdpY2sNZ2FtbWE' + \
          b'9MC40NTQ1NQAsAAAAAAIAAQAAAgIMCgA7',
    png = b'iVBORw0KGgoAAAANSUhEUgAAAAIAAAABCAYAAAD0In+KAAAAFElEQVQIHQEJAPb' + \
          b'/AWNYYP/h4uMAFL0EwlEn99gAAAAASUVORK5CYII=',
    jpg = b'/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQE' + \
          b'BAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQ' + \
          b'EBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBA' + \
          b'QEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAIDAREAAhEBAxEB/8QAFAABAAAAAAAA' + \
          b'AAAAAAAAAAAACf/EABoQAAEFAQAAAAAAAAAAAAAAAAYABAU2dbX/xAAVAQEBAAA' + \
          b'AAAAAAAAAAAAAAAAFBv/EABkRAAEFAAAAAAAAAAAAAAAAAAEAAjFxsf/aAAwDAQ' + \
          b'ACEQMRAD8AA0qs5HvTHQcJdsChioXSbOr/2Q==')

def test_imgshape():
    for t in [PNG, JPG, GIF]:
        w,h = t._imgshape(b64decode(twopixel[t.name.lower()]))
        assert w == 2
        assert h == 1
