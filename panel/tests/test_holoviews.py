from __future__ import absolute_import

from collections import OrderedDict
import pytest

from bokeh.models import (Row as BkRow, Column as BkColumn, GlyphRenderer,
                          Scatter, Line)
from bokeh.plotting import Figure

from panel.holoviews import HoloViews
from panel.layout import Column, Row
from panel.pane import Pane, PaneBase
from panel.widgets import FloatSlider, DiscreteSlider, Select

try:
    import holoviews as hv
except:
    hv = None
hv_available = pytest.mark.skipif(hv is None, reason="requires holoviews")

from .test_layout import get_div
from .test_panes import mpl_available


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
    assert pane._models[row.ref['id']] is model
    div = get_div(model)
    assert '<img' in div.text

    # Replace Pane.object
    scatter = hv.Scatter([1, 2, 3])
    pane.object = scatter
    model = row.children[0]
    div2 = get_div(model)
    assert div2.text != div.text

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}


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
    assert pane._models[row.ref['id']] is model
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
    assert isinstance(renderers[0].glyph, Scatter)
    assert len(pane._callbacks) == 1
    assert pane._models[row.ref['id']] is model

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}


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
    widgets, _ = HoloViews.widgets_from_dimensions(dmap)

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

    assert layout.ref['id'] in hv_pane._callbacks
    assert hv_pane._models[layout.ref['id']] is model

    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['A', 'B'])
    hv_pane.object = hmap
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

    assert layout.ref['id'] in hv_pane._callbacks
    assert hv_pane._models[layout.ref['id']] is model

    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['A', 'B'])
    hv_pane.object = hmap
    assert model.ref['id'] not in hv_pane._callbacks
    assert len(hv_pane.widget_box.objects) == 2
    assert hv_pane.widget_box.objects[0].name == 'A'
    assert hv_pane.widget_box.objects[1].name == 'B'

    
@hv_available
def test_holoviews_widgets_from_holomap():
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    widgets, _ = HoloViews.widgets_from_dimensions(hmap)

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

    widgets, _ = HoloViews.widgets_from_dimensions(hmap, widget_types={'X': Select})

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
    widgets, _ = HoloViews.widgets_from_dimensions(hmap, widget_types={'X': widget})

    assert widgets[0] is widget


@hv_available
def test_holoviews_link_across_panes(document, comm):
    from bokeh.models.tools import RangeTool
    from holoviews.plotting.links import RangeToolLink

    c1 = hv.Curve([])
    c2 = hv.Curve([])

    RangeToolLink(c1, c2)

    layout = Row(c1, c2)
    row = layout._get_root(document, comm=comm)

    assert len(row.children) == 2
    p1, p2 = row.children

    assert isinstance(p1, Figure)
    assert isinstance(p2, Figure)

    range_tool = row.select_one({'type': RangeTool})
    assert isinstance(range_tool, RangeTool)
    range_tool.x_range = p2.x_range


@hv_available
def test_holoviews_link_within_pane(document, comm):
    from bokeh.models.tools import RangeTool
    from holoviews.plotting.links import RangeToolLink

    c1 = hv.Curve([])
    c2 = hv.Curve([])

    RangeToolLink(c1, c2)

    pane = Pane(hv.Layout([c1, c2]))
    column = pane._get_root(document, comm=comm)

    assert len(column.children) == 1
    subcolumn = column.children[0]
    assert isinstance(subcolumn, BkColumn)
    assert len(subcolumn.children) == 2
    toolbar, subsubcolumn = subcolumn.children
    assert isinstance(subsubcolumn, BkColumn)
    assert len(subsubcolumn.children) == 1
    row = subsubcolumn.children[0]
    assert isinstance(row, BkRow)
    assert len(row.children) == 2
    p1, p2 = row.children

    assert isinstance(p1, Figure)
    assert isinstance(p2, Figure)

    range_tool = row.select_one({'type': RangeTool})
    assert isinstance(range_tool, RangeTool)
    range_tool.x_range = p2.x_range
