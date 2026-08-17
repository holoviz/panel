# panel.widgets.select module

Defines various Select widgets which allow choosing one or more items
from a list of options.

class panel.widgets.select.AutocompleteInput(\*, case_sensitive, description, min_characters, placeholder, restrict, search_strategy, value_input, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [SingleSelectBase](#panel.widgets.select.SingleSelectBase)

The AutocompleteInput widget allows selecting multiple values from a
list of options.

It falls into the broad category of multi-value, option-selection
widgets that provide a compatible API and include the MultiSelect,
CrossSelector, CheckBoxGroup and CheckButtonGroup widgets.

The MultiChoice widget provides a much more compact UI than MultiSelect.

Reference: [https://panel.holoviz.org/reference/widgets/AutocompleteInput.html](https://panel.holoviz.org/reference/widgets/AutocompleteInput.html)

Example:

\>\>\>
AutocompleteInput(
...
name='Study',
options=\['Biology',
'Chemistry',
'Physics'\],
...
placeholder='Write
your study here ...' ...
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
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``default='',`` ``label='Value')`
Initial or entered text value updated when \<enter\> key is pressed.

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`case_sensitive`` ``=`` ``Boolean(default=True,`` ``label='Case`` ``sensitive')`
Enable or disable case sensitivity.

`min_characters`` ``=`` ``Integer(default=2,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Min`` ``characters')`
The number of characters a user must type before completions are
presented.

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
Placeholder for empty input field.

`restrict`` ``=`` ``Boolean(default=True,`` ``label='Restrict')`
Set to False in order to allow users to enter text that is not present
in the list of completion strings.

`search_strategy`` ``=`` ``Selector(default='starts_with',`` ``label='Search`` ``strategy',`` ``names={},`` ``objects=['starts_with',`` ``'includes'])`
Define how to search the list of completion strings. The default option
“starts_with” means that the user’s text must match the start of a
completion string. Using “includes” means that the user’s text can match
any substring of a completion string.

`value_input`` ``=`` ``String(allow_None=True,`` ``default='',`` ``label='Value`` ``input')`
Initial or entered text value updated on every key press.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
An HTML string describing the function of this component.

class panel.widgets.select.CheckBoxGroup(\*, inline, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_CheckGroupBase`

The CheckBoxGroup widget allows selecting between a list of options by
ticking the corresponding checkboxes.

It falls into the broad category of multi-option selection widgets that
provide a compatible API and include the MultiSelect, CrossSelector and
CheckButtonGroup widgets.

Reference:
[https://panel.holoviz.org/reference/widgets/CheckBoxGroup.html](https://panel.holoviz.org/reference/widgets/CheckBoxGroup.html)

Example:

\>\>\>
CheckBoxGroup(
...
name='Fruits',
value=\['Apple',
'Pear'\],
options=\['Apple',
'Banana',
'Pear',
'Strawberry'\],
...
inline=True
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
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._CheckGroupBase`: value
>
>

`inline`` ``=`` ``Boolean(default=False,`` ``label='Inline')`
Whether the items be arrange vertically
(`False`) or horizontally in-line
(`True`).

class panel.widgets.select.CheckButtonGroup(\*, orientation, options, button_style, button_type, color, variant, description, description_delay, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_CheckGroupBase`,
`_ButtonBase`,
`TooltipMixin`

The CheckButtonGroup widget allows selecting between a list of options
by toggling the corresponding buttons.

It falls into the broad category of multi-option selection widgets that
provide a compatible API and include the MultiSelect, CrossSelector and
CheckBoxGroup widgets.

Reference: [https://panel.holoviz.org/reference/widgets/CheckButtonGroup.html](https://panel.holoviz.org/reference/widgets/CheckButtonGroup.html)

Example:

\>\>\>
CheckButtonGroup(
...
name='Regression
Models',
value=\['Lasso',
'Ridge'\],
...
options=\['Lasso',
'Linear',
'Ridge',
'Polynomial'\]
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
> `panel.widgets._mixin.TooltipMixin`:
> description, description_delay
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._CheckGroupBase`: value
>
>

`orientation`` ``=`` ``Selector(default='horizontal',`` ``label='Orientation',`` ``names={},`` ``objects=['horizontal',`` ``'vertical'])`
Button group orientation, either ‘horizontal’ (default) or ‘vertical’.

class panel.widgets.select.ColorMap(\*, ncols, swatch_height, swatch_width, value_name, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [SingleSelectBase](#panel.widgets.select.SingleSelectBase)

The ColorMap widget allows selecting a value from a dictionary of
options each containing a colormap specified as a list of colors or a
matplotlib colormap.

Reference:
[https://panel.holoviz.org/reference/widgets/ColorMap.html](https://panel.holoviz.org/reference/widgets/ColorMap.html)

Example:

\>\>\>
ColorMap(name='Reds',
options={'Reds':
\['white',
'red'\],
'Blues':
\['#ffffff',
'#0000ff'\]})

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
The selected colormap.

`options`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Options')`
Dictionary of colormaps

`ncols`` ``=`` ``Integer(default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ncols')`
Number of columns of swatches to display.

`swatch_height`` ``=`` ``Integer(default=20,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Swatch`` ``height')`
Height of the color swatches.

`swatch_width`` ``=`` ``Integer(default=100,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Swatch`` ``width')`
Width of the color swatches.

`value_name`` ``=`` ``String(allow_None=True,`` ``label='Value`` ``name')`
Name of the selected colormap.

class panel.widgets.select.CrossSelector(\*, definition_order, filter_fn, size, description, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget),
[MultiSelect](#panel.widgets.select.MultiSelect)

A composite widget which allows selecting from a list of items by moving
them between two lists. Supports filtering values by name to select them
in bulk.

Reference:
[https://panel.holoviz.org/reference/widgets/CrossSelector.html](https://panel.holoviz.org/reference/widgets/CrossSelector.html)

Example:

\>\>\>
CrossSelector(
...
name='Fruits',
value=\['Apple',
'Pear'\],
...
options=\['Apple',
'Banana',
'Pear',
'Strawberry'\]
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
> margin, disabled
>
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._MultiSelectBase`:
> value, description
>
>

`height`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=200,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The number of options shown at once (note this is the only way to
control the height of this widget)

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=600,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The number of options shown at once (note this is the only way to
control the height of this widget)

`size`` ``=`` ``Integer(default=10,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
The number of options shown at once (note this is the only way to
control the height of this widget)

`filter_fn`` ``=`` ``Callable(label='Filter`` ``fn')`
The filter function applied when querying using the text fields,
defaults to re.search. Function is two arguments, the query or pattern
and the item label.

`definition_order`` ``=`` ``Integer(default=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Definition`` ``order')`
Whether to preserve definition order after filtering. Disable to allow
the order of selection to define the order of the selected list.

filter_fn(string, flags=0)
Scan through string looking for a match to the pattern, returning a
Match object, or None if no match was found.

class panel.widgets.select.MultiChoice(\*, delete_button, max_items, option_limit, placeholder, search_option_limit, solid, description, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_MultiSelectBase`

The MultiChoice widget allows selecting multiple values from a list of
options.

It falls into the broad category of multi-value, option-selection
widgets that provide a compatible API and include the MultiSelect,
CrossSelector, CheckBoxGroup and CheckButtonGroup widgets.

The MultiChoice widget provides a much more compact UI than MultiSelect.

Reference:
[https://panel.holoviz.org/reference/widgets/MultiChoice.html](https://panel.holoviz.org/reference/widgets/MultiChoice.html)

Example:

\>\>\>
MultiChoice(
...
name='Favourites',
value=\['Panel',
'hvPlot'\],
...
options=\['Panel',
'hvPlot',
'HoloViews',
'GeoViews',
'Datashader',
'Param',
'Colorcet'\],
...
max_items=2
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
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._MultiSelectBase`:
> value, description
>
>

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`delete_button`` ``=`` ``Boolean(default=True,`` ``label='Delete`` ``button')`
Whether to display a button to delete a selected option.

`max_items`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``items')`
Maximum number of options that can be selected.

`option_limit`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Option`` ``limit')`
Maximum number of options to display at once.

`search_option_limit`` ``=`` ``Integer(allow_None=True,`` ``bounds=(1,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Search`` ``option`` ``limit')`
Maximum number of options to display at once if search string is
entered.

`placeholder`` ``=`` ``String(default='',`` ``label='Placeholder')`
String displayed when no selection has been made.

`solid`` ``=`` ``Boolean(default=True,`` ``label='Solid')`
Whether to display widget with solid or light style.

class panel.widgets.select.MultiSelect(\*, size, description, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_MultiSelectBase`

The MultiSelect widget allows selecting multiple values from a list of
options.

It falls into the broad category of multi-value, option-selection
widgets that provide a compatible API and include the\`CrossSelector\`,
CheckBoxGroup and CheckButtonGroup widgets.

Reference:
[https://panel.holoviz.org/reference/widgets/MultiSelect.html](https://panel.holoviz.org/reference/widgets/MultiSelect.html)

Example:

\>\>\>
MultiSelect(
...
name='Frameworks',
value=\['Bokeh',
'Panel'\],
...
options=\['Bokeh',
'Dash',
'Panel',
'Streamlit',
'Voila'\],
size=8
... )

Methods

|  |  |
|----|----|
| [on_double_click](#panel.widgets.select.MultiSelect.on_double_click)(callback) | Register a callback to be executed when a MultiSelect option is double-clicked. |

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
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
> `panel.widgets.select._MultiSelectBase`:
> value, width, description
>
>

`size`` ``=`` ``Integer(allow_refs=True,`` ``default=4,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
The number of items displayed at once (i.e. determines the widget
height).

on_double_click(callback: Callable\[\[param.parameterized.Event\], None \| Awaitable\[None\]\]) → None
Register a callback to be executed when a MultiSelect option is
double-clicked.

The callback is given an DoubleClickEvent argument

Parameters:
**callback:**
The function to run on click events. Must accept a positional Event
argument. Can be a sync or async function

class panel.widgets.select.NestedSelect(\*, \_levels, \_max_depth, \_widgets, layout, levels, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[CompositeWidget](panel.widgets.base.md#panel.widgets.base.CompositeWidget)

The NestedSelect widget is composed of multiple widgets, where
subsequent select options depend on the parent’s value.

Reference:
[https://panel.holoviz.org/reference/widgets/NestedSelect.html](https://panel.holoviz.org/reference/widgets/NestedSelect.html)

Example:

\>\>\>
NestedSelect(
...
options={
...
"gfs":
{"tmp":
\[1000,
500\],
"pcp":
\[1000\]},
...
"name":
{"tmp":
\[1000,
925,
850,
700,
500\],
"pcp":
\[1000\]},
...  },
...
levels=\["model",
"var",
"level"\],
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
> height, margin, width
>
>

`value`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Value')`
The value from all the Select widgets; the keys are the levels names. If
no levels names are specified, the keys are the levels indices.

`disabled`` ``=`` ``Boolean(default=False,`` ``label='Disabled')`
Whether the widget is disabled.

`layout`` ``=`` ``Parameter(default=<class`` ``'panel.layout.base.Column'>,`` ``label='Layout')`
The layout type of the widgets. If a dictionary, a “type” key can be
provided, to specify the layout type of the widgets, and any additional
keyword arguments will be used to instantiate the layout.

`levels`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='Levels')`
Either a list of strings or a list of dictionaries. If a list of
strings, the strings are used as the names of the levels. If a list of
dictionaries, each dictionary may have a “name” key, which is used as
the name of the level, a “type” key, which is used as the type of
widget, and any corresponding widget keyword arguments; otherwise, will
inherit layoutable keyword arguments from the NestedSelect itself, e.g.
width, height, and sizing_mode. Must be specified if options is
callable.

`options`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'list'>,`` ``<class`` ``'dict'>,`` ``<class`` ``'function'>),`` ``label='Options')`
The options to select from. The options may be nested dictionaries,
lists, or callables that return those types. If callables are used, the
callables must accept level and value keyword arguments, where level is
the level that updated and value is a dictionary of the current values,
containing keys up to the level that was updated.

`_widgets`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'panel.widgets.base.WidgetBase'>,`` ``label='`` ``widgets')`
The nested select widgets.

`_max_depth`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``max`` ``depth')`
The number of levels of the nested select widgets.

`_levels`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='`` ``levels')`
The internal rep of levels to prevent overwriting user provided levels.

layout
alias of [Column](panel.layout.base.md#panel.layout.base.Column)

class panel.widgets.select.RadioBoxGroup(\*, inline, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_RadioGroupBase`

The RadioBoxGroup widget allows selecting from a list or dictionary of
values using a set of checkboxes.

It falls into the broad category of single-value, option-selection
widgets that provide a compatible API and include the RadioButtonGroup,
Select and DiscreteSlider widgets.

Reference:
[https://panel.holoviz.org/reference/widgets/RadioBoxGroup.html](https://panel.holoviz.org/reference/widgets/RadioBoxGroup.html)

Example:

\>\>\>
RadioBoxGroup(
...
name='Sponsor',
options=\['Anaconda',
'Blackstone'\],
inline=True
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
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
> [class="reference internal"
> title="panel.widgets.select.SingleSelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SingleSelectBase](#panel.widgets.select.SingleSelectBase):
> value
>
>

`inline`` ``=`` ``Boolean(default=False,`` ``label='Inline')`
Whether the items be arrange vertically
(`False`) or horizontally in-line
(`True`).

class panel.widgets.select.RadioButtonGroup(\*, orientation, options, button_style, button_type, color, variant, description, description_delay, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: `_RadioGroupBase`,
`_ButtonBase`,
`TooltipMixin`

The RadioButtonGroup widget allows selecting from a list or dictionary
of values using a set of toggle buttons.

It falls into the broad category of single-value, option-selection
widgets that provide a compatible API and include the RadioBoxGroup,
Select, and DiscreteSlider widgets.

Reference: [https://panel.holoviz.org/reference/widgets/RadioButtonGroup.html](https://panel.holoviz.org/reference/widgets/RadioButtonGroup.html)

Example:

\>\>\>
RadioButtonGroup(
...
name='Plotting
library',
options=\['Matplotlib',
'Bokeh',
'Plotly'\],
...
color='success'
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
> `panel.widgets._mixin.TooltipMixin`:
> description, description_delay
>
> `panel.widgets.button._ButtonBase`:
> button_type, button_style, color, variant
>
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
> [class="reference internal"
> title="panel.widgets.select.SingleSelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SingleSelectBase](#panel.widgets.select.SingleSelectBase):
> value
>
>

`orientation`` ``=`` ``Selector(default='horizontal',`` ``label='Orientation',`` ``names={},`` ``objects=['horizontal',`` ``'vertical'])`
Button group orientation, either ‘horizontal’ (default) or ‘vertical’.

class panel.widgets.select.Select(\*, description, disabled_options, groups, size, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [SingleSelectBase](#panel.widgets.select.SingleSelectBase)

The Select widget allows selecting a value from a list or dictionary of
options by selecting it from a dropdown menu or selection area.

It falls into the broad category of single-value, option-selection
widgets that provide a compatible API and include the RadioBoxGroup,
AutocompleteInput and DiscreteSlider widgets.

Reference:
[https://panel.holoviz.org/reference/widgets/Select.html](https://panel.holoviz.org/reference/widgets/Select.html)

Example:

\>\>\>
Select(name='Study',
options=\['Biology',
'Chemistry',
'Physics'\])

Attributes:
**labels**

**values**

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
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
> [class="reference internal"
> title="panel.widgets.select.SingleSelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SingleSelectBase](#panel.widgets.select.SingleSelectBase):
> value
>
>

`width`` ``=`` ``Integer(allow_None=True,`` ``bounds=(0,`` ``None),`` ``default=300,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
Width of this component. If sizing_mode is set to stretch or scale mode
this will merely be used as a suggestion.

`description`` ``=`` ``String(allow_None=True,`` ``label='Description')`
A description of the widget, which will be displayed as a tooltip.

`disabled_options`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='Disabled`` ``options',`` ``nested_refs=True)`
Optional list of `options` that are disabled,
i.e. unusable and un-clickable. If `options` is
a dictionary the list items must be dictionary values.

`groups`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Groups',`` ``nested_refs=True)`
Dictionary whose keys are used to visually group the options and whose
values are either a list or a dictionary of options to select from.
Mutually exclusive with `options` and valid
only if `size` is 1.

`size`` ``=`` ``Integer(bounds=(1,`` ``None),`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Size')`
Declares how many options are displayed at the same time. If set to 1
displays options as dropdown otherwise displays scrollable area.

class panel.widgets.select.SelectBase(**params: Any)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

Attributes:
**labels**

**values**

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
>

`options`` ``=`` ``ClassSelector(allow_refs=True,`` ``class_=(<class`` ``'dict'>,`` ``<class`` ``'list'>),`` ``default=[],`` ``label='Options')`
A list or dictionary of options to select from.

class panel.widgets.select.SingleSelectBase(\*, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases:
[SelectBase](#panel.widgets.select.SelectBase)

Attributes:
**unicode_values**

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
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
>

`value`` ``=`` ``Parameter(allow_None=True,`` ``label='Value')`
The widget value which the widget type resolves to when used as a
reactive param reference.

class panel.widgets.select.ToggleGroup(\*, options, disabled, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, label, value, name)
Bases: [SingleSelectBase](#panel.widgets.select.SingleSelectBase)

This class is a factory of ToggleGroup widgets.

A ToggleGroup is a group of widgets which can be switched ‘on’ or ‘off’.

Two types of widgets are available through the widget_type argument :
- ‘button’ (default)

- ‘box’

Two different behaviors are available through behavior argument:
- ‘check’ (default)boolean
  Any number of widgets can be selected. In this case value is a ‘list’
  of objects.

- ‘radio’boolean
  One and only one widget is switched on. In this case value is an
  ‘object’.

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
> [title="panel.widgets.select.SelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SelectBase](#panel.widgets.select.SelectBase):
> options
>
> [class="reference internal"
> title="panel.widgets.select.SingleSelectBase"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.select.SingleSelectBase](#panel.widgets.select.SingleSelectBase):
> value
>
>

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
