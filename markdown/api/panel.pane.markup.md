# panel.pane.markup module

Pane class which render various markup languages including HTML,
Markdown, and also regular strings.

class panel.pane.markup.DataFrame(object=None, **params)
Bases: [HTML](#panel.pane.markup.HTML)

The DataFrame pane renders pandas, dask and streamz DataFrame types
using their custom HTML repr.

In the case of a streamz DataFrame the rendered data will update
periodically.

Reference:
[https://panel.holoviz.org/reference/panes/DataFrame.html](https://panel.holoviz.org/reference/panes/DataFrame.html)

Example:

\>\>\>
DataFrame(df,
index=False,
max_rows=25,
width=400)

Methods

|  |  |
|----|----|
| [applies](#panel.pane.markup.DataFrame.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.markup.HTMLBasePane"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
> [title="panel.pane.markup.HTML"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTML](#panel.pane.markup.HTML):
> disable_math, sanitize_html, sanitize_hook
>
>

`bold_rows`` ``=`` ``Boolean(default=True,`` ``label='Bold`` ``rows')`
Make the row labels bold in the output.

`border`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Border')`
A `border=border` attribute is included in the
opening \<table\> tag.

`classes`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['panel-df'],`` ``label='Classes')`
CSS class(es) to apply to the resulting html table.

`col_space`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'int'>,`` ``<class`` ``'dict'>),`` ``label='Col`` ``space')`
The minimum width of each column in CSS length units. An int is assumed
to be px units.

`decimal`` ``=`` ``String(default='.',`` ``label='Decimal')`
Character recognized as decimal separator, e.g. ‘,’ in Europe.

`escape`` ``=`` ``Boolean(default=True,`` ``label='Escape')`
Whether or not to escape the dataframe HTML. For security reasons the
default value is True.

`float_format`` ``=`` ``Callable(allow_None=True,`` ``label='Float`` ``format')`
Formatter function to apply to columns’ elements if they are floats. The
result of this function must be a unicode string.

`formatters`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'dict'>,`` ``<class`` ``'list'>),`` ``label='Formatters')`
Formatter functions to apply to columns’ elements by position or name.
The result of each function must be a unicode string.

`header`` ``=`` ``Boolean(default=True,`` ``label='Header')`
Whether to print column labels.

`index`` ``=`` ``Boolean(default=True,`` ``label='Index')`
Whether to print index (row) labels.

`index_names`` ``=`` ``Boolean(default=True,`` ``label='Index`` ``names')`
Prints the names of the indexes.

`justify`` ``=`` ``Selector(allow_None=True,`` ``label='Justify',`` ``names={},`` ``objects=['left',`` ``'right',`` ``'center',`` ``'justify',`` ``'justify-all',`` ``'start',`` ``'end',`` ``'inherit',`` ``'match-parent',`` ``'initial',`` ``'unset'])`
How to justify the column labels.

`max_rows`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``rows')`
Maximum number of rows to display.

`max_cols`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``cols')`
Maximum number of columns to display.

`na_rep`` ``=`` ``String(default='NaN',`` ``label='Na`` ``rep')`
String representation of NAN to use.

`render_links`` ``=`` ``Boolean(default=False,`` ``label='Render`` ``links')`
Convert URLs to HTML links.

`show_dimensions`` ``=`` ``Boolean(default=False,`` ``label='Show`` ``dimensions')`
Display DataFrame dimensions (number of rows by number of columns).

`sparsify`` ``=`` ``Boolean(default=True,`` ``label='Sparsify')`
Set to False for a DataFrame with a hierarchical index to print every
multi-index key at each row.

`text_align`` ``=`` ``Selector(label='Text`` ``align',`` ``names={},`` ``objects=['start',`` ``'end',`` ``'center'])`
Alignment of non-header cells.

`_object`` ``=`` ``Parameter(allow_None=True,`` ``label='`` ``object')`
Hidden parameter.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

class panel.pane.markup.HTML(object=None, **params)
Bases:
[HTMLBasePane](#panel.pane.markup.HTMLBasePane)

HTML panes renders HTML strings and objects with a \_repr_html\_ method.

The height and width can optionally be specified, to allow room for
whatever is being wrapped.

Reference: [https://panel.holoviz.org/reference/panes/HTML.html](https://panel.holoviz.org/reference/panes/HTML.html)

Example:

\>\>\>
HTML(
...  "\<h1\>This is a HTML
pane\</h1\>", ...
styles={'background-color':
'#F6F6F6'}
... )

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.markup.HTML.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.markup.HTMLBasePane"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
>

`disable_math`` ``=`` ``Boolean(default=True,`` ``label='Disable`` ``math')`
Whether to disable support for MathJax math rendering for strings
escaped with \$\$ delimiters.

`sanitize_html`` ``=`` ``Boolean(default=False,`` ``label='Sanitize`` ``html')`
Whether to sanitize HTML sent to the frontend.

`sanitize_hook`` ``=`` ``Callable(label='Sanitize`` ``hook')`
Sanitization callback to apply if sanitize_html=True.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

class panel.pane.markup.HTMLBasePane(object=None, **params)
Bases: [ModelPane](panel.pane.base.md#panel.pane.base.ModelPane)

Baseclass for Panes which render HTML inside a Bokeh Div. See the
documentation for Bokeh Div for more detail about the supported options
like style and sizing_mode.

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
>

`enable_streaming`` ``=`` ``Boolean(default=False,`` ``label='Enable`` ``streaming')`
Whether to enable streaming of text snippets. This is useful when
updating a string step by step, e.g. in a chat message.

class panel.pane.markup.JSON(object=None, **params)
Bases:
[HTMLBasePane](#panel.pane.markup.HTMLBasePane)

The JSON pane allows rendering arbitrary JSON strings, dicts and other
json serializable objects in a panel.

Reference: [https://panel.holoviz.org/reference/panes/JSON.html](https://panel.holoviz.org/reference/panes/JSON.html)

Example:

\>\>\>
JSON(json_obj,
theme='light',
height=300,
width=500)

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.markup.JSON.applies)(object, **params) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.markup.HTMLBasePane"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
>

`depth`` ``=`` ``Integer(bounds=(-1,`` ``None),`` ``default=1,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Depth')`
Depth to which the JSON tree will be expanded on initialization.

`encoder`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'json.encoder.JSONEncoder'>,`` ``label='Encoder')`
Custom JSONEncoder class used to serialize objects to JSON string.

`hover_preview`` ``=`` ``Boolean(default=False,`` ``label='Hover`` ``preview')`
Whether to display a hover preview for collapsed nodes.

`theme`` ``=`` ``Selector(default='light',`` ``label='Theme',`` ``names={},`` ``objects=['light',`` ``'dark'])`
If no value is provided, it defaults to the current theme set by
pn.config.theme, as specified in the JSON.THEME_CONFIGURATION
dictionary. If not defined there, it falls back to the default parameter
value.

classmethod applies(object: Any, **params) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

class panel.pane.markup.Markdown(object=None, **params)
Bases:
[HTMLBasePane](#panel.pane.markup.HTMLBasePane)

The Markdown pane allows rendering arbitrary markdown strings in a
panel.

It renders strings containing valid Markdown as well as objects with a
\_repr_markdown\_ method, and may define custom CSS styles.

Reference:
[https://panel.holoviz.org/reference/panes/Markdown.html](https://panel.holoviz.org/reference/panes/Markdown.html)

Example:

\>\>\>
Markdown("#
This is a header")

Attributes:
**priority**

Methods

|  |  |
|----|----|
| [applies](#panel.pane.markup.Markdown.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.markup.HTMLBasePane"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
>

`dedent`` ``=`` ``Boolean(default=True,`` ``label='Dedent')`
Whether to dedent common whitespace across all lines.

`disable_anchors`` ``=`` ``Boolean(default=False,`` ``label='Disable`` ``anchors')`
Whether to disable automatically adding anchors to headings.

`disable_math`` ``=`` ``Boolean(default=False,`` ``label='Disable`` ``math')`
Whether to disable support for MathJax math rendering for strings
escaped with \$\$ delimiters.

`extensions`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=['extra',`` ``'smarty',`` ``'codehilite'],`` ``label='Extensions',`` ``nested_refs=True)`
Markdown extension to apply when transforming markup. Does not apply if
renderer is set to ‘markdown-it’ or ‘myst’.

`hard_line_break`` ``=`` ``Boolean(default=False,`` ``label='Hard`` ``line`` ``break')`
Whether simple new lines are rendered as hard line breaks. False by
default to conform with the original Markdown spec. Not supported by the
‘myst’ renderer.

`plugins`` ``=`` ``List(bounds=(0,`` ``None),`` ``default=[],`` ``label='Plugins',`` ``nested_refs=True)`
Additional markdown-it-py plugins to use.

`renderer`` ``=`` ``Selector(default='markdown-it',`` ``label='Renderer',`` ``names={},`` ``objects=['markdown-it',`` ``'myst',`` ``'markdown'])`
Markdown renderer implementation.

`renderer_options`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Renderer`` ``options',`` ``nested_refs=True)`
Options to pass to the markdown renderer.

classmethod applies(object: Any) → float \| bool \| None
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

priority: t.ClassVar\[float \| bool \| None\] = None

class panel.pane.markup.Str(object=None, **params)
Bases:
[HTMLBasePane](#panel.pane.markup.HTMLBasePane)

The Str pane allows rendering arbitrary text and objects in a panel.

Unlike Markdown and HTML, a Str is interpreted as a raw string without
applying any markup and is displayed in a fixed-width font by default.

The pane will render any text, and if given an object will display the
object’s Python repr.

Reference: [https://panel.holoviz.org/reference/panes/Str.html](https://panel.holoviz.org/reference/panes/Str.html)

Example:

\>\>\>
Str(
...  'This raw string will not
be formatted, except for the applied
style.', ...
styles={'font-size':
'12pt'}
... )

Methods

|  |  |
|----|----|
| [applies](#panel.pane.markup.Str.applies)(object) | Returns boolean or float indicating whether the Pane can render the object. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, styles, stylesheets, tags, width,
> width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.pane.base.PaneBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.base.PaneBase](panel.pane.base.md#panel.pane.base.PaneBase):
> margin, default_layout, object
>
> [title="panel.pane.markup.HTMLBasePane"> class="sourceCode python xref py py-class docutils literal notranslate">panel.pane.markup.HTMLBasePane](#panel.pane.markup.HTMLBasePane):
> enable_streaming
>
>

classmethod applies(object: Any) → bool
Returns boolean or float indicating whether the Pane can render the
object.

If the priority of the pane is set to None, this method may also be used
to define a float priority depending on the object being rendered.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
