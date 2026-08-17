# panel.io.resources module

Patches bokeh resources to make it easy to add external JS and CSS
resources via the panel.config object.

class panel.io.resources.ResourceComponent
Bases: `object`

Mix-in class for components that define a set of resources that have to
be resolved.

resolve_resources(cdn: bool \| t.Literal\['auto'\] = 'auto', extras: dict\[str, dict\[str, str\]\] \| None = None) → ResourcesType
Resolves the resources required for this component.

Parameters:
**cdn: bool \| Literal\[‘auto’\]**
Whether to load resources from CDN or local server. If set to ‘auto’
value will be automatically determine based on global settings.

**extras: dict\[str, dict\[str, str\]\] \| None**
Additional resources to add to the bundle. Valid resource types include
js, js_modules and css.

Returns:
Dictionary containing JS and CSS resources.

class panel.io.resources.Resources(\*args, absolute=False, notebook=False, **kwargs)
Bases: `Resources`

adjust_paths(resources)
Computes relative and absolute paths for resources.

clone(\*, components=None) → \[source\]
Make a clone of a resources instance allowing to override its
components.

extra_resources(resources, resource_type)
Adds resources for ReactiveHTML components.

panel.io.resources.component_resource_path(component, attr: str, path: str \| PathLike) → str
Generates a canonical URL for a component resource.

To be used in conjunction with the
panel.io.server.ComponentResourceHandler which allows dynamically
resolving resources defined on components.

panel.io.resources.get_env()
Get the correct Jinja2 Environment, also for frozen scripts.

class panel.io.resources.json_dumps(\*, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, default=None)
Bases: `JSONEncoder`

default(obj)
Implement this method in a subclass such that it returns a serializable
object for `o`, or calls the base
implementation (to raise a `TypeError`).

For example, to support arbitrary iterators, you could implement default
like this:

def
default(self,
o):
try:
iterable =
iter(o)
except
TypeError:
pass
else:
return
list(iterable)
\# Let the base class default method raise the
TypeError return
super().default(o)

panel.io.resources.patch_model_css(root: Model, dist_url: str)
Temporary patch for Model.css property used by Panel to provide
stylesheets for components.

ALERT: Should find better solution before official Bokeh 3.x compatible
release

panel.io.resources.process_raw_css(raw_css: list\[str\]) → list\[str\]
Converts old-style Bokeh\<3 compatible CSS to Bokeh 3 compatible CSS.

panel.io.resources.resolve_custom_path(obj, path: str \| PathLike, relative: bool = False) → Path \| None
Attempts to resolve a path relative to some component.

Parameters:
**obj: type \| object**
The component to resolve the path relative to.

**path: str \| os.PathLike**
Absolute or relative path to a resource.

**relative: bool**
Whether to return a relative path.

Returns:
path: pathlib.Path \| None

panel.io.resources.resolve_resource_cdn(resource: str \| PathLike) → str \| PathLike
Resolves a CDN URL given a file path that is relative to an extension
dist directory.

panel.io.resources.resolve_stylesheet(cls, stylesheet: str, attribute: str \| None = None)
Resolves a stylesheet definition, e.g. originating on a component
Reactive.\_stylesheets or a Design.modifiers attribute. Stylesheets may
be defined as one of the following:

- Absolute URL defined with http(s) protocol

- A path relative to the component

- A raw css string

Parameters:
**cls: type \| object**
Object or class defining the stylesheet

**stylesheet: str**
The stylesheet definition

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
