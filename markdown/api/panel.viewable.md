# panel.viewable module

Defines the baseclasses that make a component render to a bokeh model
and become viewable including:

- Layoutable: Defines parameters concerned with layout and style

- ServableMixin: Mixin class that defines methods to serve object on
  server

- Renderable: Defines methods to render a component as a bokeh model

- Viewable: Defines methods to view the component in the notebook, on
  the server or in static exports

class panel.viewable.Layoutable(\*, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: `Parameterized`

Layoutable defines shared style and layout related parameters for all
Panel components with a visual representation.

**Parameter Definitions**

------------------------------------------------------------------------

`align`` ``=`` ``Align(allow_refs=True,`` ``default='start',`` ``label='Align')`
Whether the object should be aligned with the start, end or center of
its container. If set as a tuple it will declare (vertical, horizontal)
alignment.

`aspect_ratio`` ``=`` ``Aspect(allow_None=True,`` ``allow_refs=True,`` ``label='Aspect`` ``ratio')`
Describes the proportional relationship between component’s width and
height. This works if any of component’s dimensions are flexible in
size. If set to a number,
`width`` ``/`` ``height`` ``=``         ``aspect_ratio`
relationship will be maintained. Otherwise, if set to
`"auto"`, component’s preferred width and
height will be used to determine the aspect (if not set, no aspect will
be preserved).

`css_classes`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Css`` ``classes',`` ``nested_refs=True)`
CSS classes to apply to the layout.

`design`` ``=`` ``Selector(allow_refs=True,`` ``label='Design',`` ``names={},`` ``objects=[None])`
The design system to use to style components.

`height`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Height')`
The height of the component (in pixels). This can be either fixed or
preferred height, depending on height sizing policy.

`min_width`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Min`` ``width')`
Minimal width of the component (in pixels) if width is adjustable.

`min_height`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Min`` ``height')`
Minimal height of the component (in pixels) if height is adjustable.

`max_width`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``width')`
Maximum width of the component (in pixels) if width is adjustable.

`max_height`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Max`` ``height')`
Maximum height of the component (in pixels) if height is adjustable.

`margin`` ``=`` ``Margin(allow_None=True,`` ``allow_refs=True,`` ``default=0,`` ``label='Margin')`
Allows to create additional space around the component. May be specified
as a two-tuple of the form (vertical, horizontal) or a four-tuple (top,
right, bottom, left).

`styles`` ``=`` ``Dict(allow_refs=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Styles',`` ``nested_refs=True)`
Dictionary of CSS rules to apply to DOM node wrapping the component.

`stylesheets`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``item_type=<class`` ``'str'>,`` ``label='Stylesheets',`` ``nested_refs=True)`
List of stylesheets defined as URLs pointing to .css files or raw CSS
defined as a string.

`tags`` ``=`` ``List(allow_refs=True,`` ``bounds=(0,`` ``None),`` ``default=[],`` ``label='Tags',`` ``nested_refs=True)`
List of arbitrary tags to add to the component. Can be useful for
templating or for storing metadata on the model.

`width`` ``=`` ``Integer(allow_None=True,`` ``allow_refs=True,`` ``bounds=(0,`` ``None),`` ``inclusive_bounds=(True,`` ``True),`` ``label='Width')`
The width of the component (in pixels). This can be either fixed or
preferred width, depending on width sizing policy.

`width_policy`` ``=`` ``Selector(allow_refs=True,`` ``default='auto',`` ``label='Width`` ``policy',`` ``names={},`` ``objects=['auto',`` ``'fixed',`` ``'fit',`` ``'min',`` ``'max'])`
Describes how the component should maintain its width.
`"auto"` Use component’s preferred sizing
policy. `"fixed"` Use exactly
`width` pixels. Component will overflow if it
can’t fit in the available horizontal space.
`"fit"` Use component’s preferred width (if
set) and allow it to fit into the available horizontal space within the
minimum and maximum width bounds (if set). Component’s width neither
will be aggressively minimized nor maximized.
`"min"` Use as little horizontal space as
possible, not less than the minimum width (if set). The starting point
is the preferred width (if set). The width of the component may shrink
or grow depending on the parent layout, aspect management and other
factors. `"max"` Use as much horizontal space
as possible, not more than the maximum width (if set). The starting
point is the preferred width (if set). The width of the component may
shrink or grow depending on the parent layout, aspect management and
other factors.

`height_policy`` ``=`` ``Selector(allow_refs=True,`` ``default='auto',`` ``label='Height`` ``policy',`` ``names={},`` ``objects=['auto',`` ``'fixed',`` ``'fit',`` ``'min',`` ``'max'])`
Describes how the component should maintain its height.
`"auto"` Use component’s preferred sizing
policy. `"fixed"` Use exactly
`height` pixels. Component will overflow if it
can’t fit in the available vertical space.
`"fit"` Use component’s preferred height (if
set) and allow to fit into the available vertical space within the
minimum and maximum height bounds (if set). Component’s height neither
will be aggressively minimized nor maximized.
`"min"` Use as little vertical space as
possible, not less than the minimum height (if set). The starting point
is the preferred height (if set). The height of the component may shrink
or grow depending on the parent layout, aspect management and other
factors. `"max"` Use as much vertical space as
possible, not more than the maximum height (if set). The starting point
is the preferred height (if set). The height of the component may shrink
or grow depending on the parent layout, aspect management and other
factors.

`sizing_mode`` ``=`` ``Selector(allow_refs=True,`` ``label='Sizing`` ``mode',`` ``names={},`` ``objects=['fixed',`` ``'stretch_width',`` ``'stretch_height',`` ``'stretch_both',`` ``'scale_width',`` ``'scale_height',`` ``'scale_both',`` ``None])`
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

`visible`` ``=`` ``Boolean(allow_refs=True,`` ``default=True,`` ``label='Visible')`
Whether the component is visible. Setting visible to false will hide the
component entirely.

class panel.viewable.Viewable(\*, loading, align, aspect_ratio, css_classes, design, height, height_policy, margin, max_height, max_width, min_height, min_width, sizing_mode, styles, stylesheets, tags, visible, width, width_policy, name)
Bases: `Renderable`,
[Layoutable](#panel.viewable.Layoutable),
`ServableMixin`

Viewable is the baseclass all visual components in the panel library are
built on. It defines the interface for declaring any object that
displays itself by transforming the object(s) being wrapped into models
that can be served using bokeh’s layout engine. The class also defines
various methods that allow Viewable objects to be displayed in the
notebook and on bokeh server.

Methods

|  |  |
|----|----|
| [clone](#panel.viewable.Viewable.clone)(\*objects, **params) | Makes a copy of the object sharing the same parameters. |
| [embed](#panel.viewable.Viewable.embed)(\[max_states, max_opts, json, ...\]) | Renders a static version of a panel in a notebook by evaluating the set of states defined by the widgets in the model. |
| [save](#panel.viewable.Viewable.save)(filename\[, title, resources, template, ...\]) | Saves Panel objects to file. |
| [select](#panel.viewable.Viewable.select)(\[selector\]) | Iterates over the Viewable and any potential children in the applying the Selector. |
| [server_doc](#panel.viewable.Viewable.server_doc)(\[doc, title, location\]) | Returns a serveable bokeh Document with the panel attached |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [title="panel.viewable.Layoutable"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, height, min_width,
> min_height, max_width, max_height, margin, styles, stylesheets, tags,
> width, width_policy, height_policy, sizing_mode, visible
>
>

`loading`` ``=`` ``Boolean(allow_refs=True,`` ``default=False,`` ``label='Loading')`
Whether or not the Viewable is loading. If True a loading spinner is
shown on top of the Viewable.

clone(\*objects: t.Any, **params: t.Any) → Self
Makes a copy of the object sharing the same parameters.

Parameters:
**params: Keyword arguments override the parameters on the clone.**

Returns:
Cloned Viewable object

embed(max_states: int = 1000, max_opts: int = 3, json: bool = False, json_prefix: str = '', save_path: str = './', load_path: str \| None = None, progress: bool = False, states={}) → Mimebundle
Renders a static version of a panel in a notebook by evaluating the set
of states defined by the widgets in the model. Note this will only work
well for simple apps with a relatively small state space.

Parameters:
**max_states: int**
The maximum number of states to embed

**max_opts: int**
The maximum number of states for a single widget

**json: boolean (default=True)**
Whether to export the data to json files

**json_prefix: str (default=’’)**
Prefix for JSON filename

**save_path: str (default=’./’)**
The path to save json files to

**load_path: str (default=None)**
The path or URL the json files will be loaded from.

**progress: boolean (default=False)**
Whether to report progress

**states: dict (default={})**
A dictionary specifying the widget values to embed for each widget

save(filename: str \| os.PathLike \| t.IO, title: str \| None = None, resources: \| None = None, template: str \| Template \| None = None, template_variables: dict\[str, t.Any\] = {}, embed: bool = False, max_states: int = 1000, max_opts: int = 3, embed_json: bool = False, json_prefix: str = '', save_path: str = './', load_path: str \| None = None, progress: bool = True, embed_states: dict\[t.Any, t.Any\] = {}, as_png: bool \| None = None, **kwargs) → None\[source\]
Saves Panel objects to file.

Parameters:
**filename: str or file-like object**
Filename to save the plot to

**title: string**
Optional title for the plot

**resources: bokeh resources**
One of the valid bokeh.resources (e.g. CDN or INLINE)

**template:**
passed to underlying io.save

**template_variables:**
passed to underlying io.save

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

**progress: boolean (default=True)**
Whether to report progress

**embed_states: dict (default={})**
A dictionary specifying the widget values to embed for each widget

**as_png: boolean (default=None)**
To save as a .png. If None save_png will be true if filename is string
and ends with png.

select(selector: type \| Callable\[\[Viewable\], bool\] \| None = None) → list\[Viewable\]
Iterates over the Viewable and any potential children in the applying
the Selector.

Parameters:
**selector: type or callable or None**
The selector allows selecting a subset of Viewables by declaring a type
or callable function to filter by.

Returns:
viewables: list(Viewable)

server_doc(doc: Document \| None = None, title: str \| None = None, location: bool \| Location = True) → Document
Returns a serveable bokeh Document with the panel attached

Parameters:
doc : bokeh.Document (optional)
The bokeh Document to attach the panel to as a root, defaults to
bokeh.io.curdoc()

title : str
A string title to give the Document

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

Returns:
doc : bokeh.Document
The bokeh document the panel was attached to

class panel.viewable.Viewer(\*, name)
Bases: `Parameterized`

A baseclass for custom components that behave like a Panel object. By
implementing \_\_panel\_\_ method an instance of this class will behave
like the returned Panel component when placed in a layout, render itself
in a notebook and provide show and servable methods.

Methods

|  |  |
|----|----|
| [servable](#panel.viewable.Viewer.servable)(\[title, location, area, target\]) | Serves the object or adds it to the configured pn.state.template if in a panel serve context, writes to the DOM if in a pyodide context and returns the Panel object to allow it to display itself in a notebook context. |
| [show](#panel.viewable.Viewer.show)(\[title, port, address, ...\]) | Starts a Bokeh server and displays the Viewable in a new tab. |

**Parameter Definitions**

------------------------------------------------------------------------

servable(title: str \| None = None, location: bool \| Location = True, area: str = 'main', target: str \| None = None) → Viewable
Serves the object or adds it to the configured pn.state.template if in a
panel serve context, writes to the DOM if in a pyodide context and
returns the Panel object to allow it to display itself in a notebook
context.

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
The Panel object itself

show(title: str \| None = None, port: int = 0, address: str \| None = None, websocket_origin: str \| None = None, threaded: bool = False, verbose: bool = True, open: bool = True, location: bool \| Location = True, **kwargs) → threading.Thread \| Server
Starts a Bokeh server and displays the Viewable in a new tab.

Parameters:
title : str \| None
A string title to give the Document (if served as an app)

**port: int (optional, default=0)**
Allows specifying a specific port

address : str
The address the server should listen on for HTTP requests.

**websocket_origin: str or list(str) (optional)**
A list of hosts that can connect to the websocket. This is typically
required when embedding a server app in an external web site. If None,
“localhost” is used.

**threaded: boolean (optional, default=False)**
Whether to launch the Server on a separate thread, allowing interactive
use.

**verbose: boolean (optional, default=True)**
Whether to print the address and port

open : boolean (optional, default=True)
Whether to open the server in a new browser tab

location : boolean or panel.io.location.Location
Whether to create a Location component to observe and set the URL
location.

Returns:
server: bokeh.server.Server or panel.io.server.StoppableThread
Returns the Bokeh server instance or the thread the server was launched
on (if threaded=True)

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
