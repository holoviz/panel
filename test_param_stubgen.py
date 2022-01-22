from param_stubgen import (
    _get_parameterized_classes,
    _to_bases,
    _to_class_name,
    to_stub,
    _to_typed_attributes,
    _to_typehint,
    _default_to_string,
    _to_init,
    _sorted_parameter_names,
)
from panel.widgets import slider
import pytest
import param


def test_can_get_parameterized_classes():
    result = _get_parameterized_classes(slider.__name__, slider.__file__)
    result_set = set(item.__name__ for item in result)
    assert result_set == {
        "_SliderBase",
        "ContinuousSlider",
        "FloatSlider",
        "IntSlider",
        "DateSlider",
        "DiscreteSlider",
        "_RangeSliderBase",
        "RangeSlider",
        "IntRangeSlider",
        "DateRangeSlider",
        "_EditableContinuousSlider",
        "EditableFloatSlider",
        "EditableIntSlider",
        "EditableRangeSlider",
    }


def test_to_class_name():
    parameterized = slider.IntSlider
    assert _to_class_name(parameterized) == "IntSlider"


def test_to_bases():
    parameterized = slider.IntSlider
    assert _to_bases(parameterized) == "ContinuousSlider"


@pytest.mark.parametrize(
    ["parameter", "expected"],
    [
        (param.String(default="a"), '"a"'),
        (param.String(default=None), "None"),
        (param.Integer(default=2), "2"),
    ],
)
def test_default_to_string(parameter, expected):
    assert _default_to_string(parameter.default) == expected


@pytest.mark.parametrize(
    ["parameter", "typehint"],
    [
        (
            param.Boolean(),
            "bool=False",
        ),
        (
            param.Boolean(default=None),
            "Optional[bool]=None",
        ),
        (
            param.Color(),
            "Optional[str]=None",
        ),
        (
            param.Color("#aabbcc", allow_None=False),
            'str="#aabbcc"',
        ),
        (param.Integer(), "int=0"),
        (param.List(), "list=[]"),
        (param.List(class_=str), "List[str]=[]"),
        (param.List(class_=(str, int)), "List[str,int]=[]"),
        (param.Parameter(), "Any=None"),
        (param.String(), 'str=""'),
        (param.ClassSelector(class_=bool), "Optional[bool]=None"),
        (param.ClassSelector(default=True, class_=bool), "bool=True"),
        (param.ClassSelector(default=True, class_=bool, allow_None=True), "Optional[bool]=True"),
        (param.ClassSelector(class_=(str, int)), "Optional[Union[int,str]]=None"),
        (param.ClassSelector(default="test", class_=(str, int)), 'Union[int,str]="test"'),
        (
            param.ClassSelector(default="test", class_=(str, int), allow_None=True),
            'Optional[Union[int,str]]="test"',
        ),
        (slider.Widget.param.sizing_mode, "Union[NoneType,str]=None"),
    ],
)
def test_to_type_hint(parameter, typehint):
    assert _to_typehint(parameter) == typehint


def test_to_typed_attributes():
    parameterized = slider.IntSlider
    assert (
        _to_typed_attributes(parameterized)
        == """\
    value: int=0
    start: int=0
    end: int=1
    step: int=1
    value_throttled: Optional[int]=None"""
    )


def test_sort_parameters():
    class Parent(param.Parameterized):
        a = param.Parameter()
        c = param.Parameter()

    class Child(Parent):
        b = param.Parameter()

    actual = _sorted_parameter_names(Child)
    assert actual==['b', 'a', 'c', 'name']


def test_to_init():
    parameterized = slider.IntSlider
    expected = """\
    def __init__(self,
        value: int=0,
        start: int=0,
        end: int=1,
        step: int=1,
        value_throttled: Optional[int]=None,
        format: Optional[Union[str,TickFormatter]]=None,
        bar_color: str="#e6e6e6",
        direction: str="ltr",
        orientation: str="horizontal",
        show_value: bool=True,
        tooltips: bool=True,
        disabled: bool=False,
        loading: bool=False,
        align: Union[str,tuple]="start",
        aspect_ratio: Any=None,
        background: Any=None,
        css_classes: Optional[list]=None,
        width: Optional[int]=None,
        height: Optional[int]=None,
        min_width: Optional[int]=None,
        min_height: Optional[int]=None,
        max_width: Optional[int]=None,
        max_height: Optional[int]=None,
        margin: Any=(5, 10),
        width_policy: str="auto",
        height_policy: str="auto",
        sizing_mode: Union[NoneType,str]=None,
        visible: bool=True,
        name: str="IntSlider",
    ):"""
    actual = _to_init(parameterized)
    assert len(actual) == len(expected)
    assert actual == expected


def test_to_stub():
    parameterized = slider.IntSlider
    stub = '''\
class IntSlider(ContinuousSlider):
    value: int=0
    start: int=0
    end: int=1
    step: int=1
    value_throttled: Optional[int]=None

    def __init__(self,
        value: int=0,
        start: int=0,
        end: int=1,
        step: int=1,
        value_throttled: Optional[int]=None,
        format: Optional[Union[str,TickFormatter]]=None,
        bar_color: str="#e6e6e6",
        direction: str="ltr",
        orientation: str="horizontal",
        show_value: bool=True,
        tooltips: bool=True,
        disabled: bool=False,
        loading: bool=False,
        align: Union[str,tuple]="start",
        aspect_ratio: Any=None,
        background: Any=None,
        css_classes: Optional[list]=None,
        width: Optional[int]=None,
        height: Optional[int]=None,
        min_width: Optional[int]=None,
        min_height: Optional[int]=None,
        max_width: Optional[int]=None,
        max_height: Optional[int]=None,
        margin: Any=(5, 10),
        width_policy: str="auto",
        height_policy: str="auto",
        sizing_mode: Union[NoneType,str]=None,
        visible: bool=True,
        name: str="IntSlider",
    ):
        """The IntSlider widget allows selecting selecting an integer value within a set bounds
    using a slider.

    See https://panel.holoviz.org/reference/widgets/IntSlider.html

    Args:
        align: Whether the object should be aligned with the start, end or center of its container. If set as a tuple it will declare (vertical, horizontal) alignment.
        aspect_ratio: Describes the proportional relationship between component's width and height. This works if any of component's dimensions are flexible in size. If set to a number, ``width / height = aspect_ratio`` relationship will be maintained. Otherwise, if set to ``"auto"``, component's preferred width and height will be used to determine the aspect (if not set, no aspect will be preserved).
        background: Background color of the component.
        bar_color: Color of the slider bar as a hexidecimal RGB value.
        css_classes: CSS classes to apply to the layout.
        direction: Whether the slider should go from left-to-right ('ltr') or right-to-left ('rtl')
        disabled: Whether the widget is disabled.
        end: The upper bound
        format: Allows defining a custom format string or bokeh TickFormatter.
        height: The height of the component (in pixels). This can be either fixed or preferred height, depending on height sizing policy.
        height_policy: Describes how the component should maintain its height.
        loading: Whether or not the Viewable is loading. If True a loading spinner is shown on top of the Viewable.
        margin: Allows to create additional space around the component. May be specified as a two-tuple of the form (vertical, horizontal) or a four-tuple (top, right, bottom, left).
        max_height: Minimal height of the component (in pixels) if height is adjustable.
        max_width: Minimal width of the component (in pixels) if width is adjustable.
        min_height: Minimal height of the component (in pixels) if height is adjustable.
        min_width: Minimal width of the component (in pixels) if width is adjustable.
        name: String identifier for this object.
        orientation: Whether the slider should be oriented horizontally or vertically.
        show_value: Whether to show the widget value.
        sizing_mode: How the component should size itself.
        start: The lower bound
        step: The step size
        tooltips: Whether the slider handle should display tooltips.
        value: The value of the widget. Updated when the slider is dragged
        value_throttled: The value of the widget. Updated on mouse up
        visible: Whether the component is visible. Setting visible to false will hide the component entirely.
        width: The width of the component (in pixels). This can be either fixed or preferred width, depending on width sizing policy.
        width_policy: Describes how the component should maintain its width.
"""    
'''
    assert to_stub(parameterized) == stub
