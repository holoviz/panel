# panel.theme.fast module

class panel.theme.fast.Fast(theme=None, **params)
Bases: [Design](panel.theme.base.md#panel.theme.base.Design)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.theme.base.Design"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.Design](panel.theme.base.md#panel.theme.base.Design):
> theme
>
>

class panel.theme.fast.FastDarkTheme(\*, style, base_css, bokeh_theme, css, name)
Bases: [DarkTheme](panel.theme.base.md#panel.theme.base.DarkTheme)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.theme.base.Theme"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.Theme](panel.theme.base.md#panel.theme.base.Theme):
> css
>
> [class="reference internal" title="panel.theme.base.DarkTheme"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.DarkTheme](panel.theme.base.md#panel.theme.base.DarkTheme):
> base_css, bokeh_theme
>
>

`style`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.fast.FastStyle'>,`` ``default=FastStyle(accent_base_color='#0072B5',`` ``background_color='#181818',`` ``collapsed_icon='\n<svg`` ``style="stroke:`` ``var(--accent-fill-rest);"`` ``width="18"`` ``height="18"`` ``viewBox="0`` ``0`` ``18`` ``18"`` ``fill="none"`` ``xmlns="http://www.w3.org/2000/svg"`` ``slot="collapsed-icon">\n``  ``<path`` ``d="M15.2222`` ``1H2.77778C1.79594`` ``1`` ``1`` ``1.79594`` ``1`` ``2.77778V15.2222C1`` ``16.2041`` ``1.79594`` ``17`` ``2.77778`` ``17H15.2222C16.2041`` ``17`` ``17`` ``16.2041`` ``17`` ``15.2222V2.77778C17`` ``1.79594`` ``16.2041`` ``1`` ``15.2222`` ``1Z"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n``  ``<path`` ``d="M9`` ``5.44446V12.5556"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n``  ``<path`` ``d="M5.44446`` ``9H12.5556"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n</svg>\n',`` ``color='#ffffff',`` ``corner_radius=3,`` ``expanded_icon='\n<svg`` ``style="stroke:`` ``var(--accent-fill-rest);"`` ``width="18"`` ``height="18"`` ``viewBox="0`` ``0`` ``18`` ``18"`` ``fill="none"`` ``xmlns="http://www.w3.org/2000/svg"`` ``slot="expanded-icon">\n``  ``<path`` ``d="M15.2222`` ``1H2.77778C1.79594`` ``1`` ``1`` ``1.79594`` ``1`` ``2.77778V15.2222C1`` ``16.2041`` ``1.79594`` ``17`` ``2.77778`` ``17H15.2222C16.2041`` ``17`` ``17`` ``16.2041`` ``17`` ``15.2222V2.77778C17`` ``1.79594`` ``16.2041`` ``1`` ``15.2222`` ``1Z"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n``  ``<path`` ``d="M5.44446`` ``9H12.5556"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n</svg>\n',`` ``font='Open`` ``Sans,`` ``sans-serif',`` ``font_url='//fonts.googleapis.com/css?family=Open+Sans',`` ``header_accent_base_color='#ffffff',`` ``header_background='#0072B5',`` ``header_color='#ffffff',`` ``header_luminance=0.23,`` ``header_neutral_color='#0072B5',`` ``luminance=0.1,`` ``name='FastStyle00105',`` ``neutral_color='#000000',`` ``neutral_fill_card_rest='#212121',`` ``neutral_focus='#717171',`` ``neutral_foreground_rest='#e5e5e5',`` ``shadow=False),`` ``label='Style')`

property bokeh_theme
Provide new default values for Bokeh models.

Bokeh Model properties all have some built-in default value. If a
property has not been explicitly set (e.g.
`m.foo`` ``=`` ``10`),
accessing the property will return the default value. It may be useful
for users to be able to specify a different set of default values than
the built-in default. The `Theme` class allows
collections of custom default values to be easily applied to Bokeh
documents.

The `Theme` class can be constructed either
from a YAML file or from a JSON dict (but not both). Examples of both
formats are shown below.

The plotting API defaults override some theme properties. Namely:
fill_alpha, fill_color, line_alpha, line_color, text_alpha and
text_color. Those properties should therefore be set explicitly when
using the plotting API.

Args:
filename (str, optional) : path to a YAML theme file json (str,
optional) : a JSON dictionary specifying theme values

Raises:
ValueError
If neither `filename` nor
`json` is supplied.

Examples:

>
>
> Themes are specified by providing a top-level key
> `attrs` which has blocks for Model types to
> be themed. Each block has keys and values that specify the new
> property defaults for that type.
>
> Take note of the fact that YAML interprets the value None as a string,
> which is not usually what you want. To give None as a value in YAML,
> use !!null. To give ‘None’ as a value in json, use null.
>
> Here is an example theme in YAML format that sets various visual
> properties for all figures, grids, and titles:
>
>
>
>
>
> attrs:
> Plot:
>
> background_fill_color:
> '#2F2F2F'
> border_fill_color:
> '#2F2F2F'
> outline_line_color:
> '#444444'
> Axis:
>
> axis_line_color:
> !!null
> Grid:
>
> grid_line_dash:
> \[6,
> 4\]
>
> grid_line_alpha:
> .3
>
> Title:
>
> text_color:
> "white"
>
>
>
>
>
> Here is the same theme, in JSON format:
>
>
>
>
>
> { 'attrs'
> : {
> 'Plot':
> {
> 'background_fill_color':
> '#2F2F2F',
> 'border_fill_color':
> '#2F2F2F',
> 'outline_line_color':
> '#444444',
> },
> 'Axis':
> {
> 'axis_line_color':
> None,
> },
> 'Grid':
> {
> 'grid_line_dash':
> \[6,
> 4\],
> 'grid_line_alpha':
> .3,
> },
> 'Title':
> {
> 'text_color':
> 'white' }
> } }
>
>
>
>
>
>

class panel.theme.fast.FastDefaultTheme(\*, style, base_css, bokeh_theme, css, name)
Bases: [DefaultTheme](panel.theme.base.md#panel.theme.base.DefaultTheme)

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.theme.base.Theme"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.Theme](panel.theme.base.md#panel.theme.base.Theme):
> bokeh_theme, css
>
> [class="reference internal" title="panel.theme.base.DefaultTheme"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.theme.base.DefaultTheme](panel.theme.base.md#panel.theme.base.DefaultTheme):
> base_css
>
>

`style`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.fast.FastStyle'>,`` ``default=FastStyle(accent_base_color='#0072B5',`` ``background_color='#ffffff',`` ``collapsed_icon='\n<svg`` ``style="stroke:`` ``var(--accent-fill-rest);"`` ``width="18"`` ``height="18"`` ``viewBox="0`` ``0`` ``18`` ``18"`` ``fill="none"`` ``xmlns="http://www.w3.org/2000/svg"`` ``slot="collapsed-icon">\n``  ``<path`` ``d="M15.2222`` ``1H2.77778C1.79594`` ``1`` ``1`` ``1.79594`` ``1`` ``2.77778V15.2222C1`` ``16.2041`` ``1.79594`` ``17`` ``2.77778`` ``17H15.2222C16.2041`` ``17`` ``17`` ``16.2041`` ``17`` ``15.2222V2.77778C17`` ``1.79594`` ``16.2041`` ``1`` ``15.2222`` ``1Z"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n``  ``<path`` ``d="M9`` ``5.44446V12.5556"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n``  ``<path`` ``d="M5.44446`` ``9H12.5556"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n</svg>\n',`` ``color='#2B2B2B',`` ``corner_radius=3,`` ``expanded_icon='\n<svg`` ``style="stroke:`` ``var(--accent-fill-rest);"`` ``width="18"`` ``height="18"`` ``viewBox="0`` ``0`` ``18`` ``18"`` ``fill="none"`` ``xmlns="http://www.w3.org/2000/svg"`` ``slot="expanded-icon">\n``  ``<path`` ``d="M15.2222`` ``1H2.77778C1.79594`` ``1`` ``1`` ``1.79594`` ``1`` ``2.77778V15.2222C1`` ``16.2041`` ``1.79594`` ``17`` ``2.77778`` ``17H15.2222C16.2041`` ``17`` ``17`` ``16.2041`` ``17`` ``15.2222V2.77778C17`` ``1.79594`` ``16.2041`` ``1`` ``15.2222`` ``1Z"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n``  ``<path`` ``d="M5.44446`` ``9H12.5556"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n</svg>\n',`` ``font='Open`` ``Sans,`` ``sans-serif',`` ``font_url='//fonts.googleapis.com/css?family=Open+Sans',`` ``header_accent_base_color='#ffffff',`` ``header_background='#0072B5',`` ``header_color='#ffffff',`` ``header_luminance=0.23,`` ``header_neutral_color='#0072B5',`` ``luminance=1.0,`` ``name='FastStyle00104',`` ``neutral_color='#000000',`` ``neutral_fill_card_rest='#F7F7F7',`` ``neutral_focus='#888888',`` ``neutral_foreground_rest='#2B2B2B',`` ``shadow=True),`` ``label='Style')`

class panel.theme.fast.FastStyle(\*, accent_base_color, background_color, collapsed_icon, color, corner_radius, expanded_icon, font, font_url, header_accent_base_color, header_background, header_color, header_luminance, header_neutral_color, luminance, neutral_color, neutral_fill_card_rest, neutral_focus, neutral_foreground_rest, shadow, name)
Bases: `Parameterized`

The FastStyle class provides the different colors and icons used to
style the Fast Templates.

Methods

|  |  |
|----|----|
| [create_bokeh_theme](#panel.theme.fast.FastStyle.create_bokeh_theme)() | Returns a custom bokeh theme based on the style parameters |

**Parameter Definitions**

------------------------------------------------------------------------

`background_color`` ``=`` ``String(default='#ffffff',`` ``label='Background`` ``color')`

`neutral_color`` ``=`` ``String(default='#000000',`` ``label='Neutral`` ``color')`

`accent_base_color`` ``=`` ``String(default='#0072B5',`` ``label='Accent`` ``base`` ``color')`

`collapsed_icon`` ``=`` ``String(default='\n<svg`` ``style="stroke:`` ``var(--accent-fill-rest);"`` ``width="18"`` ``height="18"`` ``viewBox="0`` ``0`` ``18`` ``18"`` ``fill="none"`` ``xmlns="http://www.w3.org/2000/svg"`` ``slot="collapsed-icon">\n``  ``<path`` ``d="M15.2222`` ``1H2.77778C1.79594`` ``1`` ``1`` ``1.79594`` ``1`` ``2.77778V15.2222C1`` ``16.2041`` ``1.79594`` ``17`` ``2.77778`` ``17H15.2222C16.2041`` ``17`` ``17`` ``16.2041`` ``17`` ``15.2222V2.77778C17`` ``1.79594`` ``16.2041`` ``1`` ``15.2222`` ``1Z"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n``  ``<path`` ``d="M9`` ``5.44446V12.5556"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n``  ``<path`` ``d="M5.44446`` ``9H12.5556"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n</svg>\n',`` ``label='Collapsed`` ``icon')`

`expanded_icon`` ``=`` ``String(default='\n<svg`` ``style="stroke:`` ``var(--accent-fill-rest);"`` ``width="18"`` ``height="18"`` ``viewBox="0`` ``0`` ``18`` ``18"`` ``fill="none"`` ``xmlns="http://www.w3.org/2000/svg"`` ``slot="expanded-icon">\n``  ``<path`` ``d="M15.2222`` ``1H2.77778C1.79594`` ``1`` ``1`` ``1.79594`` ``1`` ``2.77778V15.2222C1`` ``16.2041`` ``1.79594`` ``17`` ``2.77778`` ``17H15.2222C16.2041`` ``17`` ``17`` ``16.2041`` ``17`` ``15.2222V2.77778C17`` ``1.79594`` ``16.2041`` ``1`` ``15.2222`` ``1Z"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n``  ``<path`` ``d="M5.44446`` ``9H12.5556"`` ``stroke-linecap="round"`` ``stroke-linejoin="round"></path>\n</svg>\n',`` ``label='Expanded`` ``icon')`

`color`` ``=`` ``String(default='#2B2B2B',`` ``label='Color')`

`neutral_fill_card_rest`` ``=`` ``String(default='#F7F7F7',`` ``label='Neutral`` ``fill`` ``card`` ``rest')`

`neutral_focus`` ``=`` ``String(default='#888888',`` ``label='Neutral`` ``focus')`

`neutral_foreground_rest`` ``=`` ``String(default='#2B2B2B',`` ``label='Neutral`` ``foreground`` ``rest')`

`header_luminance`` ``=`` ``Magnitude(bounds=(0.0,`` ``1.0),`` ``default=0.23,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Header`` ``luminance')`

`header_background`` ``=`` ``String(default='#0072B5',`` ``label='Header`` ``background')`

`header_neutral_color`` ``=`` ``String(default='#0072B5',`` ``label='Header`` ``neutral`` ``color')`

`header_accent_base_color`` ``=`` ``String(default='#ffffff',`` ``label='Header`` ``accent`` ``base`` ``color')`

`header_color`` ``=`` ``String(default='#ffffff',`` ``label='Header`` ``color')`

`font`` ``=`` ``String(default='Open`` ``Sans,`` ``sans-serif',`` ``label='Font')`

`font_url`` ``=`` ``String(default='//fonts.googleapis.com/css?family=Open+Sans',`` ``label='Font`` ``url')`

`corner_radius`` ``=`` ``Integer(default=3,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Corner`` ``radius')`

`shadow`` ``=`` ``Boolean(default=True,`` ``label='Shadow')`

`luminance`` ``=`` ``Magnitude(bounds=(0.0,`` ``1.0),`` ``default=1.0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Luminance')`

create_bokeh_theme()
Returns a custom bokeh theme based on the style parameters

Returns:
Dict: A Bokeh Theme

class panel.theme.fast.FastThemeMixin(\*, css, name)
Bases: `Parameterized`

**Parameter Definitions**

------------------------------------------------------------------------

`css`` ``=`` ``Filename(check_exists=True,`` ``default=PosixPath('/Users/runner/work/panel/panel/panel/theme/css/fast_variables.css'),`` ``label='Css',`` ``search_paths=[])`

class panel.theme.fast.FastWrapper(\*, object, style, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

Wraps any Panel component and initializes the Fast design provider.

Wrapping a component in this way ensures that so that any children using
the Fast design system have access to the Fast CSS variables.

Methods

|  |  |
|----|----|
| [select](#panel.theme.fast.FastWrapper.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
>

`object`` ``=`` ``Child(allow_None=True,`` ``class_=<class`` ``'panel.viewable.Viewable'>,`` ``label='Object')`
The Panel component to wrap with the Fast design provider.

`style`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.theme.fast.FastStyle'>,`` ``label='Style')`
The style to apply to the Fast design provider

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
