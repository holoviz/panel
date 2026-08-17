# panel.widgets.input module

The input widgets generally allow entering arbitrary information into a
text field or similar.

class panel.widgets.input.ArrayInput(\*, max_array_size, description, placeholder, serializer, type, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[LiteralInput](#panel.widgets.input.LiteralInput)

The ArrayInput allows rendering and editing NumPy arrays in a text input
widget.

Arrays larger than the max_array_size will be summarized and editing
will be disabled.

Reference:
[https://panel.holoviz.org/reference/widgets/ArrayInput.html](https://panel.holoviz.org/reference/widgets/ArrayInput.html)

Example:

\>\>\> To
be determined
...

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
> height, margin, disabled
>
> [title="panel.widgets.input.LiteralInput"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets. input .LiteralInput](#panel.widgets.input.LiteralInput):
> value, width, description, placeholder, serializer, type
>
>

`max_array_size`` ``=`` ``Integer(default=1000,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``array`` ``size')`
Arrays larger than this limit will be allowed in Python but will not be
serialized into JavaScript. Although such large arrays will thus not be
editable in the widget, such a restriction helps avoid overwhelming the
browser and lets other widgets remain usable.

class panel.widgets.input.Checkbox(**params: Any)
Bases: `_BooleanWidget`

The Checkbox allows toggling a single condition between True/False
states by ticking a checkbox.

This widget is interchangeable with the Toggle widget.

Reference:
[https://panel.holoviz.org/reference/widgets/Checkbox.html](https://panel.holoviz.org/reference/widgets/Checkbox.html)

Example:

\>\>\>
Checkbox(name='Works
with the tools you know and love',
value=True)

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
> `panel.widgets.input._BooleanWidget`: value
>
>

class panel.widgets.input.ColorPicker(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The ColorPicker widget allows selecting a hexadecimal RGB color value
using the browser’s color-picking widget.

Reference:
[https://panel.holoviz.org/reference/widgets/ColorPicker.html](https://panel.holoviz.org/reference/widgets/ColorPicker.html)

Example:

\>\>\>
ColorPicker(name='Color',
value='#99ef78')

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
> height, margin, disabled
>
>

`value`` ``=`` ``Color(allow_None=True,`` ``allow_named=True,`` ``label='Value')`
The selected color

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=52,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

class panel.widgets.input.DatePicker(\*, description, disabled_dates, enabled_dates, end, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The DatePicker allows selecting a date value using a text box and a
date-picking utility.

Reference:
[https://panel.holoviz.org/reference/widgets/DatePicker.html](https://panel.holoviz.org/reference/widgets/DatePicker.html)

Example:

\>\>\>
DatePicker(
...
value=date(2025,1,1),
...
start=date(2025,1,1),
end=date(2025,12,31),
...
name='Date'
... )

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
> height, margin, disabled
>
>

`value`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The current value

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`start`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Inclusive lower bound of the allowed date selection

`end`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Inclusive upper bound of the allowed date selection

`disabled_dates`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'datetime.date'>,`` ``<class`` ``'str'>),`` ``label='Disabled`` ``dates')`
Dates to make unavailable for selection; others will be available.

`enabled_dates`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'datetime.date'>,`` ``<class`` ``'str'>),`` ``label='Enabled`` ``dates')`
Dates to make available for selection; others will be unavailable.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

class panel.widgets.input.DateRangePicker(\*, description, disabled_dates, enabled_dates, end, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The DateRangePicker allows selecting a date range using a text box and a
date-picking utility.

Reference: [https://panel.holoviz.org/reference/widgets/DateRangePicker.html](https://panel.holoviz.org/reference/widgets/DateRangePicker.html)

Example:

\>\>\>
DateRangePicker(
...
value=(date(2025,1,1),
date(2025,1,5)),
...
start=date(2025,1,1),
end=date(2025,12,31),
...
name='Date
range' ... )

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
> height, margin, disabled
>
>

`value`` ``=`` ``DateRange(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2)`
The current value

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`start`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Inclusive lower bound of the allowed date selection

`end`` ``=`` ``CalendarDate(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Inclusive upper bound of the allowed date selection

`disabled_dates`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'datetime.date'>,`` ``<class`` ``'str'>),`` ``label='Disabled`` ``dates')`
Dates to make unavailable for selection; others will be available.

`enabled_dates`` ``=`` ``List(allow_None=True,`` ``bounds=(0,`` ``None),`` ``item_type=(<class`` ``'datetime.date'>,`` ``<class`` ``'str'>),`` ``label='Enabled`` ``dates')`
Dates to make available for selection; others will be unavailable.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

class panel.widgets.input.DatetimeInput(\*, end, format, start, description, placeholder, serializer, type, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[LiteralInput](#panel.widgets.input.LiteralInput)

The DatetimeInput allows specifying Python datetime like values using a
text input widget.

An optional type may be declared.

Reference:
[https://panel.holoviz.org/reference/widgets/DatetimeInput.html](https://panel.holoviz.org/reference/widgets/DatetimeInput.html)

Example:

\>\>\>
DatetimeInput(name='Datetime',
value=datetime(2019,
2,
8))

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
> height, margin, disabled
>
> [title="panel.widgets.input.LiteralInput"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets. input .LiteralInput](#panel.widgets.input.LiteralInput):
> width, description, placeholder, serializer, type
>
>

`value`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The current value

`start`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Inclusive lower bound of the allowed date selection

`end`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Inclusive upper bound of the allowed date selection

`format`` ``=`` ``String(default='%Y-%m-%d`` ``%H:%M:%S',`` ``label='Format')`
Datetime format used for parsing and formatting the datetime.

type
alias of `datetime`

class panel.widgets.input.DatetimePicker(\*, mode, allow_input, as_numpy_datetime64, description, disabled_dates, enable_seconds, enable_time, enabled_dates, end, military_time, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_DatetimePickerBase`

The DatetimePicker allows selecting selecting a datetime value using a
textbox and a datetime-picking utility.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimePicker.html](https://panel.holoviz.org/reference/widgets/DatetimePicker.html)

Example:

\>\>\>
DatetimePicker(
...
value=datetime(2025,1,1,22,0),
...
start=date(2025,1,1),
end=date(2025,12,31),
...
military_time=True,
name='Date
and time' ... )

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
> height, margin, disabled
>
> `panel.widgets.input._DatetimePickerBase`:
> width, allow_input, disabled_dates, enabled_dates, enable_time,
> enable_seconds, end, military_time, start, description,
> as_numpy_datetime64
>
>

`value`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value')`
The widget value which the widget type resolves to when used as a
reactive param reference.

`mode`` ``=`` ``String(constant=True,`` ``default='single',`` ``label='Mode')`
The mode of the datetime picker, which is always ‘single’ for this
widget.

class panel.widgets.input.DatetimeRangeInput(\*, end, format, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget)

The DatetimeRangeInput widget allows selecting a datetime range using
two DatetimeInput widgets, which return a tuple range.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimeRangeInput.html](https://panel.holoviz.org/reference/widgets/DatetimeRangeInput.html)

Example:

\>\>\>
DatetimeRangeInput(
...
name='Datetime
Range', ...
value=(datetime(2017,
1,
1),
datetime(2018,
1,
10)),
...
start=datetime(2017,
1,
1),
end=datetime(2019,
1,
1), ...
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
>

`value`` ``=`` ``Tuple(default=(None,`` ``None),`` ``label='Value',`` ``length=2)`
The current value

`start`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Start')`
Inclusive lower bound of the allowed date selection

`end`` ``=`` ``Date(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='End')`
Inclusive upper bound of the allowed date selection

`format`` ``=`` ``String(default='%Y-%m-%d`` ``%H:%M:%S',`` ``label='Format')`
Datetime format used for parsing and formatting the datetime.

class panel.widgets.input.DatetimeRangePicker(\*, mode, allow_input, as_numpy_datetime64, description, disabled_dates, enable_seconds, enable_time, enabled_dates, end, military_time, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_DatetimePickerBase`

The DatetimeRangePicker allows selecting selecting a datetime range
using a text box and a datetime-range-picking utility.

Reference: [https://panel.holoviz.org/reference/widgets/DatetimeRangePicker.html](https://panel.holoviz.org/reference/widgets/DatetimeRangePicker.html)

Example:

\>\>\>
DatetimeRangePicker(
...
value=(datetime(2025,1,1,22,0),
datetime(2025,1,2,22,0)),
...
start=date(2025,1,1),
end=date(2025,12,31),
...
military_time=True,
name='Datetime
Range' ... )

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
> height, margin, disabled
>
> `panel.widgets.input._DatetimePickerBase`:
> width, allow_input, disabled_dates, enabled_dates, enable_time,
> enable_seconds, end, military_time, start, description,
> as_numpy_datetime64
>
>

`value`` ``=`` ``DateRange(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value',`` ``length=2)`
The current value

`mode`` ``=`` ``String(constant=True,`` ``default='range',`` ``label='Mode')`
The mode of the datetime picker, which is always ‘range’ for this
widget.

class panel.widgets.input.FileDropper(\*, accepted_filetypes, chunk_size, layout, max_file_size, max_files, max_total_file_size, mime_type, multiple, previews, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The FileDropper allows the user to upload one or more files to the
server.

It is similar to the FileInput widget but additionally adds support for
chunked uploads, making it possible to upload large files. The UI also
supports previews for image files. Unlike FileInput the uploaded files
are stored as dictionary of bytes object indexed by the filename.

Reference:
[https://panel.holoviz.org/reference/widgets/FileDropper.html](https://panel.holoviz.org/reference/widgets/FileDropper.html)

Example:

\>\>\>
FileDropper(accepted_filetypes=\['image/\*'\],
multiple=True)

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
> height, margin, disabled
>
>

`value`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Value')`
A dictionary containing the uploaded file(s) as bytes or string objects
indexed by the filename. Files that have a text/\* mimetype will
automatically be decoded as utf-8.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`accepted_filetypes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Accepted`` ``filetypes')`
List of accepted file types. Can be mime types, file extensions or wild
cards.For instance \[‘image/[\*](#id1)’\] will accept all images.
\[‘.png’, ‘image/jpeg’\] will only accepts PNGs and JPEGs.

`chunk_size`` ``=`` ``Integer(default=10000000,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Chunk`` ``size')`
Size in bytes per chunk transferred across the WebSocket.

`layout`` ``=`` ``Selector(label='Layout',`` ``names={},`` ``objects=['circle',`` ``'compact',`` ``'integrated'])`
Compact mode removes padding. Integrated mode renders FilePond as part
of a bigger element. Circle mode keeps FilePond’s per-file action
buttons and upload progress indicator inside the circular drop area.

`max_file_size`` ``=`` ``String(allow_None=True,`` ``label='Max`` ``file`` ``size')`
Maximum size of a file as a string with units given in KB or MB, e.g.
5MB or 750KB.

`max_files`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``files')`
Maximum number of files that can be uploaded if multiple=True.

`max_total_file_size`` ``=`` ``String(allow_None=True,`` ``label='Max`` ``total`` ``file`` ``size')`
Maximum size of all uploaded files, as a string with units given in KB
or MB, e.g. 5MB or 750KB.

`mime_type`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Mime`` ``type')`
A dictionary containing the mimetypes for each of the uploaded files
indexed by their filename.

`multiple`` ``=`` ``Boolean(default=False,`` ``label='Multiple')`
Whether to allow uploading multiple files.

`previews`` ``=`` ``ListSelector(default=['image',`` ``'pdf'],`` ``label='Previews',`` ``names={},`` ``objects=['image',`` ``'pdf'])`
List of previews to enable in the FileDropper. The following previews
are available: - image: Adds support for image previews. - pdf: Adds
support for PDF previews.

class panel.widgets.input.FileInput(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The FileInput allows the user to upload one or more files to the server.

It makes the filename, MIME type and (bytes) content available in
Python.

Please note

- you can in fact *drag and drop* files onto the FileInput.

- you easily save the files using the save method.

Reference:
[https://panel.holoviz.org/reference/widgets/FileInput.html](https://panel.holoviz.org/reference/widgets/FileInput.html)

Example:

\>\>\>
FileInput(accept='.png,.jpeg',
multiple=True)

Methods

|  |  |
|----|----|
| [clear](#panel.widgets.input.FileInput.clear)() | Clear the file(s) in the FileInput widget |
| [save](#panel.widgets.input.FileInput.save)(filename) | Saves the uploaded FileInput data object(s) to file(s) or BytesIO object(s). |

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
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The uploaded file(s) stored as a single bytes object if multiple is
False or a list of bytes otherwise.

`accept`` ``=`` ``String(allow_None=True,`` ``label='Accept')`
A comma separated string of all extension types that should be
supported.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component rendered as a
tooltip icon.

`directory`` ``=`` ``Boolean(default=False,`` ``label='Directory')`
Whether to allow selection of directories instead of files. The filename
will be relative paths to the uploaded directory. .. note:: When a
directory is uploaded it will give add a confirmation pop up. The
confirmation pop up cannot be disabled, as this is a security feature in
the browser. .. note:: The accept parameter only works with file
extension. When using accept with directory, the number of files
reported will be the total amount of files, not the filtered.

`filename`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'list'>),`` ``label='Filename')`
Name of the uploaded file(s).

`mime_type`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'list'>),`` ``label='Mime`` ``type')`
Mimetype of the uploaded file(s).

`multiple`` ``=`` ``Boolean(default=False,`` ``label='Multiple')`
Whether to allow uploading multiple files. If enabled value parameter
will return a list.

clear()
Clear the file(s) in the FileInput widget

save(filename)
Saves the uploaded FileInput data object(s) to file(s) or BytesIO
object(s).

Parameters:
**filename (str or list\[str\]): File path or file-like object**

class panel.widgets.input.FloatInput(\*, step, value_throttled, page_step_multiplier, wheel_wait, mode, description, end, format, placeholder, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SpinnerBase`,
`_FloatInputBase`

The FloatInput allows selecting a floating point value using a spinbox.

It behaves like a slider except that the lower and upper bounds are
optional and a specific value can be entered. The value can be changed
using the keyboard (up, down, page up, page down), mouse wheel and arrow
buttons.

Reference:
[https://panel.holoviz.org/reference/widgets/FloatInput.html](https://panel.holoviz.org/reference/widgets/FloatInput.html)

Example:

\>\>\>
FloatInput(name='Value',
value=5.,
step=1e-1,
start=0,
end=10)

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
> height, margin, disabled
>
> `panel.widgets.input._NumericInputBase`:
> description, format
>
> `panel.widgets.input._FloatInputBase`: value,
> start, end, mode
>
> `panel.widgets.input._SpinnerBase`: width,
> page_step_multiplier, wheel_wait
>
>

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
Placeholder when the value is empty.

`step`` ``=`` ``Number(default=0.1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`value_throttled`` ``=`` ``Number(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The current value. Updates only on \<enter\> or when the widget looses
focus.

class panel.widgets.input.IntInput(\*, step, value_throttled, page_step_multiplier, wheel_wait, mode, description, end, format, placeholder, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SpinnerBase`,
`_IntInputBase`

The IntInput allows selecting an integer value using a spinbox.

It behaves like a slider except that lower and upper bounds are optional
and a specific value can be entered. The value can be changed using the
keyboard (up, down, page up, page down), mouse wheel and arrow buttons.

Reference:
[https://panel.holoviz.org/reference/widgets/IntInput.html](https://panel.holoviz.org/reference/widgets/IntInput.html)

Example:

\>\>\>
IntInput(name='Value',
value=100,
start=0,
end=1000,
step=10)

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
> height, margin, disabled
>
> `panel.widgets.input._NumericInputBase`:
> description, format
>
> `panel.widgets.input._IntInputBase`: value,
> start, end, mode
>
> `panel.widgets.input._SpinnerBase`: width,
> placeholder, page_step_multiplier, wheel_wait
>
>

`step`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Step')`
The step size.

`value_throttled`` ``=`` ``Integer(allow_None=True,`` ``constant=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Value`` ``throttled')`
The current value. Updates only on \<enter\> or when the widget looses
focus.

class panel.widgets.input.LiteralInput(\*, description, placeholder, serializer, type, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The LiteralInput allows declaring Python literals using a text input
widget.

A *literal* is some specific primitive value of type str , int, float,
bool etc or a dict, list, tuple, set etc of primitive values.

Optionally the literal type may be declared.

Reference:
[https://panel.holoviz.org/reference/widgets/LiteralInput.html](https://panel.holoviz.org/reference/widgets/LiteralInput.html)

Example:

\>\>\>
LiteralInput(name='Dictionary',
value={'key':
\[1,
2,
3\]},
type=dict)

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
> height, margin, disabled
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The widget value which the widget type resolves to when used as a
reactive param reference.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
Placeholder for empty input field.

`serializer`` ``=`` ``Selector(default='ast',`` ``label='Serializer',`` ``names={},`` ``objects=['ast',`` ``'json'])`
The serialization (and deserialization) method to use. ‘ast’ uses
ast.literal_eval and ‘json’ uses json.loads and json.dumps.

`type`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'type'>,`` ``<class`` ``'tuple'>),`` ``label='Type')`
A Python literal type (e.g. list, dict, set, int, float, bool, str).

class panel.widgets.input.NumberInput(\*, page_step_multiplier, wheel_wait, description, end, format, placeholder, start, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_SpinnerBase`

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
> height, margin, disabled
>
> `panel.widgets.input._NumericInputBase`:
> value, description, format, start, end
>
> `panel.widgets.input._SpinnerBase`: width,
> placeholder, page_step_multiplier, wheel_wait
>
>

class panel.widgets.input.PasswordInput(**params: Any)
Bases: `_TextInputBase`

The PasswordInput allows entering any string using an obfuscated text
input box.

Reference:
[https://panel.holoviz.org/reference/widgets/PasswordInput.html](https://panel.holoviz.org/reference/widgets/PasswordInput.html)

Example:

\>\>\>
PasswordInput(
...
name='Password',
placeholder='Enter
your password here...' ...
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
> height, margin, disabled
>
> `panel.widgets.input._TextInputBase`: value,
> width, description, max_length, placeholder, value_input
>
>

panel.widgets.input.Spinner
alias of
[NumberInput](#panel.widgets.input.NumberInput)

class panel.widgets.input.StaticText(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The StaticText widget displays a text value, but does not allow editing
it.

Reference:
[https://panel.holoviz.org/reference/widgets/StaticText.html](https://panel.holoviz.org/reference/widgets/StaticText.html)

Example:

\>\>\>
StaticText(name='Model',
value='animagen2')

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
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The current value to be displayed.

class panel.widgets.input.Switch(**params: Any)
Bases: `_BooleanWidget`

The Switch allows toggling a single condition between True/False states
by ticking a checkbox.

This widget is interchangeable with the Toggle widget.

Reference:
[https://panel.holoviz.org/reference/widgets/Switch.html](https://panel.holoviz.org/reference/widgets/Switch.html)

Example:

\>\>\>
Switch(name='Works
with the tools you know and love',
value=True)

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
> `panel.widgets.input._BooleanWidget`: value
>
>

class panel.widgets.input.TextAreaInput(**params: Any)
Bases: `_TextInputBase`

>
>
> The TextAreaInput allows entering any multiline string using a text
> input box.
>
> Lines are joined with the newline character \`
>
>

[\`](#id3).

>
>
> Reference:
> [class="reference external">https://panel.holoviz.org/reference/widgets/TextAreaInput.html](https://panel.holoviz.org/reference/widgets/TextAreaInput.html)
> :Example:
>
>
>
>
>
> \>\>\>
> TextAreaInput(
> ...
> name='Description',
> placeholder='Enter
> your description here...' ...
> )
>
>
>
>
>
>

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
> height, margin, disabled
>
> `panel.widgets.input._TextInputBase`: value,
> width, description, max_length, placeholder, value_input
>
>

`auto_grow`` ``=`` ``Boolean(default=False,`` ``label='Auto`` ``grow')`
Whether the text area should automatically grow vertically to
accommodate the current text.

`cols`` ``=`` ``Integer(default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Cols')`
Number of columns in the text input field.

`max_rows`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``rows')`
When combined with auto_grow this determines the maximum number of rows
the input area can grow.

`rows`` ``=`` ``Integer(default=2,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Rows')`
Number of rows in the text input field.

`resizable`` ``=`` ``Selector(default='both',`` ``label='Resizable',`` ``names={},`` ``objects=['both',`` ``'width',`` ``'height',`` ``False])`
Whether the layout is interactively resizable, and if so in which
dimensions: width, height, or both. Can only be set during
initialization.

class panel.widgets.input.TextInput(**params: Any)
Bases: `_TextInputBase`

The TextInput widget allows entering any string using a text input box.

Reference:
[https://panel.holoviz.org/reference/widgets/TextInput.html](https://panel.holoviz.org/reference/widgets/TextInput.html)

Example:

\>\>\>
TextInput(name='Name',
placeholder='Enter
your name here ...')

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
> height, margin, disabled
>
> `panel.widgets.input._TextInputBase`: value,
> width, description, max_length, placeholder, value_input
>
>

`enter_pressed`` ``=`` ``Event(allow_refs=True,`` ``default=False,`` ``label='Enter`` ``pressed')`
Event when the enter key has been pressed.

class panel.widgets.input.TimePicker(**params: Any)
Bases: `_TimeCommon`

The TimePicker allows selecting a time value using a text box and a
time-picking utility.

Reference:
[https://panel.holoviz.org/reference/widgets/TimePicker.html](https://panel.holoviz.org/reference/widgets/TimePicker.html)

Example:

\>\>\>
TimePicker(
...
value="12:59:31",
start="09:00:00",
end="18:00:00",
name="Time"
... )

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
> `panel.widgets.input._TimeCommon`:
> hour_increment, minute_increment, second_increment, seconds, clock
>
>

`value`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'datetime.time'>,`` ``<class`` ``'str'>),`` ``label='Value')`
The current value

`start`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'datetime.time'>,`` ``<class`` ``'str'>),`` ``label='Start')`
Inclusive lower bound of the allowed time selection

`end`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'datetime.time'>,`` ``<class`` ``'str'>),`` ``label='End')`
Inclusive upper bound of the allowed time selection

`format`` ``=`` ``String(default='H:i',`` ``label='Format')`
Formatting specification for the display of the picked date.
+—+————————————+————+ \| H \| Hours (24 hours) \| 00 to 23 \| \| h \|
Hours \| 1 to 12 \| \| G \| Hours, 2 digits with leading zeros \| 1 to
12 \| \| i \| Minutes \| 00 to 59 \| \| S \| Seconds, 2 digits \| 00 to
59 \| \| s \| Seconds \| 0, 1 to 59 \| \| K \| AM/PM \| AM or PM \|
+—+————————————+————+ See also
[https://flatpickr.js.org/formatting/#date-formatting-tokens](https://flatpickr.js.org/formatting/#date-formatting-tokens).

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
