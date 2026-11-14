import pathlib

import numpy as np
import pandas as pd
import param
import pytest

from bokeh.plotting import figure

import panel as pn

from panel.chat import ChatMessage
from panel.interact import interactive
from panel.io.loading import LOADING_INDICATOR_CSS_CLASS, _loading_css_classes
from panel.layout import Row
from panel.links import CallbackGenerator
from panel.pane import (
    Bokeh, HoloViews, Interactive, IPyWidget, Markdown, PaneBase, RGGPlot, Str,
    Vega,
)
from panel.param import (
    Param, ParamFunction, ParamMethod, ParamRef, ReactiveExpr,
)
from panel.tests.util import (
    check_layoutable_properties, hv_available, mpl_available,
)
from panel.util import _descendents

SKIP_PANES = (
    Bokeh, ChatMessage, HoloViews, Interactive, IPyWidget, Param,
    ParamFunction, ParamMethod, ParamRef, RGGPlot, ReactiveExpr, Vega,
    interactive
)

all_panes = [w for w in _descendents(PaneBase, concrete=True)
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

    css_classes = _loading_css_classes()
    assert css_classes[0] == LOADING_INDICATOR_CSS_CLASS
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
        w for pwatchers in p.param.watchers.values()
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

def test_pane_with_non_defaults_clone():
    p = Markdown("Hello World", sizing_mode="stretch_width")
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


def test_pane_pad_layout_by_margin_after_construction():
    md = Markdown(width=300)

    assert md.layout.width == 320

    md.width = 200
    assert md.layout.width == 220

    md.height = 100
    assert md.layout.height == 110

    md.sizing_mode = 'stretch_width'
    assert md.layout.sizing_mode == 'stretch_width'


def test_pane_layout_initialized_from_class_defaults():
    # RGGPlot declares width/height defaults which must still be padded
    # onto the layout at construction time
    assert RGGPlot().layout.width == 420
    assert RGGPlot().layout.height == 410
    assert pn.pane.Perspective().layout.min_width == 420


def test_pane_layout_initialized_from_refs():
    source = pn.widgets.IntInput(value=100)

    md = Markdown('x', refs={'width': source.param.value})

    assert md.width == 100
    assert md.layout.width == 120


def _mpl_figure():
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    return plt.figure()


def _pil_image():
    Image = pytest.importorskip('PIL.Image')
    return Image.new('RGB', (2, 2))


def _hv_curve():
    import holoviews as hv
    return hv.Curve([1, 2])


class _Parameterized(param.Parameterized):
    a = param.Integer(default=1)


_dispatch_cases = [
    ('text', 'Markdown'),
    ('# markdown', 'Markdown'),
    ('<div>html</div>', 'Markdown'),
    ('<svg></svg>', 'SVG'),
    ('https://holoviz.org/logo.png', 'PNG'),
    (pathlib.Path('image.png'), 'PNG'),
    (r'$x^2$', 'Markdown'),
    ('{"a": 1}', 'Markdown'),
    (3, 'Str'), (1.5, 'Str'), (True, 'Str'), (None, 'Str'), ((1, 2), 'Str'),
    ({'a': 1}, 'JSON'), ([1, 2], 'JSON'),
    ({'$schema': 'https://vega.github.io/schema/vega-lite/v5.json'}, 'Vega'),
    ({'data': [], 'layout': {}}, 'Plotly'),
    (pd.DataFrame({'a': [1]}), 'DataFrame'), (pd.Series([1]), 'DataFrame'),
    (np.zeros(3), 'Audio'), (b'bytes', 'Video'),
    (_Parameterized(), 'Param'), (_Parameterized, 'Param'), (_Parameterized.param.a, 'Param'),
    (lambda: 1, 'interactive'),
    (pn.bind(lambda v: v, pn.widgets.IntSlider()), 'ParamFunction'),
    (pn.rx(1), 'ReactiveExpr'),
    (figure(), 'Bokeh'),
    pytest.param(_mpl_figure, 'Matplotlib', marks=mpl_available),
    (_pil_image, 'JPG'),
    pytest.param(_hv_curve, 'HoloViews', marks=hv_available),
]

@pytest.mark.parametrize(('obj', 'expected'), _dispatch_cases)
def test_get_pane_type(obj, expected):
    if any(obj is fn for fn in (_mpl_figure, _pil_image, _hv_curve)):
        obj = obj()
    assert PaneBase.get_pane_type(obj).__name__ == expected


def test_get_pane_type_viewable():
    column = pn.Column()
    assert PaneBase.get_pane_type(column) is pn.Column
    assert pn.panel(column) is column


def test_get_pane_type_picks_up_late_subclass_and_releases_it():
    import gc
    import weakref

    assert PaneBase.get_pane_type(1j) is Str

    class ComplexPane(Str):
        priority = 10

        @classmethod
        def applies(cls, obj):
            return isinstance(obj, complex)

    assert PaneBase.get_pane_type(1j) is ComplexPane

    ref = weakref.ref(ComplexPane)
    del ComplexPane
    gc.collect()
    assert ref() is None, 'the dispatch cache must not keep pane classes alive'
    assert PaneBase.get_pane_type(1j) is Str
