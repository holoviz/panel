from __future__ import absolute_import

from base64 import b64decode, b64encode
import pytest

from bokeh.models import Div, Row as BkRow
from panel.pane import (Pane, PaneBase, Bokeh, Matplotlib, HTML, Str,
                        PNG, JPG, GIF, SVG, Markdown, LaTeX)

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

try:
    import PIL
except:
    PIL = None
pil_available = pytest.mark.skipif(PIL is None, reason="requires PIL")

try:
    import markdown
except:
    markdown = None
markdown_available = pytest.mark.skipif(markdown is None, reason="requires markdown")

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
    assert row.ref['id'] in pane._callbacks
    assert get_div(model) is div
    assert pane._models[row.ref['id']] is model

    # Replace Pane.object
    div2 = Div()
    pane.object = div2
    new_model = row.children[0]
    assert get_div(new_model) is div2
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is new_model

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}


def test_pane_repr(document, comm):
    pane = Pane('Some text', width=400)
    assert repr(pane) == 'Markdown(str, width=400)'


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
    assert row.ref['id'] in pane._callbacks
    model = row.children[0]
    div = get_div(model)
    assert '<img' in div.text
    text = div.text
    assert pane._models[row.ref['id']] is model

    # Replace Pane.object
    pane.object = mpl_figure()
    model = row.children[0]
    div2 = get_div(model)
    assert div is div2
    assert div.text != text
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}


@markdown_available
def test_get_markdown_pane_type():
    assert PaneBase.get_pane_type("**Markdown**") is Markdown


@markdown_available
def test_markdown_pane(document, comm):
    pane = Pane("**Markdown**")

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    div = get_div(model)
    assert div.text == "<p><strong>Markdown</strong></p>"

    # Replace Pane.object
    pane.object = "*Markdown*"
    model = row.children[0]
    assert div is get_div(model)
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    assert div.text == "<p><em>Markdown</em></p>"

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}


def test_html_pane(document, comm):
    pane = HTML("<h1>Test</h1>")

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    div = get_div(model)
    assert div.text == "<h1>Test</h1>"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    model = row.children[0]
    assert div is get_div(model)
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    assert div.text == "<h2>Test</h2>"

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}


@mpl_available
@pil_available
def test_latex_pane(document, comm):
    pane = LaTeX(r"$\frac{p^3}{q}$")

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    div = get_div(model)
    # Just checks for a PNG, not a specific rendering, to avoid
    # false alarms when formatting of the PNG changes
    assert div.text[0:37] == "<img src='data:image/png;base64,iVBOR"

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}


def test_string_pane(document, comm):
    pane = Str("<h1>Test</h1>")

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    div = get_div(model)
    assert div.text == "<pre>&lt;h1&gt;Test&lt;/h1&gt;</pre>"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    model = row.children[0]
    assert div is get_div(model)
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    assert div.text == "<pre>&lt;h2&gt;Test&lt;/h2&gt;</pre>"

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}


def test_svg_pane(document, comm):
    rect = """
    <svg xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="10" height="100" width="100"/>
    </svg>
    """
    pane = SVG(rect)

    # Create pane
    row = pane._get_root(document, comm=comm)
    assert isinstance(row, BkRow)
    assert len(row.children) == 1
    model = row.children[0]
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    div = get_div(model)
    assert div.text.startswith('<img')
    assert b64encode(rect.encode('utf-8')).decode('utf-8') in div.text

    # Replace Pane.object
    circle = """
    <svg xmlns="http://www.w3.org/2000/svg" height="100">
      <circle cx="50" cy="50" r="40" />
    </svg>
    """
    pane.object = circle
    model = row.children[0]
    assert div is get_div(model)
    assert row.ref['id'] in pane._callbacks
    assert pane._models[row.ref['id']] is model
    assert div.text.startswith('<img')
    assert b64encode(circle.encode('utf-8')).decode('utf-8') in div.text

    # Cleanup
    pane._cleanup(row)
    assert pane._callbacks == {}
    assert pane._models == {}


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
