import param
import pytest

from panel import config
from panel.interact import interactive
from panel.pane import Markdown, Str, panel as panel_fn
from panel.param import ParamMethod
from panel.util import _descendents
from panel.viewable import (
    Child, Children, Viewable, Viewer, is_viewable_param,
)

from .util import jb_available

all_viewables = [w for w in _descendents(Viewable, concrete=True)
               if not w.__name__.startswith('_') and
               not issubclass(w, interactive)]


class ExampleViewer(Viewer):
    value = param.String()

    def __panel__(self):
        return self.value


class ExampleViewerWithDeps(Viewer):
    value = param.String()

    @param.depends('value')
    def __panel__(self):
        return self.value


@jb_available
def test_viewable_ipywidget():
    pane = Str('A')
    with config.set(comms='ipywidgets'):
        data, metadata = pane._repr_mimebundle_()
    assert 'application/vnd.jupyter.widget-view+json' in data

@pytest.mark.parametrize('viewable', all_viewables)
def test_viewable_signature(viewable):
    from inspect import Parameter, signature
    parameters = signature(viewable).parameters
    if getattr(getattr(viewable, '_param__private', object), 'signature', None):
        pytest.skip('Signature already set by Param')
    assert 'params' in parameters
    try:
        assert parameters['params'] == Parameter('params', Parameter.VAR_KEYWORD, annotation='t.Any')
    except Exception:
        assert parameters['params'] == Parameter('params', Parameter.VAR_KEYWORD)

def test_Viewer_not_initialized():
    class Test(Viewer):
        def __panel__(self):
            return "# Test"

    test = panel_fn(Test)
    assert test.object == "# Test"

    # Confirm that initialized also work
    test = panel_fn(Test())
    assert test.object == "# Test"

def test_viewer_wraps_panel():
    tv = ExampleViewer(value="hello")

    view = tv._create_view()
    assert isinstance(view, Markdown)
    assert view.object == "hello"

def test_viewer_wraps_panel_with_deps(document, comm):
    tv = ExampleViewerWithDeps(value="hello")

    view = tv._create_view()

    view.get_root(document, comm)

    assert isinstance(view, ParamMethod)
    assert view._pane.object == "hello"

    tv.value = "goodbye"

    assert view._pane.object == "goodbye"

def test_viewer_with_deps_resolved_by_panel_func(document, comm):
    tv = ExampleViewerWithDeps(value="hello")

    view = panel_fn(tv)

    view.get_root(document, comm)

    assert isinstance(view, ParamMethod)
    assert view._pane.object == "hello"

def test_non_viewer_class():
    # This test checks that a class with __panel__ (other than Viewer)
    # does not raise a TypeError: issubclass() arg 1 must be a class

    class Example:
        def __panel__(self):
            return 42

    panel_fn(Example())

@pytest.mark.parametrize('viewable', all_viewables)
def test_clone(viewable):
    v = Viewable()
    clone = v.clone()

    assert ([(k, v) for k, v in sorted(v.param.values().items()) if k not in ('name')] ==
            [(k, v) for k, v in sorted(clone.param.values().items()) if k not in ('name')])

def test_clone_with_non_defaults():
    v = Viewable(loading=True)
    clone = v.clone()

    assert ([(k, v) for k, v in sorted(v.param.values().items()) if k not in ('name')] ==
            [(k, v) for k, v in sorted(clone.param.values().items()) if k not in ('name')])

def test_clone_skips_class_level_readonly_after_edit_constant():
    from panel.widgets import Terminal

    terminal = Terminal()
    with param.edit_constant(terminal):
        terminal.param.ncols.readonly = False
        terminal.ncols = 10

    clone = terminal.clone()

    assert clone.ncols != 10
    assert clone.param.ncols.readonly

def test_clone_skips_readonly_subclass_parameter():
    class ReadOnlyViewable(Viewable):
        value = param.Integer(default=1, readonly=True)

    v = ReadOnlyViewable()
    with param.edit_constant(v):
        v.param.value.readonly = False
        v.value = 5

    assert v.clone().value == 1

def test_is_viewable_parameter():
    class Example(param.Parameterized):
        p_dict = param.Dict()
        p_child = Child()
        p_children = Children()

        # ClassSelector
        c_viewable = param.ClassSelector(class_=Viewable)
        c_viewables = param.ClassSelector(class_=(Viewable,))
        c_none = param.ClassSelector(class_=None)
        c_tuple = param.ClassSelector(class_=tuple)
        c_list_tuple = param.ClassSelector(class_=(list, tuple))

        # List
        l_no_item_type = param.List()
        l_item_type_viewable = param.List(item_type=Viewable)
        l_item_type_not_viewable = param.List(item_type=tuple)

        l_item_types_viewable = param.List(item_type=(Viewable,))
        l_item_types_not_viewable = param.List(item_type=(tuple,))
        l_item_types_not_viewable2 = param.List(item_type=(list, tuple,))

    example = Example()

    assert not is_viewable_param(example.param.p_dict)
    assert is_viewable_param(example.param.p_child)
    assert is_viewable_param(example.param.p_children)

    # ClassSelector
    assert is_viewable_param(example.param.c_viewable)
    assert is_viewable_param(example.param.c_viewables)
    assert not is_viewable_param(example.param.c_none)
    assert not is_viewable_param(example.param.c_tuple)
    assert not is_viewable_param(example.param.c_list_tuple)

    # List
    assert not is_viewable_param(example.param.l_no_item_type)
    assert not is_viewable_param(example.param.l_no_item_type)
    assert is_viewable_param(example.param.l_item_type_viewable)
    assert not is_viewable_param(example.param.l_item_type_not_viewable)

    assert is_viewable_param(example.param.l_item_types_viewable)
    assert not is_viewable_param(example.param.l_item_types_not_viewable)
    assert not is_viewable_param(example.param.l_item_types_not_viewable2)


def test_viewable_design_and_loading_watchers():
    from panel.io.loading import LOADING_INDICATOR_CSS_CLASS
    from panel.theme import Bootstrap, Native

    md = Markdown('x')
    assert getattr(md, '_assigned_design', None) is None

    md.design = Bootstrap
    assert isinstance(md._design, Bootstrap)

    md.design = None
    assert isinstance(md._design, Native)

    md.loading = True
    assert LOADING_INDICATOR_CSS_CLASS in md.css_classes

    md.param.update(loading=False, design=Bootstrap)
    assert LOADING_INDICATOR_CSS_CLASS not in md.css_classes
    assert isinstance(md._design, Bootstrap)


@pytest.fixture
def preprocess_hooks_active(monkeypatch):
    # Make every default preprocessing hook consider walking the tree
    import panel.models.echarts  # noqa

    from panel.pane.echarts import ECharts
    from panel.pane.holoviews import HoloViews
    monkeypatch.setattr(HoloViews, '_instantiated', True)
    monkeypatch.setattr(ParamMethod, '_instantiated', True)
    monkeypatch.setattr(ECharts, '_js_args', False)


@pytest.fixture
def select_spy(monkeypatch):
    called = []
    original = Markdown.select

    def select(self, selector=None):
        called.append(self)
        return original(self, selector)

    monkeypatch.setattr(Markdown, 'select', select)
    return called


@pytest.mark.usefixtures('preprocess_hooks_active')
def test_preprocess_append_does_not_walk_unchanged_children(document, comm, select_spy):
    from panel.layout import Column

    old = [Markdown(f'{i}') for i in range(10)]
    layout = Column(*old)
    layout.get_root(document, comm)

    select_spy.clear()
    new = Markdown('new')
    layout.append(new)

    assert new in select_spy
    assert not any(md in old for md in select_spy)


@pytest.mark.usefixtures('preprocess_hooks_active')
def test_preprocess_esm_children_does_not_walk_unchanged_children(document, comm, select_spy):
    from panel.custom import JSComponent

    class ChildrenComponent(JSComponent):

        objects = Children()

        _esm = 'export function render({ model }) {}'

    old = [Markdown(f'{i}') for i in range(10)]
    component = ChildrenComponent(objects=old)
    component.get_root(document, comm)

    select_spy.clear()
    new = Markdown('new')
    component.objects = old + [new]

    assert new in select_spy
    assert not any(md in old for md in select_spy)


def test_preprocess_caches_hook_signature(document, comm, monkeypatch):
    import inspect

    from panel.layout import Column

    layout = Column(Markdown('a'))
    layout.get_root(document, comm)
    layout.append(Markdown('b'))

    calls = []
    signature = inspect.signature
    monkeypatch.setattr(inspect, 'signature', lambda *a, **kw: calls.append(a) or signature(*a, **kw))
    layout.append(Markdown('c'))

    assert not calls
