import param
import pytest

from panel import config
from panel.interact import interactive
from panel.pane import Markdown, Str, panel as panel_fn
from panel.param import ParamMethod
from panel.viewable import (
    Child, Children, Viewable, Viewer, is_viewable_param,
)

from .util import jb_available

all_viewables = [w for w in param.concrete_descendents(Viewable).values()
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
        assert parameters['params'] == Parameter('params', Parameter.VAR_KEYWORD, annotation='Any')
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
