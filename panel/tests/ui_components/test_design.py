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


class Params(param.Parameterized):

    action = param.Action(lambda self: None)
    boolean = param.Boolean()
    dictionary = param.Dict({})
    integer = param.Integer(1)
    listing = param.List([])
    number = param.Number(1, bounds=(0, 10))
    selector = param.Selector(objects=['a', 'b'])
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
