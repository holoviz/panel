# panel.widgets.slider module

Sliders allow you to select a value from a defined range of values by
moving one or more handle(s).

- The value will update when a handle is dragged.

- The [\`](#id1)value_throttled\`will update when
  a handle is released.

class panel.widgets.slider.ContinuousSlider(\*, format, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SliderBase`

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label, value
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
>

`format`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'bokeh.models.formatters.TickFormatter'>),`` ``label='Format')`
A custom format string or Bokeh TickFormatter.

class panel.widgets.slider.DateRangeSlider(\*, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SliderBase`

The DateRangeSlider widget allows selecting a date range using a slider
with two handles. Supports datetime.datetime, datetime.date and
np.datetime64 ranges.

Reference: [https://panel.holoviz.org/reference/widgets/DateRangeSlider.html](https://panel.holoviz.org/reference/widgets/DateRangeSlider.html)

Example:

\>\>\>
import
datetime
as
dt \>\>\>
DateRangeSlider(
...
value=(dt.datetime(2025,
1,
9),
dt.datetime(2025,
1,
16)),
...
start=dt.datetime(2025,
1,
1), ...

end=dt.datetime(2025,
1,
31), ...

step=2,
...
name="A
tuple of datetimes" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
>

`value`` ``=`` ``DateRange(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2)`
The selected range as a tuple of values. Updated when one of the handles
is dragged. Supports datetime.datetime, datetime.date, and np.datetime64
ranges.

`value_start`` ``=`` ``Date(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``start',`` ``readonly=True)`
The lower value of the selected range.

`value_end`` ``=`` ``Date(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``end',`` ``readonly=True)`
The upper value of the selected range.

`value_throttled`` ``=`` ``DateRange(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled',`` ``length=2,`` ``nested_refs=True)`
The selected range as a tuple of values. Updated one of the handles is
released. Supports datetime.datetime, datetime.date and np.datetime64
ranges

`start`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Number(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size in days. Default is 1 day.

`format`` ``=`` ``String(allow_None=True,`` ``label='Format')`
Datetime format used for parsing and formatting the date.

class panel.widgets.slider.DateSlider(\*, as_datetime, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SliderBase`

The DateSlider widget allows selecting a value within a set of bounds
using a slider. Supports datetime.datetime, datetime.date and
np.datetime64 values. The step size is fixed at 1 day.

Reference:
[https://panel.holoviz.org/reference/widgets/DateSlider.html](https://panel.holoviz.org/reference/widgets/DateSlider.html)

Example:

\>\>\>
import
datetime
as
dt \>\>\>
DateSlider(
...
value=dt.datetime(2025,
1,
1), ...

start=dt.datetime(2025,
1,
1), ...

end=dt.datetime(2025,
1,
7), ...

name="A
datetime value" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
>

`value`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The selected date value of the slider. Updated when the slider handle is
dragged. Supports datetime.datetime, datetime.date or np.datetime64
types.

`value_throttled`` ``=`` ``Date(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The value of the slider. Updated when the slider handle is released.

`start`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`as_datetime`` ``=`` ``Boolean(default=False,`` ``label='As`` ``datetime')`
Whether to store the date as a datetime.

`step`` ``=`` ``Integer(bounds=(1,`` ``None),`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step parameter in days.

`format`` ``=`` ``String(allow_None=True,`` ``label='Format')`
Datetime format used for parsing and formatting the date.

class panel.widgets.slider.DatetimeRangeSlider(\*, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [DateRangeSlider](#panel.widgets.slider.DateRangeSlider)

The DatetimeRangeSlider widget allows selecting a datetime range using a
slider with two handles. Supports datetime.datetime and np.datetime64
ranges.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimeRangeSlider.html](https://panel.holoviz.org/reference/widgets/DatetimeRangeSlider.html)

Example:

\>\>\>
import
datetime
as
dt \>\>\>
DatetimeRangeSlider(
...
value=(dt.datetime(2025,
1,
9),
dt.datetime(2025,
1,
16)),
...
start=dt.datetime(2025,
1,
1), ...

end=dt.datetime(2025,
1,
31), ...

step=10000,
...
name="A
tuple of datetimes" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> [class="reference internal"
> title="panel.widgets.slider.DateRangeSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.DateRangeSlider](#panel.widgets.slider.DateRangeSlider):
> value, value_start, value_end, value_throttled, start, end, format
>
>

`step`` ``=`` ``Number(default=60000,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size in ms. Default is 1 min.

class panel.widgets.slider.DatetimeSlider(\*, as_datetime, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[DateSlider](#panel.widgets.slider.DateSlider)

The DatetimeSlider widget allows selecting a value within a set of
bounds using a slider. Supports datetime.date, datetime.datetime and
np.datetime64 values. The step size is fixed at 1 minute.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimeSlider.html](https://panel.holoviz.org/reference/widgets/DatetimeSlider.html)

Example:

\>\>\>
import
datetime
as
dt \>\>\>
DatetimeSlider(
...
value=dt.datetime(2025,
1,
1), ...

start=dt.datetime(2025,
1,
1), ...

end=dt.datetime(2025,
1,
7), ...

name="A
datetime value" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> [title="panel.widgets.slider.DateSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.DateSlider](#panel.widgets.slider.DateSlider):
> value, value_throttled, start, end, format
>
>

`as_datetime`` ``=`` ``Boolean(constant=True,`` ``default=True,`` ``label='As`` ``datetime',`` ``readonly=True)`
Whether to store the date as a datetime.

`step`` ``=`` ``Number(bounds=(1,`` ``None),`` ``default=60,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size in seconds. Default is 1 minute, i.e 60 seconds.

class panel.widgets.slider.DiscreteSlider(\*, formatter, options, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget),
`_SliderBase`

The DiscreteSlider widget allows selecting a value from a discrete list
or dictionary of values using a slider.

Reference: [https://panel.holoviz.org/reference/widgets/DiscreteSlider.html](https://panel.holoviz.org/reference/widgets/DiscreteSlider.html)

Example:

\>\>\>
DiscreteSlider(
...
value=0,
...
options=list(\[0,
1,
2,
4,
8,
16,
32,
64\]),
...
name="A
discrete value", ...
)

Attributes:
[labels](#panel.widgets.slider.DiscreteSlider.labels)
The list of labels to display

[values](#panel.widgets.slider.DiscreteSlider.values)
The list of option values

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The selected value of the slider. Updated when the handle is dragged.
Must be one of the options.

`value_throttled`` ``=`` ``Parameter(allow_None=True,`` ``constant=True,`` ``label='Value`` ``throttled')`
The value of the slider. Updated when the handle is released.

`options`` ``=`` ``ClassSelector(class_=(<class`` ``'dict'>,`` ``<class`` ``'list'>),`` ``default=[],`` ``label='Options')`
A list or dictionary of valid options.

`formatter`` ``=`` ``String(default='%.3g',`` ``label='Formatter')`
A custom format string. Separate from format parameter since formatting
is applied in Python, not via the bokeh TickFormatter.

property labels
The list of labels to display

property values
The list of option values

class panel.widgets.slider.EditableFloatSlider(\*, fixed_end, fixed_start, editable, end, start, step, value_throttled, format, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_EditableContinuousSlider`,
[FloatSlider](#panel.widgets.slider.FloatSlider)

The EditableFloatSlider widget allows selecting selecting a numeric
floating-point value within a set of bounds using a slider and for more
precise control offers an editable number input box.

Reference: [https://panel.holoviz.org/reference/widgets/EditableFloatSlider.html](https://panel.holoviz.org/reference/widgets/EditableFloatSlider.html)

Example:

\>\>\>
EditableFloatSlider(
...
value=1.0,
start=0.0,
end=2.0,
step=0.25,
name="A
float value" ... )

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, tooltips
>
> [class="reference internal"
> title="panel.widgets.slider.ContinuousSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.ContinuousSlider](#panel.widgets.slider.ContinuousSlider):
> format
>
> [title="panel.widgets.slider.FloatSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.FloatSlider](#panel.widgets.slider.FloatSlider):
> value, start, end, step, value_throttled
>
> `panel.widgets.slider._EditableContinuousSlider`:
> editable, show_value
>
>

`fixed_start`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``start')`
A fixed lower bound for the slider and input.

`fixed_end`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``end')`
A fixed upper bound for the slider and input.

class panel.widgets.slider.EditableIntSlider(\*, fixed_end, fixed_start, editable, end, start, step, value_throttled, format, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_EditableContinuousSlider`,
[IntSlider](#panel.widgets.slider.IntSlider)

The EditableIntSlider widget allows selecting selecting an integer value
within a set of bounds using a slider and for more precise control
offers an editable integer input box.

Reference: [https://panel.holoviz.org/reference/widgets/EditableIntSlider.html](https://panel.holoviz.org/reference/widgets/EditableIntSlider.html)

Example:

\>\>\>
EditableIntSlider(
...
value=2,
start=0,
end=5,
step=1,
name="An
integer value" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, tooltips
>
> [class="reference internal"
> title="panel.widgets.slider.ContinuousSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.ContinuousSlider](#panel.widgets.slider.ContinuousSlider):
> format
>
> [title="panel.widgets.slider.IntSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.IntSlider](#panel.widgets.slider.IntSlider):
> value, start, end, step, value_throttled
>
> `panel.widgets.slider._EditableContinuousSlider`:
> editable, show_value
>
>

`fixed_start`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``start')`
A fixed lower bound for the slider and input.

`fixed_end`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``end')`
A fixed upper bound for the slider and input.

class panel.widgets.slider.EditableRangeSlider(\*, editable, end, fixed_end, fixed_start, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget),
`_SliderBase`

The EditableRangeSlider widget allows selecting a floating-point range
using a slider with two handles and for more precise control also offers
a set of number input boxes.

Reference: [https://panel.holoviz.org/reference/widgets/EditableRangeSlider.html](https://panel.holoviz.org/reference/widgets/EditableRangeSlider.html)

Example:

\>\>\>
EditableRangeSlider(
...
value=(1.0,
1.5),
start=0.0,
end=2.0,
step=0.25,
name="A
tuple of floats" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, tooltips
>
>

`value`` ``=`` ``Range(default=(0,`` ``1),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2)`
Current range value. Updated when a handle is dragged.

`show_value`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Show`` ``value',`` ``readonly=True)`
Whether to show the widget value.

`value_throttled`` ``=`` ``Range(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled',`` ``length=2)`
The value of the slider. Updated when the handle is released.

`start`` ``=`` ``Number(default=0.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Lower bound of the range.

`end`` ``=`` ``Number(default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Upper bound of the range.

`fixed_start`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``start')`
A fixed lower bound for the slider and input.

`fixed_end`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Fixed`` ``end')`
A fixed upper bound for the slider and input.

`step`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
Slider and number input step.

`editable`` ``=`` ``Tuple(default=(True,`` ``True),`` ``label='Editable',`` ``length=2)`
Whether the lower and upper values are editable.

`format`` ``=`` ``ClassSelector(class_=(<class`` ``'str'>,`` ``<class`` ``'bokeh.models.formatters.TickFormatter'>),`` ``default='0.0[0000]',`` ``label='Format')`
Allows defining a custom format string or bokeh TickFormatter.

class panel.widgets.slider.FloatSlider(\*, end, start, step, value_throttled, format, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ContinuousSlider](#panel.widgets.slider.ContinuousSlider)

The FloatSlider widget allows selecting a floating-point value within a
set of bounds using a slider.

Reference:
[https://panel.holoviz.org/reference/widgets/FloatSlider.html](https://panel.holoviz.org/reference/widgets/FloatSlider.html)

Example:

\>\>\>
FloatSlider(value=0.5,
start=0.0,
end=1.0,
step=0.1,
name="Float
value")

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> [class="reference internal"
> title="panel.widgets.slider.ContinuousSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.ContinuousSlider](#panel.widgets.slider.ContinuousSlider):
> format
>
>

`value`` ``=`` ``Number(allow_None=True,`` ``default=0.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The selected floating-point value of the slider. Updated when the handle
is dragged.

`start`` ``=`` ``Number(default=0.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Number(default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`value_throttled`` ``=`` ``Number(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The value of the slider. Updated when the handle is released.

class panel.widgets.slider.IntRangeSlider(\*, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[RangeSlider](#panel.widgets.slider.RangeSlider)

The IntRangeSlider widget allows selecting an integer range using a
slider with two handles.

Reference: [https://panel.holoviz.org/reference/widgets/IntRangeSlider.html](https://panel.holoviz.org/reference/widgets/IntRangeSlider.html)

Example:

\>\>\>
IntRangeSlider(
...
value=(2,
4),
start=0,
end=10,
step=2,
name="A
tuple of integers" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> [title="panel.widgets.slider.RangeSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.RangeSlider](#panel.widgets.slider.RangeSlider):
> value, value_start, value_end, value_throttled, format
>
>

`start`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

class panel.widgets.slider.IntSlider(\*, end, start, step, value_throttled, format, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ContinuousSlider](#panel.widgets.slider.ContinuousSlider)

The IntSlider widget allows selecting an integer value within a set of
bounds using a slider.

Reference:
[https://panel.holoviz.org/reference/widgets/IntSlider.html](https://panel.holoviz.org/reference/widgets/IntSlider.html)

Example:

\>\>\>
IntSlider(value=5,
start=0,
end=10,
step=1,
name="Integer
Value")

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
> [class="reference internal"
> title="panel.widgets.slider.ContinuousSlider"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.slider.ContinuousSlider](#panel.widgets.slider.ContinuousSlider):
> format
>
>

`value`` ``=`` ``Integer(allow_None=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The selected integer value of the slider. Updated when the handle is
dragged.

`start`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`value_throttled`` ``=`` ``Integer(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The value of the slider. Updated when the handle is released

class panel.widgets.slider.RangeSlider(\*, end, format, start, step, value_throttled, bar_color, direction, orientation, show_value, tooltips, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_RangeSliderBase`

The RangeSlider widget allows selecting a floating-point range using a
slider with two handles.

Reference:
[https://panel.holoviz.org/reference/widgets/RangeSlider.html](https://panel.holoviz.org/reference/widgets/RangeSlider.html)

Example:

\>\>\>
RangeSlider(
...
value=(1.0,
1.5),
start=0.0,
end=2.0,
step=0.25,
name="A
tuple of floats" ...
)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.slider._SliderBase`:
> bar_color, direction, orientation, show_value, tooltips
>
>

`value`` ``=`` ``Range(default=(0,`` ``1),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2,`` ``nested_refs=True)`
The selected range as a tuple of values. Updated when a handle is
dragged.

`value_start`` ``=`` ``Number(constant=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``start',`` ``readonly=True)`
The lower value of the selected range.

`value_end`` ``=`` ``Number(constant=True,`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``end',`` ``readonly=True)`
The upper value of the selected range.

`value_throttled`` ``=`` ``Range(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled',`` ``length=2,`` ``nested_refs=True)`
The selected range as a tuple of floating point values. Updated when a
handle is released

`start`` ``=`` ``Number(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
The lower bound.

`end`` ``=`` ``Number(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
The upper bound.

`step`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`format`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'bokeh.models.formatters.TickFormatter'>),`` ``label='Format')`
A format string or bokeh TickFormatter.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
