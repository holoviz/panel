from __future__ import absolute_import

import pytest

from bokeh.models import (Div, Row as BkRow, Tabs as BkTabs,
                          Column as BkColumn, Panel as BkPanel,
                          WidgetBox as BkWidgetBox, Spacer as BkSpacer)
from panel.layout import Column, Row, Tabs, Spacer
from panel.pane import Bokeh, Pane


def get_div(box):
    # Temporary utilities to unpack widget boxes
    if isinstance(box, BkRow):
        assert isinstance(box.children[1], BkSpacer)
        return get_div(box.children[0])
    elif isinstance(box, Div):
        return box
    assert isinstance(box, BkWidgetBox)
    assert isinstance(box.children[0], Div)
    return box.children[0]


def get_divs(children):
    return [get_div(c) for c in children]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_constructor(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    assert all(isinstance(p, Bokeh) for p in layout.objects)


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_getitem(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    assert layout[0].object is div1
    assert layout[1].object is div2


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_repr(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    name = panel.__name__
    assert repr(layout) == '%s\n    [0] Bokeh(Div)\n    [1] Bokeh(Div)' % name


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_select_by_type(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    panes = layout.select(Bokeh)
    assert len(panes) == 2
    assert all(isinstance(p, Bokeh) for p in panes)
    assert panes[0].object is div1
    assert panes[1].object is div2


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_select_by_function(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    panes = layout.select(lambda x: getattr(x, 'object', None) is div2)
    assert len(panes) == 1
    assert panes[0].object is div2


@pytest.mark.parametrize(['panel', 'model_type'], [(Column, BkColumn), (Row, BkRow)])
def test_layout_get_model(panel, model_type, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_model(document, comm=comm)

    assert isinstance(model, model_type)
    children = model.children
    assert get_divs(children[0].children) == [div1]
    assert get_divs(children[1].children) == [div2]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_append(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_model(document, comm=comm)

    div3 = Div()
    layout.append(div3)
    assert get_divs(model.children[0].children) == [div1]
    assert get_divs(model.children[1].children) == [div2]
    assert get_divs(model.children[2].children) == [div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_insert(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_model(document, comm=comm)

    div3 = Div()
    layout.insert(1, div3)
    assert get_divs(model.children[0].children) == [div1]
    assert get_divs(model.children[1].children) == [div3]
    assert get_divs(model.children[2].children) == [div2]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_model(document, comm=comm)

    assert model.ref['id'] in p1._callbacks
    assert p1._models[model.ref['id']] is model.children[0]
    div3 = Div()
    layout[0] = div3
    assert get_divs(model.children[0].children) == [div3]
    assert get_divs(model.children[1].children) == [div2]
    assert p1._callbacks == {}
    assert p1._models == {}


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_pop(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_model(document, comm=comm)

    assert model.ref['id'] in p1._callbacks
    assert p1._models[model.ref['id']] is model.children[0]
    layout.pop(0)
    assert get_divs(model.children[0].children) == [div2]
    assert p1._callbacks == {}
    assert p1._models == {}


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
    assert get_div(tab1.child.children[0]) is div1
    assert tab2.title == 'Div2'
    assert get_div(tab2.child.children[0]) is div2


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
    assert get_div(tab1.child.children[0]) is div1
    assert tab2.title == 'Div2'
    assert get_div(tab2.child.children[0]) is div2


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
    assert get_div(tab1.child.children[0]) is div1
    assert tab2.title == 'Div2'
    assert get_div(tab2.child.children[0]) is div2
    assert tab3.title == 'Div3'
    assert get_div(tab3.child.children[0]) is div3


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
    assert get_div(tab1.child.children[0]) is div1
    assert get_div(tab2.child.children[0]) is div3
    assert get_div(tab3.child.children[0]) is div2


def test_tabs_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    p1, p2 = tabs.objects

    model = tabs._get_model(document, comm=comm)

    tab1, tab2 = model.tabs
    assert model.ref['id'] in p1._callbacks
    assert p1._models[model.ref['id']] is tab1.child
    div3 = Div()
    tabs[0] = div3
    tab1, tab2 = model.tabs
    assert get_div(tab1.child.children[0]) is div3
    assert get_div(tab2.child.children[0]) is div2
    assert p1._callbacks == {}
    assert p1._models == {}


def test_tabs_pop(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    p1, p2 = tabs.objects

    model = tabs._get_model(document, comm=comm)

    tab1 = model.tabs[0]
    assert model.ref['id'] in p1._callbacks
    assert p1._models[model.ref['id']] is tab1.child
    tabs.pop(0)
    assert len(model.tabs) == 1
    tab1 = model.tabs[0]
    assert get_div(tab1.child.children[0]) is div2
    assert p1._callbacks == {}
    assert p1._models == {}


def test_spacer(document, comm):

    spacer = Spacer(width=400, height=300)

    root = spacer._get_root(document, comm=comm)
    model = root.children[0]
    
    assert isinstance(model, spacer._bokeh_model)
    assert model.width == 400
    assert model.height == 300

    spacer.height = 400
    assert model.height == 400
