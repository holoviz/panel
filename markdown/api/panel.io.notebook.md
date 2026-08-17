# panel.io.notebook module

Various utilities for loading JS dependencies and rendering plots inside
the Jupyter notebook.

class panel.io.notebook.JupyterCommJSBinary(id=None, on_msg=None, on_error=None, on_stdout=None, on_open=None)
Bases: `JupyterCommJS`

Extends pyviz_comms.JupyterCommJS with support for repacking binary
buffers.

Methods

|  |  |
|----|----|
| [decode](#panel.io.notebook.JupyterCommJSBinary.decode)(msg) | Decodes messages following Jupyter messaging protocol. |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> `pyviz_comms.Comm`: id
>
>

classmethod decode(msg)
Decodes messages following Jupyter messaging protocol. If JSON decoding
fails data is assumed to be a regular string.

class panel.io.notebook.JupyterCommManagerBinary
Bases: `JupyterCommManager`

client_comm
alias of [JupyterCommJSBinary](#panel.io.notebook.JupyterCommJSBinary)

class panel.io.notebook.Mimebundle(mimebundle)
Bases: `object`

Wraps a generated mimebundle.

panel.io.notebook.block_comm() → Iterator
Context manager to temporarily block comm push

panel.io.notebook.ipywidget(obj: Any, doc=None, **kwargs: Any)
Returns an ipywidget model which renders the Panel object.

Requires jupyter_bokeh to be installed.

Parameters:
**obj: object**
Any Panel object or object which can be rendered with Panel

**doc: bokeh.Document**
Bokeh document the bokeh model will be attached to.

****kwargs: dict**
Keyword arguments passed to the pn.panel utility function

Returns:
Returns an ipywidget model which renders the Panel object.

panel.io.notebook.mime_renderer(obj)
Generates a function that will render the supplied object as a
mimebundle, e.g. to monkey-patch a \_repr_mimebundle\_ method onto an
existing object.

panel.io.notebook.mimebundle_to_html(bundle: dict\[str, Any\]) → str
Converts a MIME bundle into HTML.

panel.io.notebook.push(doc: Document, comm: Comm, binary: bool = True, msg: Message \| None = None) → None
Pushes events stored on the document across the provided comm.

panel.io.notebook.push_notebook(\*objs: Viewable) → None
A utility for pushing updates to the frontend given a Panel object. This
is required when modifying any Bokeh object directly in a notebook
session.

Parameters:
**objs: panel.viewable.Viewable**

panel.io.notebook.render_embed(panel, max_states: int = 1000, max_opts: int = 3, json: bool = False, json_prefix: str = '', save_path: str = './', load_path: str \| None = None, progress: bool = True, states: dict\[Widget, list\[t.Any\]\] = {}) → Mimebundle
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

panel.io.notebook.render_mimebundle(model: Model, doc: Document, comm: Comm, manager: CommManager \| None = None, location: Location \| None = None, resources: str = 'cdn') → tuple\[dict\[str, str\], dict\[str, dict\[str, str\]\]\]
Displays bokeh output inside a notebook using the PyViz display and
comms machinery.

panel.io.notebook.require_components()
Returns JS snippet to load the required dependencies in the classic
notebook using REQUIRE JS.

panel.io.notebook.send(comm: Comm, msg: Message)
Sends a bokeh message across a pyviz_comms.Comm.

panel.io.notebook.show_server(panel: t.Any, notebook_url: str, port: int = 0) → Server
Displays a bokeh server inline in the notebook.

Parameters:
**panel: Viewable**
Panel Viewable object to launch a server for

**notebook_url: str**
The URL of the running Jupyter notebook server

**port: int (optional, default=0)**
Allows specifying a specific port

**server_id: str**
Unique ID to identify the server with

Returns:
server: bokeh.server.Server

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
