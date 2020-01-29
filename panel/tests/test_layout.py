from __future__ import absolute_import

import param
import pytest

from bokeh.models import (
    Div, Row as BkRow, Tabs as BkTabs, Column as BkColumn, Panel as BkPanel,
    Spacer as BkSpacer
)

from panel.depends import depends
from panel.layout import (
    Column, ListPanel, Row, Tabs, Spacer, GridSpec, GridBox, WidgetBox
)
from panel.pane import Bokeh, Pane
from panel.param import Param
from panel.widgets import IntSlider
from panel.tests.util import check_layoutable_properties, py3_only


all_panels = [w for w in param.concrete_descendents(ListPanel).values()
               if not w.__name__.startswith('_') and w is not Tabs]


@py3_only
@pytest.mark.parametrize('panel', all_panels)
def test_widget_signature(panel):
    from inspect import signature
    parameters = signature(panel).parameters
    assert len(parameters) == 2
    assert 'objects' in parameters


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
def test_layout_properties(layout, document, comm):
    l = layout()
    model = l.get_root(document, comm)
    check_layoutable_properties(l, model)


@pytest.mark.parametrize('layout', [Column, Row, Tabs, Spacer])
def test_layout_model_cache_cleanup(layout, document, comm):
    l = layout()

    model = l.get_root(document, comm)

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
def test_layoutget_root(panel, model_type, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout.get_root(document, comm=comm)

    assert isinstance(model, model_type)
    assert model.children == [div1, div2]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_reverse(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout.get_root(document, comm=comm)

    layout.reverse()
    assert model.children == [div2, div1]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_append(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout.get_root(document, comm=comm)

    div3 = Div()
    layout.append(div3)
    assert model.children == [div1, div2, div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_extend(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout.get_root(document, comm=comm)

    div3 = Div()
    div4 = Div()
    layout.extend([div4, div3])
    assert model.children == [div1, div2, div4, div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_insert(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout.get_root(document, comm=comm)

    div3 = Div()
    layout.insert(1, div3)
    assert model.children == [div1, div3, div2]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout.get_root(document, comm=comm)

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

    layout.get_root(document, comm=comm)
    div3 = Div()
    with pytest.raises(IndexError):
        layout[2] = div3


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem_replace_all(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout.get_root(document, comm=comm)

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
    layout.get_root(document, comm=comm)

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

    model = layout.get_root(document, comm=comm)

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
    layout.get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[1:] = [div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_setitem_replace_slice_out_of_bounds(panel, document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = panel(div1, div2, div3)
    layout.get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[3:4] = [div3]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_pop(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    p1, p2 = layout.objects

    model = layout.get_root(document, comm=comm)

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

    model = layout.get_root(document, comm=comm)

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

    model = layout.get_root(document, comm=comm)

    assert p1._models[model.ref['id']][0] is model.children[0]
    layout.clear()
    assert model.children == []
    assert p1._models == p2._models == {}


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_clone_args(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    clone = layout.clone(div2, div1)

    assert layout.objects[0].object is clone.objects[1].object
    assert layout.objects[1].object is clone.objects[0].object


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_clone_kwargs(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    clone = layout.clone(width=400, sizing_mode='stretch_height')

    assert clone.width == 400
    assert clone.sizing_mode == 'stretch_height'


def test_tabs_basic_constructor(document, comm):
    tabs = Tabs('plain', 'text')

    model = tabs.get_root(document, comm=comm)

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

    model = tabs.get_root(document, comm=comm)

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

    model = tabs.get_root(document, comm=comm)

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

    model = tabs.get_root(document, comm=comm)

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


def test_tabs_cleanup_panels(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)

    assert model.ref['id'] in tabs._panels
    tabs._cleanup(model)
    assert model.ref['id'] not in tabs._panels


def test_tabs_set_panes(document, comm):
    div1, div2 = Div(), Div()
    p1 = Pane(div1, name='Div1')
    p2 = Pane(div2, name='Div2')
    tabs = Tabs(p1, p2)

    model = tabs.get_root(document, comm=comm)

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

    model = tabs.get_root(document, comm=comm)

    tabs.reverse()
    tab1, tab2 = model.tabs
    assert tab1.child is div2
    assert tab1.title == tab1.name == p2.name == 'Div2'
    assert tab2.child is div1
    assert tab2.title == tab2.name == p1.name == 'Div1'


def test_tabs_append(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    tabs.append(div3)

    tab1, tab2, tab3 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div3


def test_empty_tabs_append(document, comm):
    tabs = Tabs()

    model = tabs.get_root(document, comm=comm)

    div1 = Div()
    tabs.append(('test title', div1))
    assert len(model.tabs) == 1
    assert model.tabs[0].title == 'test title'


def test_tabs_close_tab_in_notebook(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
    _, div2 = tabs

    tabs._comm_change({'tabs': [model.tabs[1].ref['id']]}, model.ref['id'])

    assert len(tabs.objects) == 1
    assert tabs.objects[0] is div2


def test_tabs_close_tab_on_server(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
    _, div2 = tabs

    tabs._server_change(document, model.ref['id'], 'tabs', model.tabs, model.tabs[1:])

    assert len(tabs.objects) == 1
    assert tabs.objects[0] is div2


def test_dynamic_tabs(document, comm, tabs):
    tabs.dynamic = True
    model = tabs.get_root(document, comm=comm)
    div1, div2 = tabs

    tab1, tab2 = model.tabs
    assert tab1.child is div1.object
    assert isinstance(tab2.child, BkSpacer)

    tabs.active = 1

    tab1, tab2 = model.tabs
    assert isinstance(tab1.child, BkSpacer)
    assert tab2.child is div2.object

    tabs.dynamic = False

    tab1, tab2 = model.tabs
    assert tab1.child is div1.object
    assert tab2.child is div2.object

    tabs.param.set_param(dynamic=True, active=0)

    tab1, tab2 = model.tabs
    assert tab1.child is div1.object
    assert isinstance(tab2.child, BkSpacer)


def test_tabs_append_uses_object_name(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
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
    model = tabs.get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    tabs.append(('Div3', div3))

    tab1, tab2, tab3 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div3
    assert tab3.title == 'Div3'


def test_tabs_append_with_tuple_and_named_contents(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
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
    model = tabs.get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3, div4 = Div(), Div()
    tabs.extend([div4, div3])

    tab1, tab2, tab3, tab4 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div4
    assert tab4.child is div3


def test_tabs_extend_uses_object_name(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
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
    model = tabs.get_root(document, comm=comm)
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
    model = tabs.get_root(document, comm=comm)
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
    model = tabs.get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    tabs.insert(1, div3)

    tab1, tab2, tab3 = model.tabs

    assert_tab_is_similar(tab1_before, tab1)
    assert tab2.child is div3
    assert_tab_is_similar(tab2_before, tab3)


def test_tabs_insert_uses_object_name(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
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
    model = tabs.get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    tabs.insert(1, ('Div3', div3))
    tab1, tab2, tab3 = model.tabs

    assert_tab_is_similar(tab1_before, tab1)
    assert tab2.child is div3
    assert tab2.title == 'Div3'
    assert_tab_is_similar(tab2_before, tab3)


def test_tabs_insert_with_tuple_and_named_contents(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
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

    model = tabs.get_root(document, comm=comm)

    tab1, tab2 = model.tabs
    assert p1._models[model.ref['id']][0] is tab1.child
    div3 = Div()
    tabs[0] = ('C', div3)
    tab1, tab2 = model.tabs
    assert tab1.child is div3
    assert tab1.title == 'C'
    assert tab2.child is div2
    assert p1._models == {}


def test_tabs_clone():
    div1 = Div()
    div2 = Div()
    tabs = Tabs(Pane(div1), Pane(div2))
    clone = tabs.clone()

    assert ([(k, v) for k, v in tabs.param.get_param_values() if k != 'name'] ==
            [(k, v) for k, v in clone.param.get_param_values() if k != 'name'])


def test_tabs_clone_args():
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    clone = tabs.clone(div2, div1)

    assert tabs.objects[0].object is clone.objects[1].object
    assert tabs.objects[1].object is clone.objects[0].object


def test_tabs_clone_kwargs():
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    clone = tabs.clone(width=400, sizing_mode='stretch_height')

    assert clone.width == 400
    assert clone.sizing_mode == 'stretch_height'


def test_tabs_setitem_out_of_bounds(document, comm):
    div1 = Div()
    div2 = Div()
    layout = Tabs(div1, div2)

    layout.get_root(document, comm=comm)
    div3 = Div()
    with pytest.raises(IndexError):
        layout[2] = div3


def test_tabs_setitem_replace_all(document, comm):
    div1 = Div()
    div2 = Div()
    layout = Tabs(div1, div2)
    p1, p2 = layout.objects

    model = layout.get_root(document, comm=comm)

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
    layout.get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[:] = div3


def test_tabs_setitem_replace_slice(document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = Tabs(('A', div1), ('B', div2), ('C', div3))
    p1, p2, p3 = layout.objects

    model = layout.get_root(document, comm=comm)

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
    layout.get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[1:] = [div3]


def test_tabs_setitem_replace_slice_out_of_bounds(document, comm):
    div1 = Div()
    div2 = Div()
    div3 = Div()
    layout = Tabs(div1, div2, div3)
    layout.get_root(document, comm=comm)

    div3 = Div()
    with pytest.raises(IndexError):
        layout[3:4] = [div3]


def test_tabs_pop(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)
    p1, p2 = tabs.objects

    model = tabs.get_root(document, comm=comm)

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

    model = tabs.get_root(document, comm=comm)

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

    model = tabs.get_root(document, comm=comm)

    tabs.clear()
    assert tabs._names == []
    assert len(model.tabs) == 0
    assert p1._models == p2._models == {}


def test_spacer(document, comm):
    spacer = Spacer(width=400, height=300)

    model = spacer.get_root(document, comm=comm)

    assert isinstance(model, spacer._bokeh_model)
    assert model.width == 400
    assert model.height == 300

    spacer.height = 400
    assert model.height == 400


def test_spacer_clone():
    spacer = Spacer(width=400, height=300)

    assert spacer.param.get_param_values() == spacer.clone().param.get_param_values()


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
    model = test._layout.get_root(document, comm=comm)
    test.select = 1
    assert model.children[1].text == '&lt;pre&gt;1&lt;/pre&gt;'


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
    assert gspec.param.get_param_values() == clone.param.get_param_values()


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
    

def test_widgetbox(document, comm):
    widget_box = WidgetBox("WidgetBox")

    model = widget_box.get_root(document, comm=comm)

    assert isinstance(model, widget_box._bokeh_model)

    # Test the horizontal param.
    assert not widget_box.horizontal
    widget_box.horizontal = True
    assert widget_box.horizontal


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
