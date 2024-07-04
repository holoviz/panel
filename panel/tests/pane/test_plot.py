from bokeh.models import Div, Row as BkRow

import panel as pn

from panel.pane import Bokeh, Matplotlib, PaneBase
from panel.tests.util import mpl_available, mpl_figure


def test_get_bokeh_pane_type():
    div = Div()
    assert PaneBase.get_pane_type(div) is Bokeh


def test_bokeh_pane(document, comm):
    div = Div()
    pane = pn.panel(div)

    # Create pane
    row = pane.get_root(document, comm=comm)
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


@mpl_available
def test_get_matplotlib_pane_type():
    assert PaneBase.get_pane_type(mpl_figure()) is Matplotlib


@mpl_available
def test_matplotlib_pane_initially_empty(document, comm):
    pane = pn.pane.Matplotlib()
    assert pane.object is None

    model = pane.get_root(document, comm=comm)
    assert model.text == '<img></img>'

    pane.object = mpl_figure()
    assert model.text.startswith('&lt;img src=&quot;data:image/png;base64,')
    assert pane._models[model.ref['id']][0] is model


@mpl_available
def test_matplotlib_pane(document, comm):
    pane = pn.pane.Matplotlib(mpl_figure())

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert model.text.startswith('&lt;img src=&quot;data:image/png;base64,')
    text = model.text
    assert pane._models[model.ref['id']][0] is model

    # Replace Pane.object
    pane.object = mpl_figure()
    assert model.text != text
    assert pane._models[model.ref['id']][0] is model

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@mpl_available
def test_matplotlib_pane_svg_render(document, comm):
    pane = pn.pane.Matplotlib(mpl_figure(), format='svg', encode=True)
    model = pane.get_root(document, comm=comm)
    assert model.text.startswith('&lt;img src=&quot;data:image/svg+xml;base64,')

@mpl_available
def test_matplotlib_pane_svg_render_responsive(document, comm):
    pane = pn.pane.Matplotlib(mpl_figure(), format='svg', encode=False)
    model = pane.get_root(document, comm=comm)
    # We should only replace width and height once
    assert model.text.count('width=&quot;100%&quot;')==1
    assert model.text.count('height=&quot;100%&quot;')==1

@mpl_available
def test_matplotlib_pane_svg_render_not_fixed_aspect(document, comm):
    pane = pn.pane.Matplotlib(mpl_figure(), format='svg', encode=False, fixed_aspect=False)
    model = pane.get_root(document, comm=comm)
    assert model.text.count('width=&quot;100%&quot;')==1
    assert model.text.count('height=&quot;100%&quot;')==1
    assert model.text.count('preserveAspectRatio=&quot;none&quot;')==1
