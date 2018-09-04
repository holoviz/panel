from __future__ import absolute_import

import pytest

try:
    import holoviews as hv
except:
    hv = None
hv_available = pytest.mark.skipif(hv is None, reason="requires holoviews")

try:
    import matplotlib as mpl
except:
    mpl = None
mpl_available = pytest.mark.skipif(mpl is None, reason="requires matplotlib")

from bokeh.models import (Div, Row as BkRow, WidgetBox as BkWidgetBox,
                          GlyphRenderer, Circle, Line)
from bokeh.plotting import Figure
from panel.panes import Pane, PaneBase, BokehPane, HoloViewsPane, MatplotlibPane

from .fixtures import mpl_figure


def test_get_bokeh_pane_type():
    div = Div()
    assert PaneBase.get_pane_type(div) is BokehPane


def test_bokeh_pane(document, comm):
    div = Div()
    pane = Pane(div)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    assert div.ref['id'] in pane._callbacks
    model = row.children[0]
    assert model is div

    # Replace Pane.object
    div2 = Div()
    pane.object = div2
    model = row.children[0]
    assert model is div2
    assert div2.ref['id'] in pane._callbacks
    assert div.ref['id'] not in pane._callbacks

    # Cleanup
    pane._cleanup(div2)
    assert pane._callbacks == {}


@hv_available
def test_get_holoviews_pane_type():
    curve = hv.Curve([1, 2, 3])
    assert PaneBase.get_pane_type(curve) is HoloViewsPane


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
    assert isinstance(model, BkRow)
    assert isinstance(model.children[0], BkWidgetBox)
    div = model.children[0].children[0]
    assert isinstance(div, Div)
    assert '<img' in div.text

    # Replace Pane.object
    scatter = hv.Scatter([1, 2, 3])
    pane.object = scatter
    model = row.children[0]
    assert isinstance(model, BkRow)
    assert isinstance(model.children[0], BkWidgetBox)
    div2 = model.children[0].children[0]
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


@mpl_available
def test_get_matplotlib_pane_type():
    assert PaneBase.get_pane_type(mpl_figure()) is MatplotlibPane


@mpl_available
def test_matplotlib_pane(document, comm):
    pane = Pane(mpl_figure())

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    assert len(pane._callbacks) == 1
    model = row.children[0]
    assert isinstance(model, BkRow)
    assert isinstance(model.children[0], BkWidgetBox)
    div = model.children[0].children[0]
    assert isinstance(div, Div)
    assert '<img' in div.text
    text = div.text

    # Replace Pane.object
    pane.object = mpl_figure()
    model = row.children[0]
    assert isinstance(model, BkRow)
    assert isinstance(model.children[0], BkWidgetBox)
    div2 = model.children[0].children[0]
    assert div is div2
    assert div.text != text

    # Cleanup
    pane._cleanup(model)
    assert pane._callbacks == {}
