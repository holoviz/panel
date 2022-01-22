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

from bokeh.models import TickFormatter
from typing import Union, NoneType
    
class IntSlider(ContinuousSlider):
    value: int=0
    value_throttled: Optional[int]=None
    start: int=0
    end: int=1
    step: int=1

    def __init__(self,
        value: int=0,
        start: int=0,
        end: int=1,
        step: int=1,
        value_throttled: Optional[int]=None,
        format: Optional[Union[str,TickFormatter]]=None,
        bar_color: str="#e6e6e6",
        **params
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
        value_throttled: The value of the widget. Updated when the mouse is no longer clicked
        visible: Whether the component is visible. Setting visible to false will hide the component entirely.
        width: The width of the component (in pixels). This can be either fixed or preferred width, depending on width sizing policy.
        width_policy: Describes how the component should maintain its width.
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
