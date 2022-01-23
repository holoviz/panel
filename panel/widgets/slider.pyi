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
    value: tuple=(None, None)
    value_start: Optional[Union[datetime,date,np.datetime64]]=None
    value_end: Optional[Union[datetime,date,np.datetime64]]=None
    value_throttled: Optional[tuple]=None
    start: Optional[Union[datetime,date,np.datetime64]]=None
    end: Optional[Union[datetime,date,np.datetime64]]=None
    step: Number=1

    def __init__(self,
        value_throttled: Optional[tuple]=None,
        start: Optional[Union[datetime,date,np.datetime64]]=None,
        end: Optional[Union[datetime,date,np.datetime64]]=None,
        step: Number=1,
        value: tuple=(None, None),
        value_start: Optional[Union[datetime,date,np.datetime64]]=None,
        value_end: Optional[Union[datetime,date,np.datetime64]]=None,
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
        name: str="DateRangeSlider",
    ):
        """Parameters of 'DateRangeSlider'
===============================

Parameters changed from their default values are marked in red.
Soft bound values are marked in cyan.
C/V= Constant/Variable, RO/RW = ReadOnly/ReadWrite, AN=Allow None

Name                 Value           Type         Bounds     Mode

align               'start'     ClassSelector                V RW
aspect_ratio          None        Parameter                V RW AN
background            None        Parameter                V RW AN
css_classes           None           List       (0, None)  V RW AN
width                 None         Integer      (0, None)  V RW AN
height                None         Integer      (0, None)  V RW AN
min_width             None         Integer      (0, None)  V RW AN
min_height            None         Integer      (0, None)  V RW AN
max_width             None         Integer      (0, None)  V RW AN
max_height            None         Integer      (0, None)  V RW AN
margin              (5, 10)       Parameter                  V RW
width_policy         'auto'     ObjectSelector               V RW
height_policy        'auto'     ObjectSelector               V RW
sizing_mode           None      ObjectSelector               V RW
visible               True         Boolean        (0, 1)     V RW
loading              False         Boolean        (0, 1)     V RW
disabled             False         Boolean        (0, 1)     V RW
bar_color          '#e6e6e6'        Color                    V RW
direction            'ltr'      ObjectSelector               V RW
orientation       'horizontal'  ObjectSelector               V RW
show_value            True         Boolean        (0, 1)     V RW
tooltips              True         Boolean        (0, 1)     V RW
value             (None, None)      Tuple                    V RW
value_start           None           Date                  C RO AN
value_end             None           Date                  C RO AN
value_throttled       None          Tuple                  C RW AN
start                 None           Date                  V RW AN
end                   None           Date                  V RW AN
step                   1            Number                   V RW

Parameter docstrings:
=====================

align:           Whether the object should be aligned with the start, end or
                 center of its container. If set as a tuple it will declare
                 (vertical, horizontal) alignment.
aspect_ratio:    Describes the proportional relationship between component's
                 width and height.  This works if any of component's dimensions
                 are flexible in size. If set to a number, ``width / height =
                 aspect_ratio`` relationship will be maintained.  Otherwise, if
                 set to ``"auto"``, component's preferred width and height will
                 be used to determine the aspect (if not set, no aspect will be
                 preserved).
background:      Background color of the component.
css_classes:     CSS classes to apply to the layout.
width:           The width of the component (in pixels). This can be either
                 fixed or preferred width, depending on width sizing policy.
height:          The height of the component (in pixels).  This can be either
                 fixed or preferred height, depending on height sizing policy.
min_width:       Minimal width of the component (in pixels) if width is adjustable.
min_height:      Minimal height of the component (in pixels) if height is adjustable.
max_width:       Minimal width of the component (in pixels) if width is adjustable.
max_height:      Minimal height of the component (in pixels) if height is adjustable.
margin:          Allows to create additional space around the component. May
                 be specified as a two-tuple of the form (vertical, horizontal)
                 or a four-tuple (top, right, bottom, left).
width_policy:    Describes how the component should maintain its width.

                 ``"auto"``
                     Use component's preferred sizing policy.

                 ``"fixed"``
                     Use exactly ``width`` pixels. Component will overflow if
                     it can't fit in the available horizontal space.

                 ``"fit"``
                     Use component's preferred width (if set) and allow it to
                     fit into the available horizontal space within the minimum
                     and maximum width bounds (if set). Component's width
                     neither will be aggressively minimized nor maximized.

                 ``"min"``
                     Use as little horizontal space as possible, not less than
                     the minimum width (if set).  The starting point is the
                     preferred width (if set). The width of the component may
                     shrink or grow depending on the parent layout, aspect
                     management and other factors.

                 ``"max"``
                     Use as much horizontal space as possible, not more than
                     the maximum width (if set).  The starting point is the
                     preferred width (if set). The width of the component may
                     shrink or grow depending on the parent layout, aspect
                     management and other factors.
height_policy:   Describes how the component should maintain its height.

                 ``"auto"``
                     Use component's preferred sizing policy.

                 ``"fixed"``
                     Use exactly ``height`` pixels. Component will overflow if
                     it can't fit in the available vertical space.

                 ``"fit"``
                     Use component's preferred height (if set) and allow to fit
                     into the available vertical space within the minimum and
                     maximum height bounds (if set). Component's height neither
                     will be aggressively minimized nor maximized.

                 ``"min"``
                     Use as little vertical space as possible, not less than
                     the minimum height (if set).  The starting point is the
                     preferred height (if set). The height of the component may
                     shrink or grow depending on the parent layout, aspect
                     management and other factors.

                 ``"max"``
                     Use as much vertical space as possible, not more than the
                     maximum height (if set).  The starting point is the
                     preferred height (if set). The height of the component may
                     shrink or grow depending on the parent layout, aspect
                     management and other factors.
sizing_mode:     How the component should size itself.

                 This is a high-level setting for maintaining width and height
                 of the component. To gain more fine grained control over
                 sizing, use ``width_policy``, ``height_policy`` and
                 ``aspect_ratio`` instead (those take precedence over
                 ``sizing_mode``).

                 ``"fixed"``
                     Component is not responsive. It will retain its original
                     width and height regardless of any subsequent browser
                     window resize events.

                 ``"stretch_width"``
                     Component will responsively resize to stretch to the
                     available width, without maintaining any aspect ratio. The
                     height of the component depends on the type of the
                     component and may be fixed or fit to component's contents.

                 ``"stretch_height"``
                     Component will responsively resize to stretch to the
                     available height, without maintaining any aspect
                     ratio. The width of the component depends on the type of
                     the component and may be fixed or fit to component's
                     contents.

                 ``"stretch_both"``
                     Component is completely responsive, independently in width
                     and height, and will occupy all the available horizontal
                     and vertical space, even if this changes the aspect ratio
                     of the component.

                 ``"scale_width"``
                     Component will responsively resize to stretch to the
                     available width, while maintaining the original or
                     provided aspect ratio.

                 ``"scale_height"``
                     Component will responsively resize to stretch to the
                     available height, while maintaining the original or
                     provided aspect ratio.

                 ``"scale_both"``
                     Component will responsively resize to both the available
                     width and height, while maintaining the original or
                     provided aspect ratio.
visible:         Whether the component is visible. Setting visible to false will
                 hide the component entirely.
loading:         Whether or not the Viewable is loading. If True a loading spinner
                 is shown on top of the Viewable.
disabled:        Whether the widget is disabled.
bar_color:       Color of the slider bar as a hexidecimal RGB value.
direction:       Whether the slider should go from left-to-right ('ltr') or
                 right-to-left ('rtl')
orientation:     Whether the slider should be oriented horizontally or
                 vertically.
show_value:      Whether to show the widget value.
tooltips:        Whether the slider handle should display tooltips.
value:           < No docstring available >
value_start:     < No docstring available >
value_end:       < No docstring available >
value_throttled: < No docstring available >
start:           < No docstring available >
end:             < No docstring available >
step:            < No docstring available
"""

    

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
