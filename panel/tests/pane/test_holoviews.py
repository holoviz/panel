import datetime as dt
import warnings

import numpy as np
import pytest

try:
    import holoviews as hv
except Exception:
    hv = None

try:
    import holoviews.plotting.plotly as hv_plotly
except Exception:
    hv_plotly = None
plotly_available = pytest.mark.skipif(hv_plotly is None, reason="requires plotly backend")

from bokeh.models import (
    Column as BkColumn, ColumnDataSource, GlyphRenderer, GridPlot, Line,
    Row as BkRow, Scatter, Select as BkSelect, Slider as BkSlider,
    Spacer as BkSpacer,
)
from bokeh.plotting import figure

import panel as pn

from panel.depends import bind
from panel.layout import (
    Column, FlexBox, HSpacer, Row,
)
from panel.pane import HoloViews, PaneBase, panel
from panel.tests.util import hv_available, mpl_available
from panel.theme import Native
from panel.util.warnings import PanelDeprecationWarning
from panel.widgets import (
    Checkbox, DiscreteSlider, FloatSlider, Select,
)


@hv_available
def test_get_holoviews_pane_type():
    curve = hv.Curve([1, 2, 3])
    assert PaneBase.get_pane_type(curve) is HoloViews


@pytest.mark.usefixtures("hv_mpl")
@mpl_available
@hv_available
def test_holoviews_pane_mpl_renderer(document, comm):
    curve = hv.Curve([1, 2, 3])
    pane = pn.panel(curve)

    # Create pane
    row = pane.get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert pane._models[row.ref['id']][0] is model
    assert model.text.startswith('&lt;img src=')

    # Replace Pane.object
    scatter = hv.Scatter([1, 2, 3])
    pane.object = scatter
    new_model = row.children[0]
    assert model.text != new_model.text

    # Cleanup
    pane._cleanup(row)
    assert pane._models == {}


@pytest.mark.usefixtures("hv_mpl")
@pytest.mark.usefixtures("hv_bokeh")
@mpl_available
@hv_available
def test_holoviews_pane_switch_backend(document, comm):
    curve = hv.Curve([1, 2, 3])
    pane = pn.panel(curve)

    # Create pane
    row = pane.get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert pane._models[row.ref['id']][0] is model
    assert model.text.startswith('&lt;img src=')

    # Replace Pane.object
    pane.backend = 'bokeh'
    model = row.children[0]
    assert isinstance(model, figure)

    # Cleanup
    pane._cleanup(row)
    assert pane._models == {}


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_pane_bokeh_renderer(document, comm):
    curve = hv.Curve([1, 2, 3])
    pane = pn.panel(curve)

    # Create pane
    row = pane.get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert isinstance(model, figure)
    assert pane._models[row.ref['id']][0] is model
    renderers = [r for r in model.renderers if isinstance(r, GlyphRenderer)]
    assert len(renderers) == 1
    assert isinstance(renderers[0].glyph, Line)

    # Replace Pane.object
    scatter = hv.Scatter([1, 2, 3])
    pane.object = scatter
    model = row.children[0]
    assert isinstance(model, figure)
    renderers = [r for r in model.renderers if isinstance(r, GlyphRenderer)]
    assert len(renderers) == 1
    assert isinstance(renderers[0].glyph, Scatter)
    assert pane._models[row.ref['id']][0] is model

    # Cleanup
    pane._cleanup(row)
    assert pane._models == {}

@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_pane_initialize_empty(document, comm):
    pane = HoloViews()

    # Create pane
    row = pane.get_root(document, comm=comm)

    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert isinstance(model, BkSpacer)

    pane.object = hv.Curve([1, 2, 3])
    model = row.children[0]
    assert isinstance(model, figure)

@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_pane_reflect_responsive(document, comm):
    curve = hv.Curve([1, 2, 3]).opts(responsive=True)
    pane = HoloViews(curve)

    # Create pane
    row = pane.get_root(document, comm=comm)

    assert row.sizing_mode == 'stretch_both'
    assert pane.sizing_mode == 'stretch_both'

    pane.object = hv.Curve([1, 2, 3])

    assert row.sizing_mode is None
    assert pane.sizing_mode == 'fixed'

@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_pane_reflect_responsive_override(document, comm):
    curve = hv.Curve([1, 2, 3]).opts(responsive=True)
    pane = HoloViews(curve, sizing_mode='fixed')

    # Create pane
    row = pane.get_root(document, comm=comm)

    assert row.sizing_mode == 'stretch_both'
    assert pane.sizing_mode == 'fixed'

    # Unset override
    pane.sizing_mode = None

    row = pane.get_root(document, comm=comm)

    assert row.sizing_mode == 'stretch_both'
    assert pane.sizing_mode == 'stretch_both'

@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_pane_reflect_responsive_interact_function(document, comm):
    curve_fn = lambda: hv.Curve([1, 2, 3]).opts(responsive=True)
    pane = panel(curve_fn)

    # Create pane
    row = pane.get_root(document, comm=comm)

    assert row.sizing_mode == 'stretch_both'

@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_pane_reflect_responsive_bind_function(document, comm):
    checkbox = Checkbox(value=True)
    curve_fn = lambda responsive: hv.Curve([1, 2, 3]).opts(responsive=responsive)
    pane = panel(bind(curve_fn, responsive=checkbox))

    # Create pane
    col = pane.get_root(document, comm=comm)

    assert col.sizing_mode == 'stretch_both'

    checkbox.value = False

    assert col.sizing_mode == 'fixed'

@pytest.mark.usefixtures("hv_plotly")
@hv_available
@plotly_available
def test_holoviews_pane_reflect_responsive_plotly(document, comm):
    curve = hv.Curve([1, 2, 3]).opts(responsive=True, backend='plotly')
    pane = HoloViews(curve, backend='plotly')

    # Create pane
    row = pane.get_root(document, comm=comm)

    assert row.sizing_mode == 'stretch_both'
    assert pane.sizing_mode == 'stretch_both'

    pane.object = hv.Curve([1, 2, 3])

    assert row.sizing_mode is None
    assert pane.sizing_mode is None


@pytest.mark.usefixtures("hv_plotly")
@hv_available
@plotly_available
def test_holoviews_pane_inherits_design_stylesheets(document, comm):
    curve = hv.Curve([1, 2, 3]).opts(responsive=True, backend='plotly')
    pane = HoloViews(curve, backend='plotly')

    # Create pane
    row = pane.get_root(document, comm=comm)

    Native().apply(pane, row)

    plotly_model = row.children[0]

    assert len(plotly_model.stylesheets) == 6

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
    assert widgets[3].options == value_dim.values
    assert widgets[3].value == value_dim.values[0]

    assert isinstance(widgets[4], Select)
    assert widgets[4].name == 'E'
    assert widgets[4].options == value_default_dim.values
    assert widgets[4].value == value_default_dim.default

    assert isinstance(widgets[5], DiscreteSlider)
    assert widgets[5].name == 'F'
    assert widgets[5].options == {str(v): v for v in value_numeric_dim.values}
    assert widgets[5].value == value_numeric_dim.default


@hv_available
def test_holoviews_with_widgets(document, comm):
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    hv_pane = HoloViews(hmap)
    layout = hv_pane.get_root(document, comm)
    model = layout.children[0]
    assert len(hv_pane.widget_box.objects) == 2
    assert hv_pane.widget_box.objects[0].name == 'X'
    assert hv_pane.widget_box.objects[1].name == 'Y'

    assert hv_pane._models[layout.ref['id']][0] is model

    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['A', 'B'])
    hv_pane.object = hmap
    assert len(hv_pane.widget_box.objects) == 2
    assert hv_pane.widget_box.objects[0].name == 'A'
    assert hv_pane.widget_box.objects[1].name == 'B'


@hv_available
def test_holoviews_updates_widgets(document, comm):
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    hv_pane = HoloViews(hmap)
    layout = hv_pane.get_root(document, comm)

    hv_pane.widgets = {'X': Select}
    assert isinstance(hv_pane.widget_box[0], Select)
    assert isinstance(layout.children[1].children[1], BkSelect)

    hv_pane.widgets = {'X': DiscreteSlider}
    assert isinstance(hv_pane.widget_box[0], DiscreteSlider)
    assert isinstance(layout.children[1].children[0], BkColumn)
    assert isinstance(layout.children[1].children[0].children[1], BkSlider)


@hv_available
def test_holoviews_widgets_update_plot(document, comm):
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    hv_pane = HoloViews(hmap, backend='bokeh')
    layout = hv_pane.get_root(document, comm)

    cds = layout.children[0].select_one({'type': ColumnDataSource})
    assert cds.data['y'] == np.array([0])
    hv_pane.widget_box[0].value = 1
    hv_pane.widget_box[1].value = chr(65+1)
    assert cds.data['y'] == np.array([1])


@hv_available
def test_holoviews_dynamic_widgets_with_unit_updates_plot(document, comm):
    def function(f):
        return hv.Curve((x, np.sin(f*x)))

    x = np.linspace(0, 10)
    factor = hv.Dimension('factor', unit='m', values=[1, 2, 3, 4, 5])
    dmap = hv.DynamicMap(function, kdims=factor)
    hv_pane = HoloViews(dmap, backend='bokeh')
    layout = hv_pane.get_root(document, comm)

    cds = layout.children[0].select_one({'type': ColumnDataSource})
    np.testing.assert_array_equal(cds.data['y'], np.sin(x))
    hv_pane.widget_box[0].value = 3
    np.testing.assert_array_equal(cds.data['y'], np.sin(3*x))


@hv_available
def test_holoviews_with_widgets_not_shown(document, comm):
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    hv_pane = HoloViews(hmap)
    layout_obj = Column(hv_pane, hv_pane.widget_box)
    layout = layout_obj.get_root(document, comm)
    model = layout.children[0]
    assert len(hv_pane.widget_box.objects) == 2
    assert hv_pane.widget_box.objects[0].name == 'X'
    assert hv_pane.widget_box.objects[1].name == 'Y'

    assert hv_pane._models[layout.ref['id']][0] is model

    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['A', 'B'])
    hv_pane.object = hmap
    assert len(hv_pane.widget_box.objects) == 2
    assert hv_pane.widget_box.objects[0].name == 'A'
    assert hv_pane.widget_box.objects[1].name == 'B'


@hv_available
def test_holoviews_center(document, comm):
    hv_pane = HoloViews(hv.Curve([1, 2, 3]), backend='bokeh', center=True)

    layout = hv_pane.layout

    assert len(layout) == 3
    hspacer1, hv_out, hspacer2 = layout
    assert isinstance(hspacer1, HSpacer)
    assert hv_pane is hv_out
    assert isinstance(hspacer2, HSpacer)

@hv_available
def test_holoviews_layouts(document, comm):
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    hv_pane = HoloViews(hmap, backend='bokeh')
    layout = hv_pane.layout
    model = layout.get_root(document, comm)

    for center in (True, False):
        for loc in HoloViews.param.widget_location.objects:
            hv_pane.param.update(center=center, widget_location=loc)
            if center:
                if loc.startswith('left'):
                    assert len(layout) == 4
                    widgets, hv_obj = layout[0], layout[2]
                    wmodel, hv_model = model.children[0],  model.children[2]
                elif loc.startswith('right'):
                    assert len(layout) == 4
                    hv_obj, widgets = layout[1], layout[3]
                    wmodel, hv_model = model.children[3],  model.children[1]
                elif loc.startswith('top'):
                    assert len(layout) == 3
                    col = layout[1]
                    cmodel = model.children[1]
                    assert isinstance(col, Column)
                    widgets, hv_obj = col
                    wmodel, hv_model = cmodel.children[0],  cmodel.children[1]
                elif loc.startswith('bottom'):
                    col = layout[1]
                    cmodel = model.children[1]
                    assert isinstance(col, Column)
                    hv_obj, widgets = col
                    wmodel, hv_model = cmodel.children[1],  cmodel.children[0]
            else:
                if loc.startswith('left'):
                    assert len(layout) == 2
                    widgets, hv_obj = layout
                    wmodel, hv_model = model.children
                elif loc.startswith('right'):
                    assert len(layout) == 2
                    hv_obj, widgets = layout
                    hv_model, wmodel = model.children
                elif loc.startswith('top'):
                    assert len(layout) == 1
                    col = layout[0]
                    cmodel = model.children[0]
                    assert isinstance(col, Column)
                    widgets, hv_obj = col
                    wmodel, hv_model = cmodel.children
                elif loc.startswith('bottom'):
                    assert len(layout) == 1
                    col = layout[0]
                    cmodel = model.children[0]
                    assert isinstance(col, Column)
                    hv_obj, widgets = col
                    hv_model, wmodel = cmodel.children
            assert hv_pane is hv_obj
            assert isinstance(hv_model, figure)

            box = widgets
            boxmodel = wmodel
            assert hv_pane.widget_box is box
            assert isinstance(boxmodel, BkColumn)
            assert isinstance(boxmodel.children[0], BkColumn)
            assert isinstance(boxmodel.children[0].children[1], BkSlider)
            assert isinstance(boxmodel.children[1], BkSelect)


@hv_available
def test_holoviews_widgets_from_holomap():
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    widgets, _ = HoloViews.widgets_from_dimensions(hmap)

    assert isinstance(widgets[0], DiscreteSlider)
    assert widgets[0].name == 'X'
    assert widgets[0].options == {str(i): i for i in range(3)}
    assert widgets[0].value == 0

    assert isinstance(widgets[1], Select)
    assert widgets[1].name == 'Y'
    assert widgets[1].options == ['A', 'B', 'C']
    assert widgets[1].value == 'A'


@hv_available
def test_holoviews_date_slider_widgets_from_holomap():
    hmap = hv.HoloMap({dt.datetime(2016, 1, i+1): hv.Curve([i]) for i in range(3)}, kdims=['X'])

    widgets, _ = HoloViews.widgets_from_dimensions(hmap)

    assert isinstance(widgets[0], DiscreteSlider)
    assert widgets[0].name == 'X'
    assert widgets[0].options == {
        '2016-01-01 00:00:00': dt.datetime(2016, 1, 1),
        '2016-01-02 00:00:00': dt.datetime(2016, 1, 2),
        '2016-01-03 00:00:00': dt.datetime(2016, 1, 3),
    }
    assert widgets[0].value == dt.datetime(2016, 1, 1)


@hv_available
def test_holoviews_widgets_explicit_widget_type_override():
    hmap = hv.HoloMap({(i, chr(65+i)): hv.Curve([i]) for i in range(3)}, kdims=['X', 'Y'])

    widgets, _ = HoloViews.widgets_from_dimensions(hmap, widget_types={'X': Select})

    assert isinstance(widgets[0], Select)
    assert widgets[0].name == 'X'
    assert widgets[0].options == {str(i): i for i in range(3)}
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


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_linked_axes(document, comm):
    c1 = hv.Curve([1, 2, 3])
    c2 = hv.Curve([1, 2, 3])

    layout = Row(HoloViews(c1, backend='bokeh'), HoloViews(c2, backend='bokeh'))

    row_model = layout.get_root(document, comm=comm)

    p1, p2 = row_model.select({'type': figure})

    assert p1.x_range is p2.x_range
    assert p1.y_range is p2.y_range


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_linked_axes_flexbox(document, comm):
    c1 = hv.Curve([1, 2, 3])
    c2 = hv.Curve([1, 2, 3])

    layout = FlexBox(HoloViews(c1, backend='bokeh'), HoloViews(c2, backend='bokeh'))

    row_model = layout.get_root(document, comm=comm)

    p1, p2 = row_model.select({'type': figure})

    assert p1.x_range is p2.x_range
    assert p1.y_range is p2.y_range


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_linked_axes_merged_ranges(document, comm):
    c1 = hv.Curve([1, 2, 3])
    c2 = hv.Curve([0, 1, 2, 3, 4])

    layout = Row(HoloViews(c1, backend='bokeh'), HoloViews(c2, backend='bokeh'))

    row_model = layout.get_root(document, comm=comm)

    p1, p2 = row_model.select({'type': figure})

    assert p1.x_range is p2.x_range
    assert p1.y_range is p2.y_range
    assert p1.y_range.start == -0.4
    assert p1.y_range.end == 4.4


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_linked_x_axis(document, comm):
    c1 = hv.Curve([1, 2, 3])
    c2 = hv.Curve([1, 2, 3], vdims='y2')

    layout = Row(HoloViews(c1, backend='bokeh'), HoloViews(c2, backend='bokeh'))

    row_model = layout.get_root(document, comm=comm)

    p1, p2 = row_model.select({'type': figure})

    assert p1.x_range is p2.x_range
    assert p1.y_range is not p2.y_range


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_axiswise_not_linked_axes(document, comm):
    c1 = hv.Curve([1, 2, 3])
    c2 = hv.Curve([1, 2, 3]).opts(axiswise=True, backend='bokeh')

    layout = Row(HoloViews(c1, backend='bokeh'), HoloViews(c2, backend='bokeh'))

    row_model = layout.get_root(document, comm=comm)

    p1, p2 = row_model.select({'type': figure})

    assert p1.x_range is not p2.x_range
    assert p1.y_range is not p2.y_range


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_shared_axes_opt_not_linked_axes(document, comm):
    c1 = hv.Curve([1, 2, 3])
    c2 = hv.Curve([1, 2, 3]).opts(shared_axes=False, backend='bokeh')

    layout = Row(HoloViews(c1, backend='bokeh'), HoloViews(c2, backend='bokeh'))

    row_model = layout.get_root(document, comm=comm)

    p1, p2 = row_model.select({'type': figure})

    assert p1.x_range is not p2.x_range
    assert p1.y_range is not p2.y_range


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_not_linked_axes(document, comm):
    c1 = hv.Curve([1, 2, 3])
    c2 = hv.Curve([1, 2, 3])

    layout = Row(
        HoloViews(c1, backend='bokeh'),
        HoloViews(c2, backend='bokeh', linked_axes=False)
    )

    row_model = layout.get_root(document, comm=comm)

    p1, p2 = row_model.select({'type': figure})

    assert p1.x_range is not p2.x_range
    assert p1.y_range is not p2.y_range


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_link_across_panes(document, comm):
    from bokeh.models.tools import RangeTool
    from holoviews.plotting.links import RangeToolLink

    c1 = hv.Curve([])
    c2 = hv.Curve([])

    RangeToolLink(c1, c2)

    layout = Row(pn.panel(c1, backend='bokeh'), pn.panel(c2, backend='bokeh'))
    row = layout.get_root(document, comm=comm)

    assert len(row.children) == 2
    p1, p2 = row.children

    assert isinstance(p1, figure)
    assert isinstance(p2, figure)

    range_tool = row.select_one({'type': RangeTool})
    assert isinstance(range_tool, RangeTool)
    assert range_tool.x_range == p2.x_range


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_link_after_adding_item(document, comm):
    from bokeh.models.tools import RangeTool
    from holoviews.plotting.links import RangeToolLink

    c1 = hv.Curve([])
    c2 = hv.Curve([])

    RangeToolLink(c1, c2)

    layout = Row(pn.panel(c1, backend='bokeh'))
    row = layout.get_root(document, comm=comm)

    assert len(row.children) == 1
    p1, = row.children

    assert isinstance(p1, figure)
    range_tool = row.select_one({'type': RangeTool})
    assert range_tool is None

    layout.append(pn.panel(c2, backend='bokeh'))
    _, p2 = row.children
    assert isinstance(p2, figure)
    range_tool = row.select_one({'type': RangeTool})
    assert isinstance(range_tool, RangeTool)
    assert range_tool.x_range == p2.x_range


@pytest.mark.usefixtures("hv_bokeh")
@hv_available
def test_holoviews_link_within_pane(document, comm):
    from bokeh.models.tools import RangeTool
    from holoviews.plotting.links import RangeToolLink

    c1 = hv.Curve([])
    c2 = hv.Curve([])

    RangeToolLink(c1, c2)

    pane = pn.panel(pn.panel(hv.Layout([c1, c2]), backend='bokeh'))
    column = pane.get_root(document, comm=comm)

    assert len(column.children) == 1
    grid_plot = column.children[0]
    assert isinstance(grid_plot, GridPlot)
    assert len(grid_plot.children) == 2
    (p1, _, _), (p2, _, _) = grid_plot.children

    assert isinstance(p1, figure)
    assert isinstance(p2, figure)

    range_tool = grid_plot.select_one({'type': RangeTool})
    assert isinstance(range_tool, RangeTool)
    assert range_tool.x_range == p2.x_range


@hv_available
def test_holoviews_property_override_old_method(document, comm):
    c1 = hv.Curve([])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PanelDeprecationWarning)
        pane = pn.panel(c1, backend='bokeh', css_classes=['test_class'])
    model = pane.get_root(document, comm=comm)

    assert model.children[0].css_classes == ['test_class']

@hv_available
def test_holoviews_property_override(document, comm):
    c1 = hv.Curve([])

    pane = pn.panel(c1, backend='bokeh',
                styles={'background': 'red'},
                css_classes=['test_class'])
    model = pane.get_root(document, comm=comm)

    assert model.styles["background"] == 'red'
    assert model.children[0].css_classes == ['test_class']


@hv_available
def test_holoviews_date_picker_widget(document, comm):
    ds = {
        "time": [np.datetime64("2000-01-01"), np.datetime64("2000-01-02")],
        "x": [0, 1],
        "y": [0, 1],
    }
    viz = hv.Dataset(ds, ["x", "time"], ["y"])
    layout = pn.panel(viz.to(
        hv.Scatter, ["x"], ["y"]), widgets={"time": pn.widgets.DatePicker}
    )
    widget_box = layout[0][1]
    assert isinstance(layout, pn.Row)
    assert isinstance(widget_box, pn.WidgetBox)
    assert isinstance(widget_box[0], pn.widgets.DatePicker)


@hv_available
def test_holoviews_datetime_picker_widget(document, comm):
    ds = {
        "time": [np.datetime64("2000-01-01"), np.datetime64("2000-01-02")],
        "x": [0, 1],
        "y": [0, 1],
    }
    viz = hv.Dataset(ds, ["x", "time"], ["y"])
    layout = pn.panel(viz.to(
        hv.Scatter, ["x"], ["y"]), widgets={"time": pn.widgets.DatetimePicker}
    )
    widget_box = layout[0][1]
    assert isinstance(layout, pn.Row)
    assert isinstance(widget_box, pn.WidgetBox)
    assert isinstance(widget_box[0], pn.widgets.DatetimePicker)
