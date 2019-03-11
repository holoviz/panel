from __future__ import absolute_import

import pytest

from bokeh.models import (Div, Row as BkRow, Tabs as BkTabs,
                          Column as BkColumn, Panel as BkPanel)
from panel.layout import Column, Row, Tabs, Spacer
from panel.pane import Bokeh, Pane
from panel.param import Param


@pytest.fixture
def tabs(document, comm):
    """Set up a tabs instance"""
    div1, div2 = Div(), Div()

    return Tabs(('Tab1', div1), ('Tab2', div2))

def assert_tab_is_similar(tab1, tab2):
    """Helper function to check tab match"""
    assert tab1.child is tab2.child
    assert tab1.name == tab2.name
    assert tab1.title == tab2.title


@pytest.mark.parametrize('layout', [Column, Row, Tabs, Spacer])
def test_layout_model_cache_cleanup(layout, document, comm):
    l = layout()

    model = l._get_root(document, comm)

    assert model.ref['id'] in l._models
    assert l._models[model.ref['id']] == (model, None)

    l._cleanup(model)
    assert l._models == {}


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
def test_layout_get_root(panel, model_type, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_root(document, comm=comm)

    assert isinstance(model, model_type)
    assert model.children == [div1, div2]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_reverse(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_root(document, comm=comm)

    layout.reverse()
    assert model.children == [div2, div1]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_append(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_root(document, comm=comm)

    div3 = Div()
    layout.append(div3)
    assert model.children == [div1, div2, div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_extend(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_root(document, comm=comm)

    div3 = Div()
    div4 = Div()
    layout.extend([div4, div3])
    assert model.children == [div1, div2, div4, div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_insert(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout._get_root(document, comm=comm)

    div3 = Div()
    layout.insert(1, div3)
    assert model.children == [div1, div3, div2]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_root(document, comm=comm)

    assert p1._models[model.ref['id']][0] is model.children[0]
    div3 = Div()
    layout[0] = div3
    assert model.children == [div3, div2]
    assert p1._models == {}


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem_out_of_bounds(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    layout._get_root(document, comm=comm)
    div3 = Div()
    with pytest.raises(IndexError):
        layout[2] = div3


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem_replace_all(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_root(document, comm=comm)

    assert p1._models[model.ref['id']][0] is model.children[0]
    div3 = Div()
    div4 = Div()
    layout[:] = [div3, div4]
    assert model.children == [div3, div4]
    assert p1._models == {}
    assert p2._models == {}


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem_replace_all_error(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    layout._get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[:] = div3


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem_replace_slice(panel, document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = panel(div1, div2, div3)
    p1, p2, p3 = layout.objects

    model = layout._get_root(document, comm=comm)

    assert p1._models[model.ref['id']][0] is model.children[0]
    div3 = Div()
    div4 = Div()
    layout[1:] = [div3, div4]
    assert model.children == [div1, div3, div4]
    assert p2._models == {}
    assert p3._models == {}


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem_replace_slice_error(panel, document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = panel(div1, div2, div3)
    layout._get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[1:] = [div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem_replace_slice_out_of_bounds(panel, document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = panel(div1, div2, div3)
    layout._get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[3:4] = [div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_pop(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_root(document, comm=comm)

    assert p1._models[model.ref['id']][0] is model.children[0]
    layout.pop(0)
    assert model.children == [div2]
    assert p1._models == {}


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_remove(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_root(document, comm=comm)

    assert p1._models[model.ref['id']][0] is model.children[0]
    layout.remove(p1)
    assert model.children == [div2]
    assert p1._models == {}


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_clear(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_root(document, comm=comm)

    assert p1._models[model.ref['id']][0] is model.children[0]
    layout.clear()
    assert model.children == []
    assert p1._models == p2._models == {}


def test_tabs_basic_constructor(document, comm):
    tabs = Tabs('plain', 'text')

    model = tabs._get_root(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 2
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab1, tab2 = model.tabs

    assert 'plain' in tab1.child.text
    assert 'text' in tab2.child.text


def test_tabs_constructor(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(('Div1', div1), ('Div2', div2))
    p1, p2 = tabs.objects

    model = tabs._get_root(document, comm=comm)

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

    model = tabs._get_root(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 2
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab1, tab2 = model.tabs

    assert tab1.title == tab1.name == p1.name == 'Div1'
    assert tab1.child is div1
    assert tab2.title == tab2.name == p2.name == 'Div2'
    assert tab2.child is div2


def test_tabs_constructor_with_named_objects(document, comm):
    div1, div2 = Div(), Div()
    p1 = Pane(div1, name='Div1')
    p2 = Pane(div2, name='Div2')
    tabs = Tabs(('Tab1', p1), ('Tab2', p2))

    model = tabs._get_root(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 2
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab1, tab2 = model.tabs

    assert tab1.title == 'Tab1'
    assert tab1.name == p1.name == 'Div1'
    assert tab1.child is div1
    assert tab2.title == 'Tab2'
    assert tab2.name == p2.name =='Div2'
    assert tab2.child is div2


def test_tabs_set_panes(document, comm):
    div1, div2 = Div(), Div()
    p1 = Pane(div1, name='Div1')
    p2 = Pane(div2, name='Div2')
    tabs = Tabs(p1, p2)

    model = tabs._get_root(document, comm=comm)

    div3 = Div()
    p3 = Pane(div3, name='Div3')
    tabs.objects = [p1, p2, p3]

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 3
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab1, tab2, tab3 = model.tabs

    assert tab1.title == tab1.name == p1.name =='Div1'
    assert tab1.child is div1
    assert tab2.title == tab2.name == p2.name =='Div2'
    assert tab2.child is div2
    assert tab3.title == tab3.name == p3.name =='Div3'
    assert tab3.child is div3


def test_tabs_reverse(document, comm):
    div1, div2 = Div(), Div()
    p1 = Pane(div1, name='Div1')
    p2 = Pane(div2, name='Div2')
    tabs = Tabs(p1, p2)

    model = tabs._get_root(document, comm=comm)

    tabs.reverse()
    tab1, tab2 = model.tabs
    assert tab1.child is div2
    assert tab1.title == tab1.name == p2.name == 'Div2'
    assert tab2.child is div1
    assert tab2.title == tab2.name == p1.name == 'Div1'


def test_tabs_append(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    tabs.append(div3)

    tab1, tab2, tab3 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div3


def test_empty_tabs_append(document, comm):
    tabs = Tabs()

    model = tabs._get_root(document, comm=comm)

    div1 = Div()
    tabs.append(('test title', div1))
    assert len(model.tabs) == 1
    assert model.tabs[0].title == 'test title'


def test_tabs_append_uses_object_name(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    p3 = Pane(div3, name='Div3')
    tabs.append(p3)

    tab1, tab2, tab3 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div3
    assert tab3.title == tab3.name == p3.name == 'Div3'


def test_tabs_append_with_tuple_and_unnamed_contents(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    tabs.append(('Div3', div3))

    tab1, tab2, tab3 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div3
    assert tab3.title == 'Div3'


def test_tabs_append_with_tuple_and_named_contents(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    p3 = Pane(div3, name='Div3')
    tabs.append(('Tab3', p3))

    tab1, tab2, tab3 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div3
    assert tab3.title == 'Tab3'
    assert tab3.name == p3.name == 'Div3'


def test_tabs_extend(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3, div4 = Div(), Div()
    tabs.extend([div4, div3])

    tab1, tab2, tab3, tab4 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div4
    assert tab4.child is div3


def test_tabs_extend_uses_object_name(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3, div4 = Div(), Div()
    p3, p4 = Pane(div3, name='Div3'), Pane(div4, name='Div4')
    tabs.extend([p4, p3])

    tab1, tab2, tab3, tab4 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div4
    assert tab3.title == p4.name == 'Div4'
    assert tab4.child is div3
    assert tab4.title  == p3.name == 'Div3'


def test_tabs_extend_with_tuple_and_unnamed_contents(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3, div4 = Div(), Div()
    tabs.extend([('Div4', div4), ('Div3', div3)])

    tab1, tab2, tab3, tab4 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div4
    assert tab3.title == 'Div4'
    assert tab4.child is div3
    assert tab4.title == 'Div3'


def test_tabs_extend_with_tuple_and_named_contents(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3, div4 = Div(), Div()
    p3, p4 = Pane(div3, name='Div3'), Pane(div4, name='Div4')
    tabs.extend([('Tab4', p4), ('Tab3', p3)])

    tab1, tab2, tab3, tab4 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div4
    assert tab3.title == 'Tab4'
    assert tab3.name == p4.name == 'Div4'
    assert tab4.child is div3
    assert tab4.title == 'Tab3'
    assert tab4.name == p3.name == 'Div3'


def test_tabs_insert(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    tabs.insert(1, div3)

    tab1, tab2, tab3 = model.tabs

    assert_tab_is_similar(tab1_before, tab1)
    assert tab2.child is div3
    assert_tab_is_similar(tab2_before, tab3)


def test_tabs_insert_uses_object_name(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    p3 = Pane(div3, name='Div3')
    tabs.insert(1, p3)

    tab1, tab2, tab3 = model.tabs

    assert_tab_is_similar(tab1_before, tab1)
    assert tab2.child is div3
    assert tab2.title == tab2.name == p3.name == 'Div3'
    assert_tab_is_similar(tab2_before, tab3)


def test_tabs_insert_with_tuple_and_unnamed_contents(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    tabs.insert(1, ('Div3', div3))
    tab1, tab2, tab3 = model.tabs

    assert_tab_is_similar(tab1_before, tab1)
    assert tab2.child is div3
    assert tab2.title == 'Div3'
    assert_tab_is_similar(tab2_before, tab3)


def test_tabs_insert_with_tuple_and_named_contents(document, comm, tabs):
    model = tabs._get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    p3 = Pane(div3, name='Div3')
    tabs.insert(1, ('Tab3', p3))
    tab1, tab2, tab3 = model.tabs

    assert_tab_is_similar(tab1_before, tab1)
    assert tab2.child is div3
    assert tab2.title == 'Tab3'
    assert tab2.name  == p3.name == 'Div3'
    assert_tab_is_similar(tab2_before, tab3)


def test_tabs_setitem(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    p1, p2 = tabs.objects

    model = tabs._get_root(document, comm=comm)

    tab1, tab2 = model.tabs
    assert p1._models[model.ref['id']][0] is tab1.child
    div3 = Div()
    tabs[0] = ('C', div3)
    tab1, tab2 = model.tabs
    assert tab1.child is div3
    assert tab1.title == 'C'
    assert tab2.child is div2
    assert p1._models == {}


def test_tabs_setitem_out_of_bounds(document, comm):
    div1 = Div()
    div2 = Div()
    layout = Tabs(div1, div2)

    layout._get_root(document, comm=comm)
    div3 = Div()
    with pytest.raises(IndexError):
        layout[2] = div3


def test_tabs_setitem_replace_all(document, comm):
    div1 = Div()
    div2 = Div()
    layout = Tabs(div1, div2)
    p1, p2 = layout.objects

    model = layout._get_root(document, comm=comm)

    assert p1._models[model.ref['id']][0] is model.tabs[0].child
    div3 = Div()
    div4 = Div()
    layout[:] = [('B', div3), ('C', div4)]
    tab1, tab2 = model.tabs
    assert tab1.child is div3
    assert tab1.title == 'B'
    assert tab2.child is div4
    assert tab2.title == 'C'
    assert p1._models == {}
    assert p2._models == {}


def test_tabs_setitem_replace_all_error(document, comm):
    div1 = Div()
    div2 = Div()
    layout = Tabs(div1, div2)
    layout._get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[:] = div3


def test_tabs_setitem_replace_slice(document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = Tabs(('A', div1), ('B', div2), ('C', div3))
    p1, p2, p3 = layout.objects

    model = layout._get_root(document, comm=comm)

    assert p1._models[model.ref['id']][0] is model.tabs[0].child
    div3 = Div()
    div4 = Div()
    layout[1:] = [('D', div3), ('E', div4)]
    tab1, tab2, tab3 = model.tabs
    assert tab1.child is div1
    assert tab1.title == 'A'
    assert tab2.child is div3
    assert tab2.title == 'D'
    assert tab3.child is div4
    assert tab3.title == 'E'
    assert p2._models == {}
    assert p3._models == {}


def test_tabs_setitem_replace_slice_error(document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = Tabs(div1, div2, div3)
    layout._get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[1:] = [div3]


def test_tabs_setitem_replace_slice_out_of_bounds(document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = Tabs(div1, div2, div3)
    layout._get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[3:4] = [div3]


def test_tabs_pop(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    p1, p2 = tabs.objects

    model = tabs._get_root(document, comm=comm)

    tab1 = model.tabs[0]
    assert p1._models[model.ref['id']][0] is tab1.child
    tabs.pop(0)
    assert len(model.tabs) == 1
    tab1 = model.tabs[0]
    assert tab1.child is div2
    assert p1._models == {}


def test_tabs_remove(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    p1, p2 = tabs.objects

    model = tabs._get_root(document, comm=comm)

    tab1 = model.tabs[0]
    assert p1._models[model.ref['id']][0] is tab1.child
    tabs.remove(p1)
    assert len(model.tabs) == 1
    tab1 = model.tabs[0]
    assert tab1.child is div2
    assert p1._models == {}


def test_tabs_clear(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    p1, p2 = tabs.objects

    model = tabs._get_root(document, comm=comm)

    tabs.clear()
    assert tabs._names == []
    assert len(model.tabs) == 0
    assert p1._models == p2._models == {}


def test_spacer(document, comm):
    spacer = Spacer(width=400, height=300)

    model = spacer._get_root(document, comm=comm)

    assert isinstance(model, spacer._bokeh_model)
    assert model.width == 400
    assert model.height == 300

    spacer.height = 400
    assert model.height == 400


def test_layout_with_param_setitem(document, comm):
    import param
    class TestClass(param.Parameterized):
        select = param.ObjectSelector(default=0, objects=[0,1])

        def __init__(self, **params):
            super(TestClass, self).__init__(**params)
            self._layout = Row(Param(self.param, parameters=['select']),
                               self.select)

        @param.depends('select', watch=True)
        def _load(self):
            self._layout[-1] = self.select

    test = TestClass()
    model = test._layout._get_root(document, comm=comm)
    test.select = 1
    assert model.children[1].text == '<pre>1</pre>'

