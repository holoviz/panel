from param_stubgen import (
    get_parameterized_classes,
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
    result = get_parameterized_classes(slider.__name__, slider.__file__)
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
    value_throttled: Optional[int]=None
    start: int=0
    end: int=1
    step: int=1"""
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
    value_throttled: Optional[int]=None
    start: int=0
    end: int=1
    step: int=1
    
    def __init__(self,
        align: Union[str,tuple]="start",
        aspect_ratio: Any=None,
        background: Any=None,
        bar_color: str="#e6e6e6",
        css_classes: Optional[list]=None,
        direction: str="ltr",
        disabled: bool=False,
        end: int=1,
        format: Optional[Union[str,TickFormatter]]=None,
        height: Optional[int]=None,
        height_policy: str="auto",
        loading: bool=False,
        margin: Any=(5, 10),
        max_height: Optional[int]=None,
        max_width: Optional[int]=None,
        min_height: Optional[int]=None,
        min_width: Optional[int]=None,
        name: str="IntSlider",
        orientation: str="horizontal",
        show_value: bool=True,
        sizing_mode: Union[NoneType,str]=None,
        start: int=0,
        step: int=1,
        tooltips: bool=True,
        value: int=0,
        value_throttled: Optional[int]=None,
        visible: bool=True,
        width: Optional[int]=None,
        width_policy: str="auto",
    ) -> None:
        """The IntSlider widget allows selecting selecting an integer value within a set bounds 
    using a slider.
    
    See https://panel.holoviz.org/reference/widgets/IntSlider.html

    Args:
        value:  The value of the widget. Updated when the slider is dragged
        value_throttled: The value of the widget. Updated when the mouse is no longer clicked
        start: The lower bound
        end: The upper bound
        step: The step size
    """    
'''
    assert to_stub(parameterized) == stub
