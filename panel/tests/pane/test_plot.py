from bokeh.models import Div, Row as BkRow

import panel as pn

from panel.pane import (
    PNG, Bokeh, Matplotlib, PaneBase,
)
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



@mpl_available
def test_matplotlib_pane_high_dpi_png_rendered_at_twice_dpi(document, comm):
    fig = mpl_figure()
    hidpi = pn.pane.Matplotlib(fig, dpi=144)
    lodpi = pn.pane.Matplotlib(fig, dpi=144, high_dpi=False)
    hidpi_width, _ = PNG._imgshape(hidpi._data(fig))
    lodpi_width, _ = PNG._imgshape(lodpi._data(fig))
    assert abs(hidpi_width - 2 * lodpi_width) <= 1


@mpl_available
def test_matplotlib_pane_high_dpi_png_displayed_at_dpi_size(document, comm):
    fig = mpl_figure()
    hidpi = pn.pane.Matplotlib(fig, dpi=144).get_root(document, comm=comm)
    lodpi = pn.pane.Matplotlib(fig, dpi=144, high_dpi=False).get_root(document, comm=comm)
    assert (hidpi.width, hidpi.height) == (lodpi.width, lodpi.height)


@mpl_available
def test_matplotlib_pane_high_dpi_disabled(document, comm):
    pane = pn.pane.Matplotlib(mpl_figure(), dpi=144, high_dpi=False)
    model = pane.get_root(document, comm=comm)
    assert (model.width, model.height) == PNG._imgshape(pane._data(pane.object))


@mpl_available
def test_matplotlib_pane_high_dpi_explicit_width(document, comm):
    pane = pn.pane.Matplotlib(mpl_figure(), dpi=144, width=300)
    model = pane.get_root(document, comm=comm)
    assert model.width == 300
