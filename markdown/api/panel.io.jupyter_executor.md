# panel.io.jupyter_executor module

class panel.io.jupyter_executor.JupyterServerSession(session_id: ID, document: Document, io_loop: IOLoop \| None = None, token: str \| None = None)
Bases: `ServerSession`

class panel.io.jupyter_executor.PanelExecutor(path, token, root_url, resources='server')
Bases: `WSHandler`

The PanelExecutor is intended to be run inside a kernel where it runs a
Panel application renders the HTML and then establishes a Jupyter Comm
channel to communicate with the PanelWSProxy in order to send and
receive messages to and from the frontend.

Methods

|  |  |
|----|----|
| [render_mime](#panel.io.jupyter_executor.PanelExecutor.render_mime)() | Renders the application to an IPython.display.HTML object to be served by the PanelJupyterHandler. |
| [write_message](#panel.io.jupyter_executor.PanelExecutor.write_message)(message\[, binary, locked\]) | Override parent write_message with a version that acquires a write lock before writing. |

render_mime() → Mimebundle
Renders the application to an IPython.display.HTML object to be served
by the PanelJupyterHandler.

async write_message(message: bytes \| str \| dict\[str, Any\], binary: bool = False, locked: bool = True) → None
Override parent write_message with a version that acquires a write lock
before writing.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
