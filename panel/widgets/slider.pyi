from ..config import config as config
from ..io import state as state
from ..layout import Column as Column, Row as Row
from ..util import edit_readonly as edit_readonly, param_reprs as param_reprs, value_as_date as value_as_date, value_as_datetime as value_as_datetime
from ..viewable import Layoutable as Layoutable
from .base import CompositeWidget as CompositeWidget, Widget as Widget
from .input import FloatInput as FloatInput, IntInput as IntInput, StaticText as StaticText
from typing import Any, Optional

class _SliderBase(Widget):
    bar_color: str
    direction: str
    orientation: str
    show_value: bool
    tooltips: bool
    
    def __init__(self, **params) -> None: ...

class ContinuousSlider(_SliderBase):
    format: Any
    def __init__(self, **params) -> None: ...


class FloatSlider(ContinuousSlider):
    start: Any
    end: Any
    value: Any
    value_throttled: Any
    step: Any
    
class IntSlider(ContinuousSlider):
    value: int
    value_throttled: Optional[int]
    start: int
    end: int
    step: int

    def __init__(self, value: int=0, value_throttled: Optional[int]=None, start: int=0, end: int=1, step: int=1, **params) -> None:
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
    
class DateSlider(_SliderBase):
    value: Any
    value_throttled: Any
    start: Any
    end: Any
    def __init__(self, **params) -> None: ...

class DiscreteSlider(CompositeWidget, _SliderBase):
    options: Any
    value: Any
    value_throttled: Any
    formatter: Any
    def __init__(self, **params) -> None: ...
    @property
    def labels(self): ...
    @property
    def values(self): ...

class _RangeSliderBase(_SliderBase):
    value: Any
    value_start: Any
    value_end: Any
    def __init__(self, **params) -> None: ...

class RangeSlider(_RangeSliderBase):
    format: Any
    value: Any
    value_start: Any
    value_end: Any
    value_throttled: Any
    start: Any
    end: Any
    step: Any
    def __init__(self, **params) -> None: ...

class IntRangeSlider(RangeSlider):
    start: Any
    end: Any
    step: Any

class DateRangeSlider(_RangeSliderBase):
    value: Any
    value_start: Any
    value_end: Any
    value_throttled: Any
    start: Any
    end: Any
    step: Any

class _EditableContinuousSlider(CompositeWidget):
    editable: Any
    show_value: Any
    def __init__(self, **params) -> None: ...

class EditableFloatSlider(_EditableContinuousSlider, FloatSlider): ...
class EditableIntSlider(_EditableContinuousSlider, IntSlider): ...

class EditableRangeSlider(CompositeWidget, _SliderBase):
    editable: Any
    end: Any
    format: Any
    show_value: Any
    start: Any
    step: Any
    value: Any
    value_throttled: Any
    def __init__(self, **params) -> None: ...
