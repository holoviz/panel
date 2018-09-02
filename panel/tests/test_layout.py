from bokeh.models import Div, Row as BkRow
from panel.layout import Row
from panel.panels import BokehPanel


def test_layout_constructor():
    div1 = Div()
    div2 = Div()
    row = Row(div1, div2)

    assert all(isinstance(p, BokehPanel) for p in row.panels)


def test_layout_get_model(document, comm):
    div1 = Div()
    div2 = Div()
    row = Row(div1, div2)

    model = row._get_model(document, comm=comm)

    assert isinstance(model, BkRow)
    assert model.children == [div1, div2]


def test_layout_append(document, comm):
    div1 = Div()
    div2 = Div()
    row = Row(div1, div2)

    model = row._get_model(document, comm=comm)

    div3 = Div()
    row.append(div3)
    assert model.children == [div1, div2, div3]


def test_layout_insert(document, comm):
    div1 = Div()
    div2 = Div()
    row = Row(div1, div2)

    model = row._get_model(document, comm=comm)

    div3 = Div()
    row.insert(1, div3)
    assert model.children == [div1, div3, div2]


def test_layout_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    row = Row(div1, div2)
    p1, p2 = row.panels

    model = row._get_model(document, comm=comm)

    assert div1.ref['id'] in p1._callbacks
    div3 = Div()
    row[0] = div3
    assert model.children == [div3, div2]
    assert p1._callbacks == {}


def test_layout_pop(document, comm):
    div1 = Div()
    div2 = Div()
    row = Row(div1, div2)
    p1, p2 = row.panels

    model = row._get_model(document, comm=comm)

    assert div1.ref['id'] in p1._callbacks
    row.pop(0)
    assert model.children == [div2]
    assert p1._callbacks == {}
