import pytest

from bokeh.models import (
    Div, Spacer as BkSpacer, TabPanel as BkPanel, Tabs as BkTabs,
)

import panel as pn

from panel.layout import Tabs


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
    p1 = pn.panel(div1, name='Div1')
    p2 = pn.panel(div2, name='Div2')
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
    p1 = pn.panel(div1, name='Div1')
    p2 = pn.panel(div2, name='Div2')
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


def test_tabs_add(document, comm):
    div1 = Div()
    div2 = Div()
    tabs1 = Tabs(('Div1', div1), ('Div2', div2))
    div3 = Div()
    div4 = Div()
    tabs2 = Tabs(('Div3', div3), ('Div4', div4))

    combined = tabs1 + tabs2

    model = combined.get_root(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 4
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab1, tab2, tab3, tab4 = model.tabs

    assert tab1.title == 'Div1'
    assert tab1.child is div1
    assert tab2.title == 'Div2'
    assert tab2.child is div2
    assert tab3.title == 'Div3'
    assert tab3.child is div3
    assert tab4.title == 'Div4'
    assert tab4.child is div4


def test_tabs_add_list(document, comm):
    div1 = Div()
    div2 = Div()
    tabs1 = Tabs(('Div1', div1), ('Div2', div2))
    div3 = Div()
    div4 = Div()

    combined = tabs1 + [('Div3', div3), ('Div4', div4)]

    model = combined.get_root(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 4
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab1, tab2, tab3, tab4 = model.tabs

    assert tab1.title == 'Div1'
    assert tab1.child is div1
    assert tab2.title == 'Div2'
    assert tab2.child is div2
    assert tab3.title == 'Div3'
    assert tab3.child is div3
    assert tab4.title == 'Div4'
    assert tab4.child is div4


def test_tabs_radd_list(document, comm):
    div1 = Div()
    div2 = Div()
    tabs1 = Tabs(('Div1', div1), ('Div2', div2))
    div3 = Div()
    div4 = Div()

    combined = [('Div3', div3), ('Div4', div4)] + tabs1

    model = combined.get_root(document, comm=comm)

    assert isinstance(model, BkTabs)
    assert len(model.tabs) == 4
    assert all(isinstance(c, BkPanel) for c in model.tabs)
    tab3, tab4, tab1, tab2 = model.tabs

    assert tab1.title == 'Div1'
    assert tab1.child is div1
    assert tab2.title == 'Div2'
    assert tab2.child is div2
    assert tab3.title == 'Div3'
    assert tab3.child is div3
    assert tab4.title == 'Div4'
    assert tab4.child is div4


def test_tabs_set_panes(document, comm):
    div1, div2 = Div(), Div()
    p1 = pn.panel(div1, name='Div1')
    p2 = pn.panel(div2, name='Div2')
    tabs = Tabs(p1, p2)

    model = tabs.get_root(document, comm=comm)

    div3 = Div()
    p3 = pn.panel(div3, name='Div3')
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
    p1 = pn.panel(div1, name='Div1')
    p2 = pn.panel(div2, name='Div2')
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
    old_tabs = list(model.tabs)
    _, div2 = tabs

    tabs._comm_change(document, model.ref['id'], comm, None, 'tabs', old_tabs, [model.tabs[1]])

    assert len(tabs.objects) == 1
    assert tabs.objects[0] is div2


def test_tabs_close_tab_on_server(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
    _, div2 = tabs

    tabs._server_change(document, model.ref['id'], None, 'tabs', model.tabs, model.tabs[1:])

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

    tabs.param.update(dynamic=True, active=0)

    tab1, tab2 = model.tabs
    assert tab1.child is div1.object
    assert isinstance(tab2.child, BkSpacer)


def test_tabs_append_uses_object_name(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3 = Div()
    p3 = pn.panel(div3, name='Div3')
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
    p3 = pn.panel(div3, name='Div3')
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


def test_tabs_iadd(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3, div4 = Div(), Div()
    tabs += [div4, div3]

    tab1, tab2, tab3, tab4 = model.tabs
    assert_tab_is_similar(tab1_before, tab1)
    assert_tab_is_similar(tab2_before, tab2)

    assert tab3.child is div4
    assert tab4.child is div3


def test_tabs_extend_uses_object_name(document, comm, tabs):
    model = tabs.get_root(document, comm=comm)
    tab1_before, tab2_before = model.tabs

    div3, div4 = Div(), Div()
    p3, p4 = pn.panel(div3, name='Div3'), pn.panel(div4, name='Div4')
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
    p3, p4 = pn.panel(div3, name='Div3'), pn.panel(div4, name='Div4')
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
    p3 = pn.panel(div3, name='Div3')
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
    p3 = pn.panel(div3, name='Div3')
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
    tabs = Tabs(pn.panel(div1), pn.panel(div2))
    clone = tabs.clone()

    assert ([(k, v) for k, v in tabs.param.values().items() if k != 'name'] ==
            [(k, v) for k, v in clone.param.values().items() if k != 'name'])


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


def test_tabs_pane_update(document, comm):
    div1 = Div()
    div2 = Div()
    tabs = Tabs(div1, div2)

    model = tabs.get_root(document, comm=comm)

    new_div = Div()
    tabs[1].object = new_div
    assert model.tabs[1].child is new_div
