import param
import pytest

import panel as pn

from panel.config import config
from panel.interact import interactive
from panel.io.loading import LOADING_INDICATOR_CSS_CLASS
from panel.layout import Row
from panel.links import CallbackGenerator
from panel.pane import (
    Bokeh, HoloViews, Interactive, IPyWidget, Markdown, PaneBase, RGGPlot,
    Vega,
)
from panel.param import Param, ParamMethod
from panel.tests.util import check_layoutable_properties
from panel.util import param_watchers

SKIP_PANES = (
    Bokeh, HoloViews, Interactive, IPyWidget, Param, ParamMethod, RGGPlot,
    Vega, interactive
)

all_panes = [w for w in param.concrete_descendents(PaneBase).values()
             if not w.__name__.startswith('_') and not
             issubclass(w, SKIP_PANES)
             and w.__module__.startswith('panel')]


def test_pane_repr(document, comm):
    pane = pn.panel('Some text', width=400)
    assert repr(pane) == 'Markdown(str, width=400)'


@pytest.mark.parametrize('pane', all_panes)
def test_pane_layout_properties(pane, document, comm):
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    model = p.get_root(document, comm)
    check_layoutable_properties(p, model)


@pytest.mark.parametrize('pane', all_panes+[Bokeh, HoloViews])
def test_pane_linkable_params(pane, document, comm):
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    controls = p.controls(jslink=True)
    layout = Row(p, controls)

    try:
        CallbackGenerator.error = True
        layout.get_root(document, comm)
    except Exception as e:
        raise e
    finally:
        CallbackGenerator.error = False

@pytest.mark.parametrize('pane', all_panes+[Bokeh])
def test_pane_loading_param(pane, document, comm):
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")

    root = p.get_root(document, comm)
    model = p._models[root.ref['id']][0]

    p.loading = True

    css_classes = [LOADING_INDICATOR_CSS_CLASS, f'pn-{config.loading_spinner}']
    assert all(cls in model.css_classes for cls in css_classes)

    p.loading = False

    assert not any(cls in model.css_classes for cls in css_classes)

@pytest.mark.parametrize('pane', all_panes+[Bokeh])
def test_pane_untracked_watchers(pane, document, comm):
    # Ensures internal code correctly detects
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    watchers = [
        w for pwatchers in param_watchers(p).values()
        for awatchers in pwatchers.values() for w in awatchers
    ]
    assert len([wfn for wfn in watchers if wfn not in p._internal_callbacks and not hasattr(wfn.fn, '_watcher_name')]) == 0

@pytest.mark.parametrize('pane', all_panes)
def test_pane_clone(pane):
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    clone = p.clone()

    assert ([(k, v) for k, v in sorted(p.param.values().items()) if k not in ('name', '_pane')] ==
            [(k, v) for k, v in sorted(clone.param.values().items()) if k not in ('name', '_pane')])


@pytest.mark.parametrize('pane', all_panes)
def test_pane_signature(pane):
    from inspect import Parameter, signature
    parameters = signature(pane).parameters
    assert len(parameters) == 2
    assert 'object' in parameters
    assert parameters['object'] == Parameter('object', Parameter.POSITIONAL_OR_KEYWORD, default=None)


def test_pane_pad_layout_by_margin():
    md = Markdown(width=300, height=300, margin=(25, 12, 14, 42))

    assert md.layout.width == 354
    assert md.layout.height == 339
