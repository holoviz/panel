# panel.template.base module

Templates allow multiple Panel objects to be embedded into custom HTML
documents.

class panel.template.base.BaseTemplate(template: str \| \_Template, items=None, nb_template: str \| \_Template \| None = None, **params)
Bases: `Parameterized`,
`MimeRenderMixin`,
`ServableMixin`,
[ResourceComponent](panel.io.resources.md#panel.io.resources.ResourceComponent)

Methods

|  |  |
|----|----|
| [resolve_resources](#panel.template.base.BaseTemplate.resolve_resources)(\[cdn, extras\]) | Resolves the resources required for this template component. |
| [save](#panel.template.base.BaseTemplate.save)(filename\[, title, resources, embed, ...\]) | Saves Panel objects to file. |
| [select](#panel.template.base.BaseTemplate.select)(\[selector\]) | Iterates over the Template and any potential children in the applying the Selector. |
| [servable](#panel.template.base.BaseTemplate.servable)(\[title, location, area, target\]) | Serves the template and returns self to allow it to display itself in a notebook context. |
| [server_doc](#panel.template.base.BaseTemplate.server_doc)(\[doc, title, location\]) | Returns a servable Document with the template attached. |

**Parameter Definitions**

------------------------------------------------------------------------

`config`` ``=`` ``ClassSelector(class_=<class`` ``'panel.config._base_config'>,`` ``constant=True,`` ``default=_base_config(css_files=[],`` ``js_files={},`` ``js_modules={},`` ``name='_base_config00108',`` ``raw_css=[]),`` ``label='Config')`
Configuration object declaring custom CSS and JS files to load
specifically for this template.

`design`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.base.Design'>,`` ``default=<class`` ``'panel.theme.base.Design'>,`` ``label='Design')`
A Design applies themes to a template.

`location`` ``=`` ``Boolean(default=False,`` ``label='Location')`
Whether to add a Location component to this Template. Note if this is
set to true, the Jinja2 template must either insert all available roots
or explicitly embed the location root with : {{ embed(roots.location)
}}.

`theme`` ``=`` ``ClassSelector(class_=<class`` ``'panel.theme.base.Theme'>,`` ``constant=True,`` ``default=<class`` ``'panel.theme.base.DefaultTheme'>,`` ``label='Theme')`

design
alias of [Design](panel.theme.base.md#panel.theme.base.Design)

resolve_resources(cdn: bool \| t.Literal\['auto'\] = 'auto', extras: dict\[str, dict\[str, str\]\] \| None = None) → ResourcesType
Resolves the resources required for this template component.

Parameters:
**cdn: bool \| Literal\[‘auto’\]**
Whether to load resources from CDN or local server. If set to ‘auto’
value will be automatically determine based on global settings.

**extras: dict\[str, dict\[str, str\]\] \| None**
Additional resources to add to the bundle. Valid resource types include
js, js_modules and css.

Returns:
Dictionary containing JS and CSS resources.

save(filename: str \| PathLike \| IO, title: str \| None = None, resources=None, embed: bool = False, max_states: int = 1000, max_opts: int = 3, embed_json: bool = False, json_prefix: str = '', save_path: str = './', load_path: str \| None = None) → None
Saves Panel objects to file.

Parameters:
**filename: string or file-like object**
Filename to save the plot to

**title: string**
Optional title for the plot

**resources: bokeh resources**
One of the valid bokeh.resources (e.g. CDN or INLINE)

**embed: bool**
Whether the state space should be embedded in the saved file.

**max_states: int**
The maximum number of states to embed

**max_opts: int**
The maximum number of states for a single widget

**embed_json: boolean (default=True)**
Whether to export the data to json files

**json_prefix: str (default=’’)**
Prefix for the auto-generated json directory

**save_path: str (default=’./’)**
The path to save json files to

**load_path: str (default=None)**
The path or URL the json files will be loaded from.

select(selector=None)
Iterates over the Template and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

servable(title: str \| None = None, location: bool \| Location = True, area: str = 'main', target: str \| None = None) → Self
Serves the template and returns self to allow it to display itself in a
notebook context.

Parameters:
title : str
A string title to give the Document (if served as an app)

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

**area: str (deprecated)**
The area of a template to add the component too. Only has an effect if
pn.config.template has been set.

**target: str**
Target area to write to. If a template has been configured on
pn.config.template this refers to the target area in the template while
in pyodide this refers to the ID of the DOM node to write to.

Returns:
The template object

server_doc(doc: Document \| None = None, title: str \| None = None, location: bool \| Location = True) → Document
Returns a servable Document with the template attached.

Parameters:
doc : bokeh.Document (optional)
The Bokeh Document to attach the panel to as a root, defaults to
bokeh.io.curdoc()

title : str
A string title to give the Document

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

Returns:
doc : bokeh.Document
The Bokeh document the panel was attached to.

theme
alias of [DefaultTheme](panel.theme.base.md#panel.theme.base.DefaultTheme)

class panel.template.base.BasicTemplate(\*, \_actions, base_target, base_url, busy_indicator, collapsed_sidebar, favicon, header, header_background, header_color, logo, main, main_max_width, manifest, meta_author, meta_description, meta_keywords, meta_refresh, meta_viewport, modal, notifications, sidebar, sidebar_width, site, site_url, title, config, design, location, theme, name)
Bases:
[BaseTemplate](#panel.template.base.BaseTemplate)

BasicTemplate provides a baseclass for templates with a basic
organization including a header, sidebar and main area. Unlike the more
generic Template class these default templates make it easy for a user
to generate an application with a polished look and feel without having
to write any Jinja2 template themselves.

Methods

|  |  |
|----|----|
| [close_modal](#panel.template.base.BasicTemplate.close_modal)() | Closes the modal area |
| [open_modal](#panel.template.base.BasicTemplate.open_modal)() | Opens the modal area |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](#panel.template.base.BaseTemplate):
> config, design, theme
>
>

`location`` ``=`` ``Boolean(constant=True,`` ``default=True,`` ``label='Location',`` ``readonly=True)`
Whether to add a Location component to this Template. Note if this is
set to true, the Jinja2 template must either insert all available roots
or explicitly embed the location root with : {{ embed(roots.location)
}}.

`busy_indicator`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.widgets.indicators.BooleanIndicator'>,`` ``constant=True,`` ``default=LoadingSpinner(height=20,`` ``width=20),`` ``label='Busy`` ``indicator')`
Visual indicator of application busy state.

`collapsed_sidebar`` ``=`` ``Selector(constant=True,`` ``default=False,`` ``label='Collapsed`` ``sidebar',`` ``names={},`` ``objects=[False])`
Whether the sidebar (if present) is initially collapsed.

`header`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.layout.base.ListLike'>,`` ``constant=True,`` ``label='Header')`
A list-like container which populates the header bar.

`main`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.layout.base.ListLike'>,`` ``constant=True,`` ``label='Main')`
A list-like container which populates the main area.

`main_max_width`` ``=`` ``String(default='',`` ``label='Main`` ``max`` ``width')`
The maximum width of the main area. For example ‘800px’ or ‘80%’. If the
string is ‘’ (default) no max width is set.

`sidebar`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.layout.base.ListLike'>,`` ``constant=True,`` ``label='Sidebar')`
A list-like container which populates the sidebar.

`sidebar_width`` ``=`` ``Integer(default=330,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Sidebar`` ``width')`
The width of the sidebar in pixels. Default is 330.

`modal`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.layout.base.ListLike'>,`` ``constant=True,`` ``label='Modal')`
A list-like container which populates the modal

`notifications`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.io.notifications.NotificationAreaBase'>,`` ``constant=True,`` ``label='Notifications')`
The NotificationArea instance attached to this template. Automatically
added if config.notifications is set, but may also be provided
explicitly.

`logo`` ``=`` ``String(default='',`` ``label='Logo')`
URI of logo to add to the header (if local file, logo is base64 encoded
as URI). Default is ‘’, i.e. not shown.

`favicon`` ``=`` ``String(allow_None=True,`` ``label='Favicon')`
URI of favicon to add to the document head (if local file, favicon is
base64 encoded as URI).

`title`` ``=`` ``String(default='Panel`` ``Application',`` ``label='Title')`
A title to show in the header. Also added to the document head meta
settings and as the browser tab title.

`site`` ``=`` ``String(default='',`` ``label='Site')`
Name of the site. Will be shown in the header and link to the
‘site_url’. Default is ‘’, i.e. not shown.

`site_url`` ``=`` ``String(default='/',`` ``label='Site`` ``url')`
Url of the site and logo. Default is ‘/’.

`manifest`` ``=`` ``String(allow_None=True,`` ``label='Manifest')`
Manifest to add to site.

`meta_description`` ``=`` ``String(default='',`` ``label='Meta`` ``description')`
A meta description to add to the document head for search engine
optimization. For example ‘P.A. Nelson’.

`meta_keywords`` ``=`` ``String(default='',`` ``label='Meta`` ``keywords')`
Meta keywords to add to the document head for search engine
optimization.

`meta_author`` ``=`` ``String(default='',`` ``label='Meta`` ``author')`
A meta author to add to the the document head for search engine
optimization. For example ‘P.A. Nelson’.

`meta_refresh`` ``=`` ``String(default='',`` ``label='Meta`` ``refresh')`
A meta refresh rate to add to the document head. For example ‘30’ will
instruct the browser to refresh every 30 seconds. Default is ‘’, i.e. no
automatic refresh.

`meta_viewport`` ``=`` ``String(default='',`` ``label='Meta`` ``viewport')`
A meta viewport to add to the header.

`base_url`` ``=`` ``String(default='',`` ``label='Base`` ``url')`
Specifies the base URL for all relative URLs in a page. Default is ‘’,
i.e. not the domain.

`base_target`` ``=`` ``Selector(default='_self',`` ``label='Base`` ``target',`` ``names={},`` ``objects=['_blank',`` ``'_self',`` ``'_parent',`` ``'_top'])`
Specifies the base Target for all relative URLs in a page.

`header_background`` ``=`` ``String(default='',`` ``label='Header`` ``background')`
Optional header background color override.

`header_color`` ``=`` ``String(default='',`` ``label='Header`` ``color')`
Optional header text color override.

`_actions`` ``=`` ``ClassSelector(class_=<class`` ``'panel.template.base.TemplateActions'>,`` ``default=TemplateActions(),`` ``label='`` ``actions')`

close_modal() → None
Closes the modal area

open_modal() → None
Opens the modal area

class panel.template.base.Template(template: str \| \_Template, nb_template: str \| \_Template \| None = None, items: dict\[str, t.Any\] \| None = None, **params)
Bases:
[BaseTemplate](#panel.template.base.BaseTemplate)

A Template is a high-level component to render multiple Panel objects
into a single HTML document defined through a Jinja2 template. The
Template object is given a Jinja2 template and then allows populating
this template by adding Panel objects, which are given unique names.
These unique names may then be referenced in the template to insert the
rendered Panel object at a specific location. For instance, given a
Jinja2 template that defines roots A and B like this:

>
>
> \<div\> {{ embed(roots.A) }} \</div\> \<div\> {{ embed(roots.B) }}
> \</div\>
>
>

We can then populate the template by adding panel ‘A’ and ‘B’ to the
Template object:

>
>
> template.add_panel(‘A’, pn.panel(‘A’)) template.add_panel(‘B’,
> pn.panel(‘B’))
>
>

Once a template has been fully populated it can be rendered using the
same API as other Panel objects. Note that all roots that have been
declared using the {{ embed(roots.A) }} syntax in the Jinja2 template
must be defined when rendered.

Since embedding complex CSS frameworks inside a notebook can have
undesirable side-effects and a notebook does not afford the same amount
of screen space a Template may given separate template and nb_template
objects. This allows for different layouts when served as a standalone
server and when used in the notebook.

Methods

|  |  |
|----|----|
| [add_panel](#panel.template.base.Template.add_panel)(name, panel\[, tags\]) | Add panels to the Template, which may then be referenced by the given name using the jinja2 embed macro. |
| [add_variable](#panel.template.base.Template.add_variable)(name, value) | Add parameters to the template, which may then be referenced by the given name in the Jinja2 template. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [title="panel.template.base.BaseTemplate"> class="sourceCode python xref py py-class docutils literal notranslate">panel.template.base.BaseTemplate](#panel.template.base.BaseTemplate):
> config, design, location, theme
>
>

add_panel(name: str, panel: Any, tags: list\[str\] = \[\]) → None
Add panels to the Template, which may then be referenced by the given
name using the jinja2 embed macro.

Parameters:
name : str
The name to refer to the panel by in the template

panel : panel.Viewable
A Panel component to embed in the template.

add_variable(name: str, value: Any) → None
Add parameters to the template, which may then be referenced by the
given name in the Jinja2 template.

Parameters:
name : str
The name to refer to the panel by in the template

value : object
Any valid Jinja2 variable type.

class panel.template.base.TemplateActions(\*, close_modal, open_modal, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: [ReactiveHTML](panel.reactive.md#panel.reactive.ReactiveHTML)

A component added to templates that allows triggering events such as
opening and closing a modal.

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

`open_modal`` ``=`` ``Integer(allow_refs=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Open`` ``modal')`
The number of times the open modal action has been triggered. This is
used to trigger the open modal script.

`close_modal`` ``=`` ``Integer(allow_refs=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Close`` ``modal')`
The number of times the close modal action has been triggered. This is
used to trigger the close modal script.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
