# panel.links module

Defines Links which allow declaring links between bokeh properties.

class panel.links.Callback(source: Reactive, target: JSLinkTarget \| None = None, args: dict\[str, t.Any\] \| None = None, code: dict\[str, str\] \| None = None, **params)
Bases: `Parameterized`

A Callback defines some callback to be triggered when a property changes
on the source object. A Callback can execute arbitrary Javascript code
and will make all objects referenced in the args available in the JS
namespace.

Attributes:
**source**

Methods

|  |  |
|----|----|
| [init](#panel.links.Callback.init)() | Registers the Callback |
| [register_callback](#panel.links.Callback.register_callback)(callback) | Register a LinkCallback providing the implementation for the Link for a particular backend. |
| [unwatch](#panel.links.Callback.unwatch)() | Unregisters the Callback, preventing it from being applied to future renders. |

**Parameter Definitions**

------------------------------------------------------------------------

`args`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``default={},`` ``label='Args')`
A mapping of names to Python objects. These objects are made available
to the callback’s code snippet as the values of named parameters to the
callback.

`code`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Code')`
A dictionary mapping from a source specification to a JS code snippet to
be executed if the source property changes.

init() → None
Registers the Callback

classmethod register_callback(callback: type\[CallbackGenerator\]) → None
Register a LinkCallback providing the implementation for the Link for a
particular backend.

unwatch() → None
Unregisters the Callback, preventing it from being applied to future
renders. Note that if the callback has already been applied to a
rendered model, it will not be removed from that model automatically.

class panel.links.Link(source: Reactive, target: JSLinkTarget \| None = None, **params)
Bases: [Callback](#panel.links.Callback)

A Link defines some connection between a source and target model. It
allows defining callbacks in response to some change or event on the
source object. Instead a Link directly causes some action to occur on
the target, for JS based backends this usually means that a
corresponding JS callback will effect some change on the target in
response to a change on the source.

A Link must define a source object which is what triggers events, but
must not define a target. It is also possible to define bi- directional
links between the source and target object.

Attributes:
**target**

Methods

|  |  |
|----|----|
| [link](#panel.links.Link.link)() | Registers the Link |
| [unlink](#panel.links.Link.unlink)() | Unregisters the Link |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [title="panel.links.Callback"> class="sourceCode python xref py py-class docutils literal notranslate">panel.links.Callback](#panel.links.Callback):
> args, code
>
>

`bidirectional`` ``=`` ``Boolean(default=False,`` ``label='Bidirectional')`
Whether to link source and target in both directions.

`properties`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Properties')`
A dictionary mapping between source specification to target
specification.

link() → None
Registers the Link

unlink() → None
Unregisters the Link

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
