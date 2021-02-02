import pytest

import param

from panel.interact import interactive
from panel.pane import Pane, PaneBase, Bokeh, HoloViews, IPyWidget, Interactive
from panel.param import ParamMethod
from panel.tests.util import check_layoutable_properties, py3_only


all_panes = [w for w in param.concrete_descendents(PaneBase).values()
             if not w.__name__.startswith('_') and not
             issubclass(w, (Bokeh, HoloViews, ParamMethod, interactive, IPyWidget, Interactive))
             and w.__module__.startswith('panel')]


def test_pane_repr(document, comm):
    pane = Pane('Some text', width=400)
    assert repr(pane) == 'Markdown(str, width=400)'


@pytest.mark.parametrize('pane', all_panes)
def test_pane_layout_properties(pane, document, comm):
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    model = p.get_root(document, comm)
    check_layoutable_properties(p, model)


@pytest.mark.parametrize('pane', all_panes)
def test_pane_clone(pane):
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    clone = p.clone()

    assert ([(k, v) for k, v in sorted(p.param.get_param_values()) if k != 'name'] ==
            [(k, v) for k, v in sorted(clone.param.get_param_values()) if k != 'name'])


@py3_only
@pytest.mark.parametrize('pane', all_panes)
def test_pane_signature(pane):
    from inspect import Parameter, signature
    parameters = signature(pane).parameters
    assert len(parameters) == 2
    assert 'object' in parameters
    assert parameters['object'] == Parameter('object', Parameter.POSITIONAL_OR_KEYWORD, default=None)
