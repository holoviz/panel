from __future__ import absolute_import

import pytest

from bokeh.models import Div, Row as BkRow, Tabs as BkTabs, Column as BkColumn, Panel as BkPanel
from panel.layout import Column, Row, Tabs, Spacer
from panel.panes import Bokeh, Pane


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_constructor(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    assert all(isinstance(p, Bokeh) for p in layout.objects)


@pytest.mark.parametrize(['panel', 'model_type'], [(Column, BkColumn), (Row, BkRow)])
def test_layout_get_model(panel, model_type, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_model(document, comm=comm)

    assert isinstance(model, model_type)
    assert model.children == [div1, div2]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_append(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_model(document, comm=comm)

    div3 = Div()
    layout.append(div3)
    assert model.children == [div1, div2, div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_insert(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_model(document, comm=comm)

    div3 = Div()
    layout.insert(1, div3)
    assert model.children == [div1, div3, div2]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_model(document, comm=comm)

    assert div1.ref['id'] in p1._callbacks
    div3 = Div()
    layout[0] = div3
    assert model.children == [div3, div2]
    assert p1._callbacks == {}


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_pop(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_model(document, comm=comm)

    assert div1.ref['id'] in p1._callbacks
    layout.pop(0)
    assert model.children == [div2]
    assert p1._callbacks == {}


def test_tabs_constructor(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(('Div1', div1), ('Div2', div2))
    p1, p2 = tabs.objects

    model = tabs._get_model(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 2
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab1, tab2 = model.tabs

    assert tab1.title == 'Div1'
    assert tab1.child is div1
    assert tab2.title == 'Div2'
    assert tab2.child is div2


def test_tabs_implicit_constructor(document, comm):
    div1, div2 = Div(), Div()
    p1 = Pane(div1, name='Div1')
    p2 = Pane(div2, name='Div2')
    tabs = Tabs(p1, p2)

    model = tabs._get_model(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 2
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab1, tab2 = model.tabs

    assert tab1.title == 'Div1'
    assert tab1.child is div1
    assert tab2.title == 'Div2'
    assert tab2.child is div2


def test_tabs_set_panes(document, comm):
    div1, div2 = Div(), Div()
    p1 = Pane(div1, name='Div1')
    p2 = Pane(div2, name='Div2')
    tabs = Tabs(p1, p2)

    model = tabs._get_model(document, comm=comm)

    div3 = Div()
    p3 = Pane(div3, name='Div3')
    tabs.objects = [p1, p2, p3]

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 3
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab1, tab2, tab3 = model.tabs

    assert tab1.title == 'Div1'
    assert tab1.child is div1
    assert tab2.title == 'Div2'
    assert tab2.child is div2
    assert tab3.title == 'Div3'
    assert tab3.child is div3


def test_tabs_append(document, comm):
    div1, div2 = Div(), Div()
    p1 = Pane(div1, name='Div1')
    p2 = Pane(div2, name='Div2')
    tabs = Tabs(p1, p2)

    model = tabs._get_model(document, comm=comm)

    div3 = Div()
    tabs.append(div3)
    tab1, tab2, tab3 = model.tabs


def test_tabs_insert(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)

    model = tabs._get_model(document, comm=comm)

    div3 = Div()
    tabs.insert(1, div3)
    tab1, tab2, tab3 = model.tabs
    assert tab1.child is div1
    assert tab2.child is div3
    assert tab3.child is div2


def test_tabs_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    p1, p2 = tabs.objects

    model = tabs._get_model(document, comm=comm)

    assert div1.ref['id'] in p1._callbacks
    div3 = Div()
    tabs[0] = div3
    tab1, tab2 = model.tabs
    assert tab1.child is div3
    assert tab2.child is div2
    assert p1._callbacks == {}


def test_tabs_pop(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    p1, p2 = tabs.objects

    model = tabs._get_model(document, comm=comm)

    assert div1.ref['id'] in p1._callbacks
    tabs.pop(0)
    assert len(model.tabs) == 1
    tab1 = model.tabs[0]
    assert tab1.child is div2
    assert p1._callbacks == {}


def test_spacer(document, comm):

    spacer = Spacer(width=400, height=300)

    model = spacer._get_model(document, comm=comm)

    assert isinstance(model, spacer._bokeh_model)
    assert model.width == 400
    assert model.height == 300

    spacer.height = 400
    assert model.height == 400
