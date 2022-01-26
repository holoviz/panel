import datetime
import logging
import pathlib
from inspect import ismodule

import numpy as np
import param
import pytest

import panel as pn
from panel.widgets import slider
from param_stubgen import (_default_to_string, _get_original_docstring,
                           _get_parameterized_classes, _sorted_parameter_names,
                           _to_bases, _to_class_name, _to_init,
                           _to_typed_attributes, _to_typehint, get_modules,
                           module_to_stub, parameterized_to_stub, to_module)

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)

class Parent(param.Parameterized):
        """The Parent class provides ..."""
        a = param.String(doc="A string parameter")
        c = param.Integer(doc="An int parameter")

class Child(Parent):
    """The Child class provides ..."""
    b = param.List(doc="A list parameter")

def test_can_get_parameterized_classes():
    result = _get_parameterized_classes(slider)
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
        (param.Callable(default=print), "print"),
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
        (param.Number(), 'Number=0.0'),
        (param.Date(), 'Optional[Union[datetime.datetime,datetime.date,np.datetime64]]=None'),
        (param.Tuple(), "tuple=(0, 0)"),
        (param.Range(), "Optional[Tuple[Number,Number]]=None"),
        (param.ObjectSelector(), "Any=None"),
        (param.Selector() ,"Any=None"),
        (param.Callable(), "Optional[Callable]=None"),
        (param.Callable(print), "Callable=..."),
        (param.Action(), "Optional[Callable]=None"),
        (param.Action(default=lambda x: print(x)), "Callable=..."),
        (param.Filename(), "Optional[Union[str,pathlib.Path]]=None"),
        (param.Filename(default=pathlib.Path(__file__)), 'Union[str,pathlib.Path]=...'),
        (param.Filename(default='/home/'), 'Union[str,pathlib.Path]="/home/"'),
        (param.Event(), "bool=False"),
        (param.CalendarDate(), "Optional[datetime.date]=None"),
        (param.CalendarDate(default=datetime.date(2020,2,3)), "datetime.date=..."),
        (param.DateRange(),"Optional[Tuple[Union[datetime.datetime,datetime.date,np.datetime64],Union[datetime.datetime,datetime.date,np.datetime64]]]=None"),
        (param.DateRange((datetime.date(2020,2,3), datetime.date(2021,2,3))),"Tuple[Union[datetime.datetime,datetime.date,np.datetime64],Union[datetime.datetime,datetime.date,np.datetime64]]=..."),
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

def test_get_original_docstring():
    expected = 'The Child class provides ...'
    assert _get_original_docstring(Child)==expected


def test_sort_parameters():
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

def test_to_stub_intslider_without_exceptions():
    assert parameterized_to_stub(slider.IntSlider)

def test_to_original_docstring():
    _get_original_docstring

def test_to_stub_basic_parameterized():
    # Todo: indent Args
    expected = '''\
class Child(Parent):
    b: list=[]

    def __init__(self,
        b: list=[],
        a: str="",
        c: int=0,
        name: Optional[str]="Child",
    ):
        """The Child class provides ...

        Args:
            a: A string parameter
            b: A list parameter
            c: An int parameter
            name: String identifier for this object.
"""
'''
    assert parameterized_to_stub(Child) == expected

def test_module_to_stub():
    """Can create stub from module"""
    assert module_to_stub(slider)

def test_to_module():
    to_module(path="", parent="pathlib.Path(pn.__file__).parent")

def test_get_modules(): 
    modules = list(get_modules(pn))
    assert modules
    assert ismodule(modules[0][0])
    assert isinstance(modules[0][1], str)

def test_can_stub_panel():
    for module, path in get_modules(pn):
        module_to_stub(module)
