import pytest

pytest.importorskip("IPython")

from bokeh.models import ImportedStyleSheet, InlineStyleSheet

from panel.config import config, panel_extension
from panel.io.notebook import ipywidget
from panel.io.resources import CDN_ROOT, set_resource_mode
from panel.pane import Str
from panel.widgets import TextEditor

from ..util import jb_available


@pytest.fixture
def nb_loaded():
    old = panel_extension._loaded
    panel_extension._loaded = True
    try:
        yield
    finally:
        panel_extension._loaded = old


@jb_available
def test_ipywidget(document):
    pane = Str('A')
    widget = ipywidget(pane, doc=document)

    assert widget._view_count == 0
    assert len(pane._models) == 1

    init_id = list(pane._models)[0]

    widget._view_count = 1

    assert widget._view_count == 1
    assert init_id in pane._models

    widget._view_count = 0

    assert len(pane._models) == 0

    widget._view_count = 1

    assert len(pane._models) == 1
    prev_id = list(pane._models)[0]

    widget.notify_change({'new': 1, 'old': 1, 'name': '_view_count',
                          'type': 'change', 'model': widget})
    assert prev_id in pane._models
    assert len(pane._models) == 1

    widget._view_count = 2

    assert prev_id in pane._models
    assert len(pane._models) == 1

def test_notebook_cdn_css_stylesheets(nb_loaded):
    widget = TextEditor()
    with config.set(inline=False):
        widget._repr_mimebundle_()
    with set_resource_mode('cdn'):
        stylesheets = widget._widget_type.__css__
    model = list(widget._models.values())[0][0]
    for stylesheet, url in zip(model.stylesheets, stylesheets):
        assert isinstance(stylesheet, ImportedStyleSheet)
        assert url.startswith(CDN_ROOT)
        assert stylesheet.url == url

def test_notebook_inline_css_stylesheets(nb_loaded):
    widget = TextEditor()
    with config.set(inline=True):
        widget._repr_mimebundle_()
    model = list(widget._models.values())[0][0]
    for stylesheet in model.stylesheets[:len(model.__css__)]:
        assert isinstance(stylesheet, InlineStyleSheet)
