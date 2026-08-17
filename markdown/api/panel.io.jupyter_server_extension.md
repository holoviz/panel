# panel.io.jupyter_server_extension module

The Panel jupyter_server_extension implements Jupyter RequestHandlers
that allow a Panel application to run inside Jupyter kernels. This
allows Panel applications to be served in the kernel (and therefore the
environment) they were written for.

The PanelJupyterHandler may be given the path to a notebook, .py file or
Lumen .yaml file. It will then attempt to resolve the appropriate kernel
based on the kernelspec or a query parameter. Once the kernel has been
provisioned the handler will execute a code snippet on the kernel which
creates a PanelExecutor. The PanelExecutor creates a
bokeh.server.session.ServerSession and connects it to a Jupyter Comm.
The PanelJupyterHandler will then serve the result of executor.render().

Once the frontend has rendered the HTML it will send a request to open a
WebSocket will be sent to the PanelWSProxy. This in turns forwards any
messages it receives via the kernel.shell_channel and the Comm to the
PanelExecutor. This way we proxy any WS messages being sent to and from
the server to the kernel.

class panel.io.jupyter_server_extension.PanelBaseHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: `JupyterHandler`

Methods

|                |     |
|----------------|-----|
| **initialize** |     |
| **nb_path**    |     |

initialize(**kwargs)

class panel.io.jupyter_server_extension.PanelJupyterHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: [PanelBaseHandler](#panel.io.jupyter_server_extension.PanelBaseHandler)

The PanelJupyterHandler expects to be given a path to a notebook, .py
file or Lumen .yaml file. Based on the kernelspec in the notebook or the
kernel query parameter it will then provision a Jupyter kernel to run
the Panel application in.

Once the kernel is launched it will instantiate a PanelExecutor inside
the kernel and serve the HTML returned by it. If successful it will
store the kernel and comm_id on panel.state.

Methods

|                |     |
|----------------|-----|
| **get**        |     |
| **initialize** |     |

initialize(**kwargs)

class panel.io.jupyter_server_extension.PanelLayoutHandler(application: Application, request: HTTPServerRequest, **kwargs: Any)
Bases: [PanelBaseHandler](#panel.io.jupyter_server_extension.PanelBaseHandler)

Methods

|         |     |
|---------|-----|
| **get** |     |

class panel.io.jupyter_server_extension.PanelWSProxy(tornado_app, \*args, **kw)
Bases: `WSHandler`,
`JupyterHandler`

The PanelWSProxy serves as a proxy between the frontend and the Jupyter
kernel that is running the Panel application. It send and receives Bokeh
protocol messages via a Jupyter Comm.

Methods

|  |  |
|----|----|
| [check_origin](#panel.io.jupyter_server_extension.PanelWSProxy.check_origin)(\[origin_to_satisfy_tornado\]) | Implement a check_origin policy for Tornado to call. |
| [get_current_user](#panel.io.jupyter_server_extension.PanelWSProxy.get_current_user)() | Delegate to the synchronous `get_user` method of the auth provider |
| [on_close](#panel.io.jupyter_server_extension.PanelWSProxy.on_close)() | Clean up when the connection is closed. |
| [on_message](#panel.io.jupyter_server_extension.PanelWSProxy.on_message)(fragment) | Process an individual wire protocol fragment. |
| [open](#panel.io.jupyter_server_extension.PanelWSProxy.open)(path, \*args, **kwargs) | Initialize a connection to a client. |
| [prepare](#panel.io.jupyter_server_extension.PanelWSProxy.prepare)() | Async counterpart to `get_current_user` |

|                |     |
|----------------|-----|
| **initialize** |     |

check_origin(origin_to_satisfy_tornado: str = '') → bool
Implement a check_origin policy for Tornado to call.

The supplied origin will be compared to the Bokeh server allowlist. If
the origin is not allow, an error will be logged and
`False` will be returned.

Args:
origin (str) :
The URL of the connection origin

Returns:
bool, True if the connection is allowed, False otherwise

get_current_user() → str
Delegate to the synchronous `get_user` method
of the auth provider

initialize(\*args, **kwargs)

on_close() → None
Clean up when the connection is closed.

async on_message(fragment: str \| bytes) → None
Process an individual wire protocol fragment.

The websocket RFC specifies opcodes for distinguishing text frames from
binary frames. Tornado passes us either a text or binary string
depending on that opcode, we have to look at the type of the fragment to
see what we got.

Args:
fragment (unicode or bytes) : wire fragment to process

open(path, \*args, **kwargs) → None
Initialize a connection to a client.

Returns:
None

async prepare()
Async counterpart to `get_current_user`

async panel.io.jupyter_server_extension.ensure_async(obj: Awaitable \| t.Any) → t.Any
Convert a non-awaitable object to a coroutine if needed, and await it if
it was not already awaited.

panel.io.jupyter_server_extension.generate_executor(path: str, token: str, root_url: str) → str
Generates the code to instantiate a PanelExecutor that is to be be run
on the kernel to start a server session.

Parameters:
**path: str**
The path of the Panel application to execute.

**token: str**
The Bokeh JWT token containing the session_id, request arguments,
headers and cookies.

**root_url: str**
The root_url the server is running on.

Returns:
The code to be executed inside the kernel.

panel.io.jupyter_server_extension.url_path_join(\*pieces)
Join components of url into a relative url Use to prevent double slash
when joining subpath. This will leave the initial and final / in place

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
