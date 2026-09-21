import param
import pytest

from panel.config import config
from panel.pane import HoloViews
from panel.param import Param
from panel.theme import Bootstrap, Material
from panel.theme.base import (
    DESIGN_ALIASES, Design, resolve_component, resolve_design, resolve_widget,
)
from panel.widgets import (
    Checkbox, DiscreteSlider, FloatSlider, IntSlider, LiteralInput, Select,
    TextInput, widget,
)


class Alternate(TextInput):
    pass


class AlternateNumber(FloatSlider):
    pass


class AlternateInt(IntSlider):
    pass


class AlternateBoolean(Checkbox):
    pass


class AlternateSelect(Select):
    pass


class AlternateDiscrete(DiscreteSlider):
    pass


class AlternateLiteral(LiteralInput):
    pass


class AlternateDesign(Design):

    component_mapping = {
        Checkbox: AlternateBoolean,
        DiscreteSlider: AlternateDiscrete,
        FloatSlider: AlternateNumber,
        IntSlider: AlternateInt,
        LiteralInput: AlternateLiteral,
        Select: AlternateSelect,
        TextInput: Alternate,
    }


class Parameters(param.Parameterized):

    string = param.String(default='foo')

    boolean = param.Boolean(default=False)

    number = param.Number(default=0.5, bounds=(0, 1))

    integer = param.Integer(default=1, bounds=(0, 10))

    unbounded = param.Number(default=0.5)

    unbounded_int = param.Integer(default=1)

    dictionary = param.Dict(default={})


@pytest.fixture
def alternate_design():
    with config.set(design=AlternateDesign):
        yield


def _alternates(*types):
    """
    Builds a Design substituting a fresh subclass for each of the given
    component types.

    The types are resolved from the classic mapping by the caller rather
    than declared up front, since Param.mapping, Param.input_widgets and
    HoloViews.default_widgets are mutable class attributes other
    libraries may extend in place.
    """
    mapping = {
        wtype: type(f'Alternate{wtype.__name__}', (wtype,), {})
        for wtype in dict.fromkeys(types)
    }
    design = type('DynamicDesign', (Design,), {'component_mapping': mapping})
    return design, mapping


def _param_widgets(obj, **kwargs):
    pane = Param(obj, **kwargs)
    return {w._param_name: w for w in pane.layout[1:]}


def test_resolve_design_by_name():
    assert resolve_design('material') is Material
    assert resolve_design('Bootstrap') is Bootstrap


def test_resolve_design_passes_through_class():
    assert resolve_design(AlternateDesign) is AlternateDesign


def test_resolve_design_unknown():
    with pytest.raises(ValueError, match='Design .* was not recognized'):
        resolve_design('not-a-design')


@pytest.fixture
def design_alias():
    aliases = []
    def register(ref):
        DESIGN_ALIASES['alias-design'] = ref
        aliases.append('alias-design')
    yield register
    for alias in aliases:
        del DESIGN_ALIASES[alias]


@pytest.mark.parametrize('ref', [
    'panel.theme.material.Material',
    'panel.theme.material:Material',
])
def test_resolve_design_alias(design_alias, ref):
    design_alias(ref)
    assert resolve_design('alias-design') is Material


def test_resolve_design_alias_bad_module(design_alias):
    design_alias('not.a.module.Design')
    with pytest.raises(ValueError, match='could not be resolved'):
        resolve_design('alias-design')


def test_resolve_design_alias_not_a_design(design_alias):
    design_alias('panel.theme.material.MaterialDefaultTheme')
    with pytest.raises(ValueError, match='does not reference a Design'):
        resolve_design('alias-design')


def test_config_design_accepts_string():
    with config.set(design='material'):
        assert config.design is Material


def test_extension_design_accepts_string():
    import panel as pn
    with config.set(design=None):
        pn.extension(design='bootstrap')
        assert config.design is Bootstrap


def test_config_set_if_unset():
    with config.set(design=None):
        assert config.set_if_unset(design=Material) == ['design']
        assert config.design is Material
        assert config.set_if_unset(design=Bootstrap) == []
        assert config.design is Material


def test_config_set_if_unset_invalid():
    with pytest.raises(AttributeError):
        config.set_if_unset(not_a_parameter=True)


def test_resolve_component_without_design():
    with config.set(design=None):
        assert resolve_component(TextInput) is TextInput


def test_resolve_component(alternate_design):
    assert resolve_component(TextInput) is Alternate
    assert resolve_component(Select) is AlternateSelect


def test_resolve_component_ignores_subclasses(alternate_design):
    class CustomTextInput(TextInput):
        pass

    assert resolve_component(CustomTextInput) is CustomTextInput


def test_design_resolve_widget_mapping():
    class WidgetMappingDesign(Design):
        widget_mapping = {
            param.String: Alternate,
            param.Number: lambda p: AlternateInt if isinstance(p, param.Integer) else None
        }

    with config.set(design=WidgetMappingDesign):
        assert resolve_widget(Parameters.param['string']) is Alternate
        assert resolve_widget(Parameters.param['integer']) is AlternateInt
        # The callable returns None for a plain Number, falling back to
        # the classic resolution.
        assert resolve_widget(Parameters.param['number']) is None
        assert resolve_widget(Parameters.param['boolean']) is None


def test_param_widget_type():
    pobjs = [Parameters.param[n] for n in ('string', 'boolean', 'number', 'integer')]
    with config.set(design=None):
        classic = [Param.widget_type(pobj) for pobj in pobjs]

    design, mapping = _alternates(*classic)
    with config.set(design=design):
        resolved = [Param.widget_type(pobj) for pobj in pobjs]

    assert resolved == [mapping[wtype] for wtype in classic]


def test_param_pane_widgets():
    names = ('string', 'boolean', 'number', 'integer')
    with config.set(design=None):
        classic = {
            name: type(w) for name, w in _param_widgets(Parameters()).items()
            if name in names
        }

    design, mapping = _alternates(*classic.values())
    with config.set(design=design):
        widgets = _param_widgets(Parameters())

    for name in names:
        assert type(widgets[name]) is mapping[classic[name]]


def test_param_pane_input_widgets():
    # Unbounded numbers resolve to input widgets, not sliders
    names = ('unbounded', 'unbounded_int')
    with config.set(design=None):
        classic = {
            name: type(w) for name, w in _param_widgets(Parameters()).items()
            if name in names
        }

    design, mapping = _alternates(*classic.values())
    with config.set(design=design):
        widgets = _param_widgets(Parameters())

    for name in names:
        assert type(widgets[name]) is mapping[classic[name]]


def test_param_pane_widget_override_wins(alternate_design):
    pane = Param(Parameters(), widgets={'string': TextInput})
    widgets = {w._param_name: w for w in pane.layout[1:]}
    assert type(widgets['string']) is TextInput


def test_widget_from_single_value(alternate_design):
    assert isinstance(widget('foo', 'Label'), Alternate)
    assert isinstance(widget(True, 'Label'), AlternateBoolean)
    assert isinstance(widget(1, 'Label'), AlternateInt)
    assert isinstance(widget(1.5, 'Label'), AlternateNumber)


def test_widget_from_tuple(alternate_design):
    assert isinstance(widget((0, 10), 'Label'), AlternateInt)
    assert isinstance(widget((0.0, 10.0), 'Label'), AlternateNumber)
    assert isinstance(widget((0, 10, 1, 5), 'Label'), AlternateInt)


def test_widget_from_iterable(alternate_design):
    assert isinstance(widget([1, 2, 3], 'Label'), AlternateDiscrete)
    assert isinstance(widget(['a', 'b'], 'Label'), AlternateSelect)


def test_interact_widgets(alternate_design):
    from panel.interact import interactive

    inter = interactive(lambda a, b: (a, b), a='foo', b=1)
    assert isinstance(inter._widgets['a'], Alternate)
    assert isinstance(inter._widgets['b'], AlternateInt)


def test_holoviews_default_widgets():
    keys = ('discrete', 'discrete_numeric', 'int', 'float')
    with config.set(design=None):
        classic = [HoloViews._resolve_widget(key, False) for key in keys]

    design, mapping = _alternates(*classic)
    with config.set(design=design):
        resolved = [HoloViews._resolve_widget(key, False) for key in keys]

    assert resolved == [mapping[wtype] for wtype in classic]


def test_holoviews_explicit_widgets_not_resolved(alternate_design):
    assert HoloViews._resolve_widget(
        'discrete', False, {'discrete': Select}
    ) is Select
