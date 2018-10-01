from __future__ import absolute_import

from base64 import b64decode
import pytest

import param
from bokeh.models import (Div, Row as BkRow, WidgetBox as BkWidgetBox,
                          GlyphRenderer, Circle, Line)
from bokeh.plotting import Figure
from panel.pane import (Pane, PaneBase, Bokeh, HoloViews, Matplotlib,
                        HTML, Str, PNG, JPG, GIF)

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
