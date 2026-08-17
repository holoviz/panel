# panel.widgets.indicators module

## Indicators

Indicators can be used to indicate status or progress

Check out the Panel gallery of indicators
[https://panel.holoviz.org/reference/index.html#indicators](https://panel.holoviz.org/reference/index.html#indicators)
for inspiration.

### How to use indicators

\>\>\>
pn.indicators.Number(
...
label='Rate',
value=72,
format='{value}%',
...
colors=\[(80,
'green'),
(100,
'red')\]
... )

class panel.widgets.indicators.BooleanIndicator(\*, throttle, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `Indicator`

BooleanIndicator is an abstract baseclass for indicators that visually
indicate a boolean value.

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Boolean(default=False,`` ``label='Value')`
Whether the indicator is active or not.

`throttle`` ``=`` ``Integer(allow_refs=True,`` ``default=500,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Throttle')`
” Throttles value change events, ensuring that they only toggle off
after a minimum time specified in milliseconds has passed.

class panel.widgets.indicators.BooleanStatus(\*, color, throttle, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [BooleanIndicator](#panel.widgets.indicators.BooleanIndicator)

The BooleanStatus is a boolean indicator providing a visual
representation of a boolean status as filled or non-filled circle.

If the value is set to True the indicator will be filled while setting
it to False will cause it to be non-filled.

Reference: [https://panel.holoviz.org/reference/indicators/BooleanStatus.html](https://panel.holoviz.org/reference/indicators/BooleanStatus.html)

Example:

\>\>\>
BooleanStatus(value=True,
color='primary',
width=100,
height=100)

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
> [class="reference internal"
> title="panel.widgets.indicators.BooleanIndicator"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.indicators.BooleanIndicator](#panel.widgets.indicators.BooleanIndicator):
> throttle
>
>

`value`` ``=`` ``Boolean(default=False,`` ``label='Value')`
Whether the indicator is active or not.

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
height of the circle.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of the circle.

`color`` ``=`` ``Selector(default='dark',`` ``label='Color',`` ``names={},`` ``objects=['primary',`` ``'secondary',`` ``'success',`` ``'info',`` ``'danger',`` ``'warning',`` ``'light',`` ``'dark'])`
The color of the circle, one of ‘primary’, ‘secondary’, ‘success’,
‘info’, ‘danger’, ‘warning’, ‘light’, ‘dark’

class panel.widgets.indicators.Dial(\*, annulus_width, background, bounds, colors, default_color, end_angle, format, label_color, nan_format, needle_color, needle_width, start_angle, tick_size, title_size, unfilled_color, value_size, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](#panel.widgets.indicators.ValueIndicator)

A Dial represents a value in some range as a position on an annular
dial. It is similar to a Gauge but more minimal visually.

Reference:
[https://panel.holoviz.org/reference/indicators/Dial.html](https://panel.holoviz.org/reference/indicators/Dial.html)

Example:

\>\>\>
Dial(label='Speed',
value=79,
format="{value}
km/h",
bounds=(0,
200),
colors=\[(0.4,
'green'),
(1,
'red')\])

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Number(allow_None=True,`` ``default=25,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
Value to indicate on the dial a value within the declared bounds.

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``default=250,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``default=250,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`annulus_width`` ``=`` ``Number(default=0.2,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Annulus`` ``width')`
Width of the radial annulus as a fraction of the total.

`background`` ``=`` ``Parameter(allow_None=True,`` ``label='Background')`
Background color of the component.

`bounds`` ``=`` ``Range(default=(0,`` ``100),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Bounds',`` ``length=2)`
The upper and lower bound of the dial.

`colors`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=<class`` ``'tuple'>,`` ``label='Colors')`
Color thresholds for the Dial, specified as a list of tuples of the
fractional threshold and the color to switch to.

`default_color`` ``=`` ``String(default='lightblue',`` ``label='Default`` ``color')`
Color of the radial annulus if not color thresholds are supplied.

`end_angle`` ``=`` ``Number(default=25,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End`` ``angle')`
Angle at which the dial ends.

`format`` ``=`` ``String(default='{value}%',`` ``label='Format')`
Formatting string for the value indicator and lower/upper bounds.

`label_color`` ``=`` ``String(default='black',`` ``label='Label`` ``color')`
Color for all extraneous labels.

`nan_format`` ``=`` ``String(default='-',`` ``label='Nan`` ``format')`
How to format nan values.

`needle_color`` ``=`` ``String(default='black',`` ``label='Needle`` ``color')`
Color of the Dial needle.

`needle_width`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Needle`` ``width')`
Radial width of the needle.

`start_angle`` ``=`` ``Number(default=-205,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start`` ``angle')`
Angle at which the dial starts.

`tick_size`` ``=`` ``String(allow_None=True,`` ``label='Tick`` ``size')`
Font size of the Dial min/max labels.

`title_size`` ``=`` ``String(allow_None=True,`` ``label='Title`` ``size')`
Font size of the Dial title.

`unfilled_color`` ``=`` ``String(default='whitesmoke',`` ``label='Unfilled`` ``color')`
Color of the unfilled region of the Dial.

`value_size`` ``=`` ``String(allow_None=True,`` ``label='Value`` ``size')`
Font size of the Dial value label.

class panel.widgets.indicators.Gauge(\*, annulus_width, bounds, colors, custom_opts, end_angle, format, num_splits, show_labels, show_ticks, start_angle, title_size, tooltip_format, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](#panel.widgets.indicators.ValueIndicator)

A Gauge represents a value in some range as a position on speedometer or
gauge. It is similar to a Dial but visually a lot busier. Requires the
ECharts extension to be loaded.

Reference:
[https://panel.holoviz.org/reference/indicators/Gauge.html](https://panel.holoviz.org/reference/indicators/Gauge.html)

Example:

\>\>\>
pn.extension('echarts')
\>\>\>
Gauge(label='Speed',
value=79,
bounds=(0,
200),
colors=\[(0.4,
'green'),
(1,
'red')\])

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Number(allow_None=True,`` ``default=25,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
Value to indicate on the gauge a value within the declared bounds.

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`annulus_width`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Annulus`` ``width')`
Width of the gauge annulus.

`bounds`` ``=`` ``Range(default=(0,`` ``100),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Bounds',`` ``length=2)`
The upper and lower bound of the dial.

`colors`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=<class`` ``'tuple'>,`` ``label='Colors')`
Color thresholds for the Gauge, specified as a list of tuples of the
fractional threshold and the color to switch to.

`custom_opts`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Custom`` ``opts')`
Additional options to pass to the ECharts Gauge definition.

`end_angle`` ``=`` ``Number(default=-45,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End`` ``angle')`
Angle at which the gauge ends.

`format`` ``=`` ``String(default='{value}%',`` ``label='Format')`
Formatting string for the value indicator.

`num_splits`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Num`` ``splits')`
Number of splits along the gauge.

`show_ticks`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``ticks')`
Whether to show ticks along the dials.

`show_labels`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``labels')`
Whether to show tick labels along the dials.

`start_angle`` ``=`` ``Number(default=225,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start`` ``angle')`
Angle at which the gauge starts.

`tooltip_format`` ``=`` ``String(default='{b}`` ``:`` ``{c}%',`` ``label='Tooltip`` ``format')`
Formatting string for the hover tooltip.

`title_size`` ``=`` ``Integer(allow_None=True,`` ``default=18,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Title`` ``size')`
Size of title font.

class panel.widgets.indicators.LinearGauge(\*, bounds, colors, default_color, format, horizontal, nan_format, needle_color, show_boundaries, tick_size, title_size, unfilled_color, value_size, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](#panel.widgets.indicators.ValueIndicator)

A LinearGauge represents a value in some range as a position on an
linear scale. It is similar to a Dial/Gauge but visually more compact.

Reference: [https://panel.holoviz.org/reference/indicators/LinearGauge.html](https://panel.holoviz.org/reference/indicators/LinearGauge.html)

Example:

\>\>\>
LinearGauge(value=30,
default_color='red',
bounds=(0,
100))

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> margin, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Number(allow_None=True,`` ``default=25,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
Value to indicate on the dial a value within the declared bounds.

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``default=125,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`bounds`` ``=`` ``Range(default=(0,`` ``100),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Bounds',`` ``length=2)`
The upper and lower bound of the gauge.

`default_color`` ``=`` ``String(default='lightblue',`` ``label='Default`` ``color')`
Color of the radial annulus if not color thresholds are supplied.

`colors`` ``=`` ``Parameter(allow_None=True,`` ``label='Colors')`
Color thresholds for the gauge, specified as a list of tuples of the
fractional threshold and the color to switch to.

`format`` ``=`` ``String(default='{value:.2f}%',`` ``label='Format')`
Formatting string for the value indicator and lower/upper bounds.

`horizontal`` ``=`` ``Boolean(default=False,`` ``label='Horizontal')`
Whether to display the linear gauge horizontally.

`nan_format`` ``=`` ``String(default='-',`` ``label='Nan`` ``format')`
How to format nan values.

`needle_color`` ``=`` ``String(default='black',`` ``label='Needle`` ``color')`
Color of the gauge needle.

`show_boundaries`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``boundaries')`
Whether to show the boundaries between colored regions.

`unfilled_color`` ``=`` ``String(default='whitesmoke',`` ``label='Unfilled`` ``color')`
Color of the unfilled region of the LinearGauge.

`title_size`` ``=`` ``String(allow_None=True,`` ``label='Title`` ``size')`
Font size of the gauge title.

`tick_size`` ``=`` ``String(allow_None=True,`` ``label='Tick`` ``size')`
Font size of the gauge tick labels.

`value_size`` ``=`` ``String(allow_None=True,`` ``label='Value`` ``size')`
Font size of the gauge value label.

class panel.widgets.indicators.LoadingSpinner(\*, bgcolor, color, size, throttle, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [BooleanIndicator](#panel.widgets.indicators.BooleanIndicator)

The LoadingSpinner is a boolean indicator providing a visual
representation of the loading status.

If the value is set to True the spinner will rotate while setting it to
False will disable the rotating segment.

Reference: [https://panel.holoviz.org/reference/indicators/LoadingSpinner.html](https://panel.holoviz.org/reference/indicators/LoadingSpinner.html)

Example:

\>\>\>
LoadingSpinner(value=True,
color='primary',
bgcolor='light',
width=100,
height=100)

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
> [class="reference internal"
> title="panel.widgets.indicators.BooleanIndicator"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.indicators.BooleanIndicator](#panel.widgets.indicators.BooleanIndicator):
> throttle
>
>

`value`` ``=`` ``Boolean(allow_refs=True,`` ``default=False,`` ``label='Value')`
Whether the indicator is active or not.

`bgcolor`` ``=`` ``Selector(allow_refs=True,`` ``default='light',`` ``label='Bgcolor',`` ``names={},`` ``objects=['dark',`` ``'light'])`
The color of spinner background segment, either ‘light’ or ‘dark’.

`color`` ``=`` ``Selector(allow_refs=True,`` ``default='dark',`` ``label='Color',`` ``names={},`` ``objects=['primary',`` ``'secondary',`` ``'success',`` ``'info',`` ``'danger',`` ``'warning',`` ``'light',`` ``'dark'])`
The color of the spinning segment, one of ‘primary’, ‘secondary’,
‘success’, ‘info’, ‘warn’, ‘danger’, ‘light’, ‘dark’.

`size`` ``=`` ``Integer(allow_refs=True,`` ``default=125,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
Size of the spinner in pixels.

class panel.widgets.indicators.Number(\*, colors, default_color, font_size, format, nan_format, title_size, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](#panel.widgets.indicators.ValueIndicator)

The Number indicator renders the value as text optionally colored
according to the colors thresholds.

Reference:
[https://panel.holoviz.org/reference/indicators/Number.html](https://panel.holoviz.org/reference/indicators/Number.html)

Example:

\>\>\>
Number(label='Rate',
value=72,
format='{value}%',
colors=\[(80,
'green'),
(100,
'red')\]

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
> [class="reference internal"
> title="panel.widgets.indicators.ValueIndicator"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.indicators.ValueIndicator](#panel.widgets.indicators.ValueIndicator):
> value
>
>

`default_color`` ``=`` ``String(default='currentcolor',`` ``label='Default`` ``color')`
The color of the Number indicator if no colors are provided

`colors`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=<class`` ``'tuple'>,`` ``label='Colors')`
Color thresholds for the Number indicator, specified as a tuple of the
absolute thresholds and the color to switch to.

`format`` ``=`` ``String(default='{value}',`` ``label='Format')`
A formatter string which accepts a {value}.

`font_size`` ``=`` ``String(default='54pt',`` ``label='Font`` ``size')`
The size of number itself.

`nan_format`` ``=`` ``String(default='-',`` ``label='Nan`` ``format')`
How to format nan values.

`title_size`` ``=`` ``String(default='18pt',`` ``label='Title`` ``size')`
The size of the title given by the label.

class panel.widgets.indicators.Progress(\*, active, bar_color, max, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](#panel.widgets.indicators.ValueIndicator)

The Progress widget displays the progress towards some target based on
the current value and the max value.

If no value is set, the Progress widget is in indeterminate mode and
will animate depending on whether it is active or not. A more beautiful
indicator for this use case is the LoadingSpinner.

Reference:
[https://panel.holoviz.org/reference/indicators/Progress.html](https://panel.holoviz.org/reference/indicators/Progress.html)

Example:

\>\>\>
Progress(value=20,
max=100,
bar_color="primary")

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, disabled
>
>

`value`` ``=`` ``Integer(allow_None=True,`` ``bounds=(-1,`` ``None),`` ``default=-1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The current value of the progress bar. If set to -1 the progress bar
will be indeterminate and animate depending on the active parameter.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`sizing_mode`` ``=`` ``Selector(label='Sizing`` ``mode',`` ``names={},`` ``objects=['fixed',`` ``'stretch_width',`` ``'stretch_height',`` ``'stretch_both',`` ``'scale_width',`` ``'scale_height',`` ``'scale_both',`` ``None])`
How the component should size itself. This is a high-level setting for
maintaining width and height of the component. To gain more fine grained
control over sizing, use `width_policy`,
`height_policy` and
`aspect_ratio` instead (those take precedence
over `sizing_mode`).
`"fixed"` Component is not responsive. It will
retain its original width and height regardless of any subsequent
browser window resize events. `"stretch_width"`
Component will responsively resize to stretch to the available width,
without maintaining any aspect ratio. The height of the component
depends on the type of the component and may be fixed or fit to
component’s contents. `"stretch_height"`
Component will responsively resize to stretch to the available height,
without maintaining any aspect ratio. The width of the component depends
on the type of the component and may be fixed or fit to component’s
contents. `"stretch_both"` Component is
completely responsive, independently in width and height, and will
occupy all the available horizontal and vertical space, even if this
changes the aspect ratio of the component.
`"scale_width"` Component will responsively
resize to stretch to the available width, while maintaining the original
or provided aspect ratio. `"scale_height"`
Component will responsively resize to stretch to the available height,
while maintaining the original or provided aspect ratio.
`"scale_both"` Component will responsively
resize to both the available width and height, while maintaining the
original or provided aspect ratio.

`active`` ``=`` ``Boolean(default=True,`` ``label='Active')`
If no value is set the active property toggles animation of the progress
bar on and off.

`bar_color`` ``=`` ``Selector(default='success',`` ``label='Bar`` ``color',`` ``names={},`` ``objects=['primary',`` ``'secondary',`` ``'success',`` ``'info',`` ``'danger',`` ``'warning',`` ``'light',`` ``'dark'])`
The color of the bar, one of ‘primary’, ‘secondary’, ‘success’, ‘info’,
‘warning’, ‘danger’, ‘light’, ‘dark’.

`max`` ``=`` ``Integer(default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max')`
The maximum value of the progress bar.

sizing_mode: t.Literal\['fixed', 'stretch_width', 'stretch_height', 'stretch_both', 'scale_width', 'scale_height', 'scale_both'\] \| None = None

class panel.widgets.indicators.String(\*, default_color, font_size, title_size, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [ValueIndicator](#panel.widgets.indicators.ValueIndicator)

The String indicator renders a string with a title.

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``String(allow_None=True,`` ``label='Value')`
The string to display

`default_color`` ``=`` ``String(default='currentcolor',`` ``label='Default`` ``color')`
The color of the indicator if no colors are provided

`font_size`` ``=`` ``String(default='54pt',`` ``label='Font`` ``size')`
The size of number itself.

`title_size`` ``=`` ``String(default='18pt',`` ``label='Title`` ``size')`
The size of the title given by the label.

class panel.widgets.indicators.TooltipIcon(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The TooltipIcon displays a small ? icon. When you hover over the ? icon,
the value will display.

Use the TooltipIcon to provide

- helpful information to users without taking up a lot of screen space

- tooltips next to Panel widgets that do not support tooltips yet.

Reference: [https://panel.holoviz.org/reference/indicators/TooltipIcon.html](https://panel.holoviz.org/reference/indicators/TooltipIcon.html)

Example:

\>\>\>
pn.widgets.TooltipIcon(value="This
is a simple tooltip by using a string")

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> aspect_ratio, css_classes, design, min_width, min_height, max_width,
> max_height, styles, stylesheets, tags, width_policy, height_policy,
> sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``ClassSelector(class_=(<class`` ``'str'>,`` ``<class`` ``'bokeh.models.ui.tooltips.Tooltip'>),`` ``default='Description',`` ``label='Value')`
The description in the tooltip.

`align`` ``=`` ``Align(default='center',`` ``label='Align')`
Whether the object should be aligned with the start, end or center of
its container. If set as a tuple it will declare (vertical, horizontal)
alignment.

class panel.widgets.indicators.Tqdm(\*, layout, lock, max, progress, text, text_pane, write_to_console, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `Indicator`

The Tqdm indicator wraps the well known tqdm progress indicator and
displays the progress towards some target in your Panel app.

Reference:
[https://panel.holoviz.org/reference/indicators/Tqdm.html](https://panel.holoviz.org/reference/indicators/Tqdm.html)

Example:

\>\>\> tqdm
=
Tqdm()
\>\>\> for
i in
tqdm(range(0,10),
desc="My
loop",
leave=True,
colour='#666666'):
...
time.sleep(timeout)

Methods

|  |  |
|----|----|
| `get_lock`() |  |
| [reset](#panel.widgets.indicators.Tqdm.reset)() | Resets the parameters |
| `set_lock`(lock) |  |

|            |     |
|------------|-----|
| **pandas** |     |

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Integer(bounds=(-1,`` ``None),`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The current value of the progress bar. If set to -1 the progress bar
will be indeterminate and animate depending on the active parameter.

`margin`` ``=`` ``Margin(allow_None=True,`` ``default=0,`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=400,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`layout`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'panel.layout.base.Column'>,`` ``<class`` ``'panel.layout.base.Row'>),`` ``constant=True,`` ``label='Layout')`
The layout for the text and progress indicator.

`lock`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'object'>,`` ``label='Lock')`
The multithreading.Lock or multiprocessing.Lock object to be used by
Tqdm.

`max`` ``=`` ``Integer(default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max')`
The maximum value of the progress bar.

`progress`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.widgets.indicators.Progress'>,`` ``label='Progress')`
The Progress indicator used to display the progress.

`text`` ``=`` ``String(default='',`` ``label='Text')`
The current tqdm style progress text.

`text_pane`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.pane.markup.Str'>,`` ``label='Text`` ``pane')`
The pane to display the text to.

`write_to_console`` ``=`` ``Boolean(default=False,`` ``label='Write`` ``to`` ``console')`
Whether or not to also write to the console.

reset()
Resets the parameters

class panel.widgets.indicators.Trend(\*, data, layout, neg_color, plot_color, plot_type, plot_x, plot_y, pos_color, value_change, selection, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `SyncableData`,
`Indicator`

The Trend indicator enables the user to display a dashboard kpi card.

The card can be layout out as:

- a column (text and plot on top of each other) or a row (text and

- plot after each other)

Reference:
[https://panel.holoviz.org/reference/indicators/Trend.html](https://panel.holoviz.org/reference/indicators/Trend.html)

Example:

\>\>\> data
=
{'x':
np.arange(50),
'y':
np.random.randn(50).cumsum()}
\>\>\>
Trend(label='Price',
data=data,
plot_type='area',
width=200,
height=200)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.reactive.SyncableData`: selection
>
>

`label`` ``=`` ``String(default='',`` ``label='Label')`
The label or a short description of the card.

`value`` ``=`` ``Parameter(default='auto',`` ``label='Value')`
The primary value to be displayed.

`sizing_mode`` ``=`` ``Selector(label='Sizing`` ``mode',`` ``names={},`` ``objects=['fixed',`` ``'stretch_width',`` ``'stretch_height',`` ``'stretch_both',`` ``'scale_width',`` ``'scale_height',`` ``'scale_both',`` ``None])`
How the component should size itself. This is a high-level setting for
maintaining width and height of the component. To gain more fine grained
control over sizing, use `width_policy`,
`height_policy` and
`aspect_ratio` instead (those take precedence
over `sizing_mode`).
`"fixed"` Component is not responsive. It will
retain its original width and height regardless of any subsequent
browser window resize events. `"stretch_width"`
Component will responsively resize to stretch to the available width,
without maintaining any aspect ratio. The height of the component
depends on the type of the component and may be fixed or fit to
component’s contents. `"stretch_height"`
Component will responsively resize to stretch to the available height,
without maintaining any aspect ratio. The width of the component depends
on the type of the component and may be fixed or fit to component’s
contents. `"stretch_both"` Component is
completely responsive, independently in width and height, and will
occupy all the available horizontal and vertical space, even if this
changes the aspect ratio of the component.
`"scale_width"` Component will responsively
resize to stretch to the available width, while maintaining the original
or provided aspect ratio. `"scale_height"`
Component will responsively resize to stretch to the available height,
while maintaining the original or provided aspect ratio.
`"scale_both"` Component will responsively
resize to both the available width and height, while maintaining the
original or provided aspect ratio.

`data`` ``=`` ``Parameter(allow_None=True,`` ``label='Data')`
The plot data declared as a dictionary of arrays or a DataFrame.

`layout`` ``=`` ``Selector(default='column',`` ``label='Layout',`` ``names={},`` ``objects=['column',`` ``'row'])`
The layout of the indicator, either a column (text and plot on top of
each other) or a row (text and plot after each other).

`plot_x`` ``=`` ``String(default='x',`` ``label='Plot`` ``x')`
The name of the key in the plot_data to use on the x-axis.

`plot_y`` ``=`` ``String(default='y',`` ``label='Plot`` ``y')`
The name of the key in the plot_data to use on the y-axis.

`plot_color`` ``=`` ``String(default='#428bca',`` ``label='Plot`` ``color')`
The color to use in the plot.

`plot_type`` ``=`` ``Selector(default='bar',`` ``label='Plot`` ``type',`` ``names={},`` ``objects=['line',`` ``'step',`` ``'area',`` ``'bar'])`
The plot type to render the plot data as.

`pos_color`` ``=`` ``String(default='#5cb85c',`` ``label='Pos`` ``color')`
The color used to indicate a positive change.

`neg_color`` ``=`` ``String(default='#d9534f',`` ``label='Neg`` ``color')`
The color used to indicate a negative change.

`value_change`` ``=`` ``Parameter(default='auto',`` ``label='Value`` ``change')`
A secondary value. For example the change in percent.

sizing_mode: t.Literal\['fixed', 'stretch_width', 'stretch_height', 'stretch_both', 'scale_width', 'scale_height', 'scale_both'\] \| None = None

class panel.widgets.indicators.ValueIndicator(**params: Any)
Bases: `Indicator`

A ValueIndicator provides a visual representation for a numeric value.

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
> height_policy, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
> `panel.widgets.indicators.Indicator`:
> sizing_mode
>
>

`value`` ``=`` ``Number(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The widget value which the widget type resolves to when used as a
reactive param reference.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
