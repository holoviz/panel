import param
import pytest

from panel import config
from panel.interact import interactive
from panel.pane import Str, panel
from panel.viewable import Viewable, Viewer

from .util import jb_available

all_viewables = [w for w in param.concrete_descendents(Viewable).values()
               if not w.__name__.startswith('_') and
               not issubclass(w, interactive)]

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
