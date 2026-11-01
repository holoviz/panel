"""
Tests that MaterialUIDesign resolves the widgets Panel generates on the user's
behalf through the Design hooks, independently of panel-material-ui's
import-time patches, which the panel_ui fixture undoes.
"""
import param
import pytest

from panel.config import config
from panel.interact import interactive
from panel.param import Param
from panel.tests.util import hv_available
from panel.widgets import (
    Checkbox, FloatSlider, IntSlider, Select, TextInput,
)


def noop(*args) -> None:
    pass


class Params(param.Parameterized):

    action = param.Action(noop)
    boolean = param.Boolean()
    dictionary = param.Dict({})
    integer = param.Integer(1)
    listing = param.List([])
    number = param.Number(1, bounds=(0, 10))
    selector: param.Selector[str] = param.Selector(default='a', objects=['a', 'b'])
    span = param.Range((0, 1), bounds=(0, 2))
    string = param.String()
    pair = param.Tuple((1, 2))


@pytest.fixture
def material(panel_ui):
    with config.set(design=panel_ui.MaterialUIDesign):
        yield panel_ui


def param_widgets(obj, **kwargs):
    return {w.label: w for w in Param(obj, **kwargs).layout[1:]}


def test_param_widgets_are_material(material):
    widgets = param_widgets(Params())

    expected = {
        'Action': material.Button,
        'Boolean': material.Checkbox,
        'Dictionary': material.DictInput,
        'Integer': material.IntInput,
        'Listing': material.ListInput,
        'Number': material.FloatSlider,
        'Selector': material.Select,
        'Span': material.RangeSlider,
        'String': material.TextInput,
        'Pair': material.TupleInput,
    }
    assert {label: type(w) for label, w in widgets.items()} == expected


def test_param_explicit_widget_is_not_substituted(material):
    widgets = param_widgets(Params(), widgets={'string': TextInput})

    assert type(widgets['String']) is TextInput


def test_param_widgets_are_classic_without_design(panel_ui):
    with config.set(design=None):
        widgets = param_widgets(Params())

    assert type(widgets['String']) is TextInput
    assert type(widgets['Boolean']) is Checkbox
    assert type(widgets['Number']) is FloatSlider


def test_interact_widgets_are_material(material):
    result = interactive(
        lambda s, i, f, o: None, s='a', i=1, f=1.5, o=['a', 'b']
    )

    assert {name: type(w) for name, w in result._widgets.items()} == {
        's': material.TextInput,
        'i': material.IntSlider,
        'f': material.FloatSlider,
        'o': material.Select,
    }


def test_interact_widgets_are_classic_without_design(panel_ui):
    with config.set(design=None):
        result = interactive(lambda s, i, o: None, s='a', i=1, o=['a', 'b'])

    assert {name: type(w) for name, w in result._widgets.items()} == {
        's': TextInput, 'i': IntSlider, 'o': Select,
    }


@hv_available
def test_holoviews_widgets_are_material(material):
    import holoviews as hv

    from panel.pane import HoloViews

    hmap = hv.HoloMap(
        {(i, c): hv.Curve([i]) for i in range(3) for c in 'ab'},
        kdims=['X', 'C']
    )
    widgets, _ = HoloViews.widgets_from_dimensions(hmap)

    assert [type(w) for w in widgets] == [
        material.DiscreteSlider, material.Select
    ]


def test_ui_param_widgets_are_material_without_design(panel_ui):
    with config.set(design=None):
        widgets = {w.label: w for w in panel_ui.Param(Params()).layout[1:]}

    assert type(widgets['String']) is panel_ui.TextInput
    assert type(widgets['Number']) is panel_ui.FloatSlider
    assert type(widgets['Pair']) is panel_ui.TupleInput


def test_ui_param_widget_type_is_material_without_design(panel_ui):
    with config.set(design=None):
        assert panel_ui.Param.widget_type(Params.param.string) is panel_ui.TextInput
        assert Param.widget_type(Params.param.string) is TextInput


def test_ui_param_expands_subobjects_with_ui_param(panel_ui):
    class Outer(param.Parameterized):
        inner = param.ClassSelector(class_=Params, default=Params())

    with config.set(design=None):
        pane = panel_ui.Param(Outer(), expand=True)

    assert [type(p) for p in pane._expand_layout if isinstance(p, Param)] == [panel_ui.Param]


def test_ui_panel_returns_ui_param(panel_ui):
    with config.set(design=None):
        layout = panel_ui.panel(Params().param)

    assert type(layout[1]) is panel_ui.Button
    assert type(panel_ui.panel('# Title')).__name__ == 'Markdown'


def test_panel_does_not_return_ui_param(panel_ui):
    from panel.pane import PaneBase

    assert PaneBase.get_pane_type(Params().param) is Param


@hv_available
def test_ui_holoviews_widgets_are_material_without_design(panel_ui):
    import holoviews as hv

    from panel.pane import HoloViews, PaneBase

    hmap = hv.HoloMap(
        {(i, c): hv.Curve([i]) for i in range(3) for c in 'ab'},
        kdims=['X', 'C']
    )
    with config.set(design=None):
        widgets, _ = panel_ui.HoloViews.widgets_from_dimensions(hmap)
        classic, _ = HoloViews.widgets_from_dimensions(hmap)
        pane = panel_ui.panel(hmap)

    assert [type(w) for w in widgets] == [panel_ui.DiscreteSlider, panel_ui.Select]
    assert [type(w).__module__.split('.')[0] for w in classic] == ['panel', 'panel']
    assert type(pane[0]) is panel_ui.HoloViews
    assert PaneBase.get_pane_type(hmap) is HoloViews


def test_ui_holoviews_pane_widgets_are_material_without_design(panel_ui):
    import holoviews as hv

    dmap = hv.DynamicMap(
        lambda wave, frequency: hv.Curve([]), kdims=['wave', 'frequency']
    ).redim.values(wave=['sin', 'cos']).redim.range(frequency=(0.5, 5))
    with config.set(design=None):
        pane = panel_ui.HoloViews(dmap)

    assert [type(w) for w in pane.widget_box] == [
        panel_ui.Select, panel_ui.EditableFloatSlider
    ]


def test_holoviews_pane_widgets_are_material(material):
    import holoviews as hv

    from panel.pane import HoloViews

    hmap = hv.HoloMap(
        {(i, c): hv.Curve([i]) for i in range(3) for c in 'ab'},
        kdims=['X', 'C']
    )
    pane = HoloViews(hmap)

    assert [type(w) for w in pane.widget_box] == [
        material.DiscreteSlider, material.Select
    ]


def test_ui_holoviews_pane_keeps_overridden_default_widgets(panel_ui):
    import holoviews as hv

    from panel.widgets import RadioButtonGroup

    hmap = hv.HoloMap({c: hv.Curve([]) for c in 'ab'}, kdims=['C'])
    pane = panel_ui.HoloViews(hmap, default_widgets={'discrete': RadioButtonGroup})

    assert type(pane.widget_box[0]) is RadioButtonGroup
