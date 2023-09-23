import param
import pytest

from panel import config
from panel.interact import interactive
from panel.pane import Markdown, Str, panel
from panel.param import ParamMethod
from panel.viewable import Viewable, Viewer

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

    test = panel(Test)
    assert test.object == "# Test"

    # Confirm that initialized also work
    test = panel(Test())
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

    view = panel(tv)

    view.get_root(document, comm)

    assert isinstance(view, ParamMethod)
    assert view._pane.object == "hello"

def test_non_viewer_class():
    # This test checks that a class with __panel__ (other than Viewer)
    # does not raise a TypeError: issubclass() arg 1 must be a class

    class Example:
        def __panel__(self):
            return 42

    panel(Example())
