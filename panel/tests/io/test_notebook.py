import pytest

pytest.importorskip("IPython")

from bokeh.models import ImportedStyleSheet, InlineStyleSheet

from panel.config import config, panel_extension
from panel.io import resources as resources_module
from panel.io.notebook import ipywidget, load_notebook, replace_inline_css
from panel.io.resource_spec import resource_spec
from panel.io.resources import (
    CDN_DIST, CDN_ROOT, JS_VERSION, set_resource_mode,
)
from panel.layout import Column
from panel.models.tabulator import DataTabulator
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


@pytest.fixture
def notebook_bootstrap():
    """
    Runs the notebook bootstrap, undoing the global state it sets.
    """
    from bokeh.io.state import curstate
    state, mode = curstate(), resources_module.RESOURCE_MODE
    notebook, notebook_type = state.notebook, state.notebook_type
    try:
        load_notebook(inline=True)
        yield
    finally:
        resources_module.RESOURCE_MODE = mode
        state._notebook, state._notebook_type = notebook, notebook_type


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


def test_notebook_resources_resolve_absolutely(notebook_bootstrap):
    """
    A component rendered in a later cell builds its specification outside
    any resource mode block, and the notebook page cannot resolve a url
    into the static endpoint Panel serves for an application.
    """
    spec = resource_spec(DataTabulator)
    urls = [url for lib in spec['libs'] for url in lib['js']] + spec['css']

    assert urls
    assert all(url.startswith('http') for url in urls)


def test_notebook_dynamic_component_resources_resolve_absolutely(
    nb_loaded, notebook_bootstrap
):
    column = Column()
    column._repr_mimebundle_()
    editor = TextEditor()
    column.append(editor)

    (model, _) = list(editor._models.values())[0]
    urls = [url for lib in model.external_resources['libs'] for url in lib['js']]

    assert urls
    assert all(url.startswith('http') for url in urls)


def test_replace_inline_css_ignores_version_query():
    url = f'{CDN_DIST}css/loading.css'
    unversioned = replace_inline_css(ImportedStyleSheet(url=url))
    versioned = replace_inline_css(ImportedStyleSheet(url=f'{url}?v={JS_VERSION}'))

    assert isinstance(unversioned, InlineStyleSheet)
    assert isinstance(versioned, InlineStyleSheet)
    assert versioned.css == unversioned.css
