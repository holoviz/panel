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
    assert model is div
    assert pane._models[row.ref['id']][0] is model

    # Replace Pane.object
    div2 = Div()
    pane.object = div2
    new_model = row.children[0]
    assert new_model is div2
    assert pane._models[row.ref['id']][0] is new_model

    # Cleanup
    pane._cleanup(row)
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
    model = pane._get_root(document, comm=comm)
    assert '<img' in model.text
    text = model.text
    assert pane._models[model.ref['id']][0] is model

    # Replace Pane.object
    pane.object = mpl_figure()
    assert model.text != text
    assert pane._models[model.ref['id']][0] is model

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@markdown_available
def test_get_markdown_pane_type():
    assert PaneBase.get_pane_type("**Markdown**") is Markdown


@markdown_available
def test_markdown_pane(document, comm):
    pane = Pane("**Markdown**")

    # Create pane
    model = pane._get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "<p><strong>Markdown</strong></p>"

    # Replace Pane.object
    pane.object = "*Markdown*"
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "<p><em>Markdown</em></p>"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


def test_html_pane(document, comm):
    pane = HTML("<h1>Test</h1>")

    # Create pane
    model = pane._get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "<h1>Test</h1>"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "<h2>Test</h2>"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@mpl_available
@pil_available
def test_latex_pane(document, comm):
    pane = LaTeX(r"$\frac{p^3}{q}$")

    # Create pane
    model = pane._get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    # Just checks for a PNG, not a specific rendering, to avoid
    # false alarms when formatting of the PNG changes
    assert model.text[0:32] == "<img src='data:image/png;base64,"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


def test_string_pane(document, comm):
    pane = Str("<h1>Test</h1>")

    # Create pane
    model = pane._get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "<pre>&lt;h1&gt;Test&lt;/h1&gt;</pre>"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "<pre>&lt;h2&gt;Test&lt;/h2&gt;</pre>"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


def test_svg_pane(document, comm):
    rect = """
    <svg xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="10" height="100" width="100"/>
    </svg>
    """
    pane = SVG(rect)

    # Create pane
    model = pane._get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('<img')
    assert b64encode(rect.encode('utf-8')).decode('utf-8') in model.text

    # Replace Pane.object
    circle = """
    <svg xmlns="http://www.w3.org/2000/svg" height="100">
      <circle cx="50" cy="50" r="40" />
    </svg>
    """
    pane.object = circle
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('<img')
    assert b64encode(circle.encode('utf-8')).decode('utf-8') in model.text

    # Cleanup
    pane._cleanup(model)
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
