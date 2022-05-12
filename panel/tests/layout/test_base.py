import pytest

import param

from bokeh.models import Column as BkColumn, Div, Row as BkRow

from panel.layout import (
    Accordion, Card, Column, Row, Tabs, Spacer, WidgetBox
)
from panel.layout.base import ListPanel, NamedListPanel
from panel.widgets import Debugger
from panel.param import Param
from panel.pane import Bokeh
from panel.tests.util import check_layoutable_properties

excluded = (NamedListPanel, Debugger)
all_panels = [w for w in param.concrete_descendents(ListPanel).values()
               if not w.__name__.startswith('_') and not issubclass(w, excluded)]

@pytest.mark.parametrize('panel', all_panels)
def test_layout_signature(panel):
    from inspect import signature
    parameters = signature(panel).parameters
    assert len(parameters) == 2, 'Found following parameters %r on %s' % (parameters, panel)
    assert 'objects' in parameters


@pytest.mark.parametrize('layout', [Column, Row, Tabs, Spacer, Card, Accordion])
def test_layout_properties(layout, document, comm):
    l = layout()
    model = l.get_root(document, comm)
    check_layoutable_properties(l, model)


@pytest.mark.parametrize('layout', [Card, Column, Row, Tabs, Spacer])
def test_layout_model_cache_cleanup(layout, document, comm):
    l = layout()

    model = l.get_root(document, comm)

    assert model.ref['id'] in l._models
    assert l._models[model.ref['id']] == (model, None)

    l._cleanup(model)
    assert l._models == {}


@pytest.mark.parametrize('panel', [Card, Column, Row])
def test_layout_constructor(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    assert all(isinstance(p, Bokeh) for p in layout.objects)


@pytest.mark.parametrize('panel', [Card, Column, Row])
def test_layout_constructor_with_objects_param(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(objects=[div1, div2])
    assert all(isinstance(p, Bokeh) for p in layout.objects)


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_add(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout1 = panel(div1, div2)
    div3 = Div()
    div4 = Div()
    layout2 = panel(div3, div4)

    combined = layout1 + layout2

    model = combined.get_root(document, comm=comm)

    assert model.children == [div1, div2, div3, div4]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_add_list(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout1 = panel(div1, div2)
    div3 = Div()
    div4 = Div()

    combined = layout1 + [div3, div4]

    model = combined.get_root(document, comm=comm)

    assert model.children == [div1, div2, div3, div4]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_radd_list(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout1 = panel(div1, div2)
    div3 = Div()
    div4 = Div()

    combined = [div3, div4] + layout1

    model = combined.get_root(document, comm=comm)

    assert model.children == [div3, div4, div1, div2]


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_add_error(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    with pytest.raises(TypeError):
        layout + 1


@pytest.mark.parametrize('panel', [Card, Column, Row])
def test_layout_getitem(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    assert layout[0].object is div1
    assert layout[1].object is div2


@pytest.mark.parametrize('panel', [Card, Column, Row])
def test_layout_repr(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    name = panel.__name__
    assert repr(layout) == '%s\n    [0] Bokeh(Div)\n    [1] Bokeh(Div)' % name


@pytest.mark.parametrize('panel', [Card, Column, Row])
def test_layout_select_by_type(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    panes = layout.select(Bokeh)
    assert len(panes) == 2
    assert all(isinstance(p, Bokeh) for p in panes)
    assert panes[0].object is div1
    assert panes[1].object is div2


@pytest.mark.parametrize('panel', [Card, Column, Row])
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
def test_layout_iadd(panel, document, comm):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)

    model = layout.get_root(document, comm=comm)

    div3 = Div()
    div4 = Div()
    layout += [div4, div3]
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


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_clone_no_args_no_kwargs(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2, width=400, sizing_mode='stretch_height')
    clone = layout.clone()

    assert layout.objects[0].object is clone.objects[0].object
    assert layout.objects[1].object is clone.objects[1].object

    assert clone.width == 400
    assert clone.sizing_mode == 'stretch_height'


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_clone_objects_in_kwargs(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    clone = layout.clone(
        objects=(div2, div1),
        width=400, sizing_mode='stretch_height'
    )

    assert layout.objects[0].object is clone.objects[1].object
    assert layout.objects[1].object is clone.objects[0].object

    assert clone.width == 400
    assert clone.sizing_mode == 'stretch_height'


@pytest.mark.parametrize('panel', [Column, Row])
def test_layout_clone_objects_in_args_and_kwargs(panel):
    div1 = Div()
    div2 = Div()
    layout = panel(div1, div2)
    with pytest.raises(ValueError):
        layout.clone(div1, objects=div1)


def test_widgetbox(document, comm):
    widget_box = WidgetBox("WidgetBox")

    model = widget_box.get_root(document, comm=comm)

    assert isinstance(model, widget_box._bokeh_model)

    # Test the horizontal param.
    assert not widget_box.horizontal
    widget_box.horizontal = True
    assert widget_box.horizontal


def test_layout_with_param_setitem(document, comm):
    import param
    class TestClass(param.Parameterized):
        select = param.ObjectSelector(default=0, objects=[0,1])

        def __init__(self, **params):
            super().__init__(**params)
            self._layout = Row(Param(self.param, parameters=['select']),
                               self.select)

        @param.depends('select', watch=True)
        def _load(self):
            self._layout[-1] = self.select

    test = TestClass()
    model = test._layout.get_root(document, comm=comm)
    test.select = 1
    assert model.children[1].text == '&lt;pre&gt;1&lt;/pre&gt;'
