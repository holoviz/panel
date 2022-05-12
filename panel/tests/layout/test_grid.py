import pytest

from bokeh.models import Div

from panel.depends import depends
from panel.layout import GridBox, GridSpec, Spacer
from panel.widgets import IntSlider


def test_gridspec_cleanup(document, comm):
    spacer = Spacer()
    gspec = GridSpec()
    gspec[0, 0] = spacer

    model = gspec.get_root(document, comm)

    ref = model.ref['id']
    assert ref in gspec._models
    assert ref in spacer._models

    gspec._cleanup(model)
    assert ref not in gspec._models
    assert ref not in spacer._models


def test_gridspec_integer_setitem():
    div = Div()
    gspec = GridSpec()
    gspec[0, 0] = div

    assert list(gspec.objects) == [(0, 0, 1, 1)]


def test_gridspec_clone():
    div = Div()
    gspec = GridSpec()
    gspec[0, 0] = div
    clone = gspec.clone()

    assert gspec.objects == clone.objects
    assert gspec.param.values() == clone.param.values()


def test_gridspec_slice_setitem():
    div = Div()
    gspec = GridSpec()
    gspec[0, :] = div

    assert list(gspec.objects) == [(0, None, 1, None)]


def test_gridspec_setitem_int_overlap():
    div = Div()
    gspec = GridSpec(mode='error')
    gspec[0, 0] = div
    with pytest.raises(IndexError):
        gspec[0, 0] = 'String'


def test_gridspec_setitem_slice_overlap():
    div = Div()
    gspec = GridSpec(mode='error')
    gspec[0, :] = div
    with pytest.raises(IndexError):
        gspec[0, 1] = div


def test_gridspec_setitem_cell_override():
    div = Div()
    div2 = Div()
    gspec = GridSpec()
    gspec[0, 0] = div
    gspec[0, 0] = div2
    assert (0, 0, 1, 1) in gspec.objects
    assert gspec.objects[(0, 0, 1, 1)].object is div2


def test_gridspec_setitem_span_override():
    div = Div()
    div2 = Div()
    gspec = GridSpec()
    gspec[0, :] = div
    gspec[0, 0] = div2
    assert (0, 0, 1, 1) in gspec.objects
    assert gspec.objects[(0, 0, 1, 1)].object is div2


def test_gridspec_fixed_with_int_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    gspec = GridSpec(width=800, height=500)

    gspec[0, 0] = div1
    gspec[1, 1] = div2

    model = gspec.get_root(document, comm=comm)
    assert model.children == [(div1, 0, 0, 1, 1), (div2, 1, 1, 1, 1)]
    assert div1.width == 400
    assert div1.height == 250
    assert div2.width == 400
    assert div2.height == 250


def test_gridspec_fixed_with_slice_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    gspec = GridSpec(width=900, height=500)

    gspec[0, 0:2] = div1
    gspec[1, 2] = div2

    model = gspec.get_root(document, comm=comm)
    assert model.children == [(div1, 0, 0, 1, 2), (div2, 1, 2, 1, 1)]
    assert div1.width == 600
    assert div1.height == 250
    assert div2.width == 300
    assert div2.height == 250


def test_gridspec_fixed_with_upper_partial_slice_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    gspec = GridSpec(width=900, height=500)

    gspec[0, :2] = div1
    gspec[1, 2] = div2

    model = gspec.get_root(document, comm=comm)
    assert model.children == [(div1, 0, 0, 1, 2), (div2, 1, 2, 1, 1)]
    assert div1.width == 600
    assert div1.height == 250
    assert div2.width == 300
    assert div2.height == 250


def test_gridspec_fixed_with_lower_partial_slice_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    gspec = GridSpec(width=900, height=500)

    gspec[0, 1:] = div1
    gspec[1, 2] = div2

    model = gspec.get_root(document, comm=comm)
    assert model.children == [(div1, 0, 1, 1, 2), (div2, 1, 2, 1, 1)]
    assert div1.width == 600
    assert div1.height == 250
    assert div2.width == 300
    assert div2.height == 250


def test_gridspec_fixed_with_empty_slice_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    gspec = GridSpec(width=900, height=500)

    gspec[0, :] = div1
    gspec[1, 2] = div2

    model = gspec.get_root(document, comm=comm)
    assert model.children == [(div1, 0, 0, 1, 3), (div2, 1, 2, 1, 1)]
    assert div1.width == 900
    assert div1.height == 250
    assert div2.width == 300
    assert div2.height == 250


def test_gridspec_stretch_with_int_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    gspec = GridSpec(sizing_mode='stretch_both')

    gspec[0, 0] = div1
    gspec[1, 1] = div2

    model = gspec.get_root(document, comm=comm)
    assert model.children == [(div1, 0, 0, 1, 1), (div2, 1, 1, 1, 1)]
    assert div1.sizing_mode == 'stretch_both'
    assert div2.sizing_mode == 'stretch_both'


def test_gridspec_stretch_with_slice_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    gspec = GridSpec(sizing_mode='stretch_both')

    gspec[0, 0:2] = div1
    gspec[1, 2] = div2

    model = gspec.get_root(document, comm=comm)
    assert model.children == [(div1, 0, 0, 1, 2), (div2, 1, 2, 1, 1)]
    assert div1.sizing_mode == 'stretch_both'
    assert div2.sizing_mode == 'stretch_both'


def test_gridspec_fixed_with_replacement_pane(document, comm):
    slider = IntSlider(start=0, end=2)

    @depends(slider)
    def div(value):
        return Div(text=str(value))

    gspec = GridSpec()

    gspec[0, 0:2] = Div()
    gspec[1, 2] = div

    model = gspec.get_root(document, comm=comm)
    ((div1, _, _, _, _), (row, _, _, _, _)) = model.children
    div2 = row.children[0]
    assert div1.width == 400
    assert div1.height == 300
    assert div2.width == 200
    assert div2.height == 300

    slider.value = 1
    assert row.children[0] is not div2
    assert row.children[0].width == 200
    assert row.children[0].height == 300


def test_gridspec_stretch_with_replacement_pane(document, comm):
    slider = IntSlider(start=0, end=2)

    @depends(slider)
    def div(value):
        return Div(text=str(value))

    gspec = GridSpec(sizing_mode='stretch_width')

    gspec[0, 0:2] = Div()
    gspec[1, 2] = div

    model = gspec.get_root(document, comm=comm)
    ((div1, _, _, _, _), (row, _, _, _, _)) = model.children
    div2 = row.children[0]
    assert div1.sizing_mode == 'stretch_width'
    assert div1.height == 300
    assert div2.sizing_mode == 'stretch_width'
    assert div2.height == 300

    slider.value = 1
    assert row.children[0] is not div2
    assert row.children[0].sizing_mode == 'stretch_width'
    assert row.children[0].height == 300



def test_gridbox_ncols(document, comm):
    grid_box = GridBox(Div(), Div(), Div(), Div(), Div(), Div(), Div(), Div(), ncols=3)

    model = grid_box.get_root(document, comm=comm)

    assert len(model.children) == 8
    coords = [
        (0, 0, 1, 1), (0, 1, 1, 1), (0, 2, 1, 1),
        (1, 0, 1, 1), (1, 1, 1, 1), (1, 2, 1, 1),
        (2, 0, 1, 1), (2, 1, 1, 1)
    ]
    for child, coord in zip(model.children, coords):
        assert child[1:] == coord


def test_gridbox_nrows(document, comm):
    grid_box = GridBox(Div(), Div(), Div(), Div(), Div(), Div(), Div(), Div(), nrows=2)

    model = grid_box.get_root(document, comm=comm)

    assert len(model.children) == 8

    coords = [
        (0, 0, 1, 1), (0, 1, 1, 1), (0, 2, 1, 1), (0, 3, 1, 1),
        (1, 0, 1, 1), (1, 1, 1, 1), (1, 2, 1, 1), (1, 3, 1, 1)
    ]
    for child, coord in zip(model.children, coords):
        assert child[1:] == coord


def test_gridspec_fixed_ncols():
    grid = GridSpec(ncols=3)
    for index in range(5):
        grid[index, :] = "Hello World"


def test_gridspec_fixed_nrows():
    grid = GridSpec(nrows=3)
    for index in range(5):
        grid[:, index] = "Hello World"
