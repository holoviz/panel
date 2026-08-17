# panel.io.handlers module

class panel.io.handlers.FunctionHandler(func: ModifyDoc, \*, trap_exceptions: bool = False)
Bases: `FunctionHandler`

Methods

|  |  |
|----|----|
| [modify_document](#panel.io.handlers.FunctionHandler.modify_document)(doc) | Execute the configured `func` to modify the document. |

modify_document(doc: Document) → None
Execute the configured `func` to modify the
document.

After this method is first executed,
`safe_to_fork` will return
`False`.

class panel.io.handlers.MarkdownHandler(\*args, **kwargs)
Bases:
[PanelCodeHandler](#panel.io.handlers.PanelCodeHandler)

Modify Bokeh documents by creating Dashboard from a Markdown file.

class panel.io.handlers.NotebookHandler(\*, filename: PathLike, argv: list\[str\] = \[\], package: ModuleType \| None = None)
Bases:
[PanelCodeHandler](#panel.io.handlers.PanelCodeHandler)

Modify Bokeh documents by creating Dashboard from a notebook file.

Methods

|  |  |
|----|----|
| [modify_document](#panel.io.handlers.NotebookHandler.modify_document)(doc) | Run Bokeh application code to update a `Document` |

modify_document(doc: Document) → None
Run Bokeh application code to update a
`Document`

Parameters:
doc (Document) : a `Document` to update

class panel.io.handlers.PanelCodeHandler(\*, source: str \| None = None, filename: PathLike, argv: list\[str\] = \[\], package: ModuleType \| None = None, runner: PanelCodeRunner \| None = None)
Bases: `CodeHandler`

Modify Bokeh documents by creating Dashboard from code.

Additionally this subclass adds support for the ability to:

- Log session launch, load and destruction

- Capture document_ready events to track when app is loaded.

- Add profiling support

- Ensure that state.curdoc is set

- Reload the application module if autoreload is enabled

- Track modules loaded during app execution to enable autoreloading

Methods

|  |  |
|----|----|
| [modify_document](#panel.io.handlers.PanelCodeHandler.modify_document)(doc) | Modify an application document in a specified manner. |
| [url_path](#panel.io.handlers.PanelCodeHandler.url_path)() | The last path component for the basename of the configured filename. |

modify_document(doc: Document)
Modify an application document in a specified manner.

When a Bokeh server session is initiated, the Bokeh server asks the
Application for a new Document to service the session. To do this, the
Application first creates a new empty Document, then it passes this
Document to the `modify_document` method of
each of its handlers. When all handlers have updated the Document, it is
used to service the user session.

*Subclasses must implement this method*

Args:
doc (Document) : A Bokeh Document to update in-place

Returns:
Document

url_path() → str \| None
The last path component for the basename of the configured filename.

class panel.io.handlers.PanelCodeRunner(source: str, path: PathLike, argv: list\[str\], package: ModuleType \| None = None)
Bases: `CodeRunner`

Methods

|  |  |
|----|----|
| [run](#panel.io.handlers.PanelCodeRunner.run)(module\[, post_check\]) | Execute the configured source code in a module and run any post checks. |

run(module: ModuleType, post_check: Callable\[\[\], None\] \| None = None) → None
Execute the configured source code in a module and run any post checks.

See bokeh.application.handlers.code_runner for original implementation.

class panel.io.handlers.ScriptHandler(\*, filename: PathLike, argv: list\[str\] = \[\], package: ModuleType \| None = None)
Bases:
[PanelCodeHandler](#panel.io.handlers.PanelCodeHandler)

Modify Bokeh documents by creating Dashboard from a Python script.

panel.io.handlers.capture_code_cell(cell)
Parses a code cell and generates wrapper code to capture the return
value of the cell and any other outputs published inside the cell.

panel.io.handlers.extract_code(filehandle: IO, supported_syntax: tuple\[str, ...\] = ('{pyodide}', 'python')) → str
Extracts Panel application code from a Markdown file.

panel.io.handlers.parse_notebook(filename: str \| os.PathLike \| t.IO, preamble: list\[str\] \| None = None) → tuple\[NotebookNode, str, dict\[str, t.Any\]\]
Parses a notebook on disk and returns a script.

Parameters:
**filename: str \| os.PathLike**
The notebook file to parse.

**preamble: list\[str\]**
Any lines of code to prepend to the parsed code output.

Returns:
nb: nbformat.NotebookNode
nbformat dictionary-like representation of the notebook

code: str
The parsed and converted script

cell_layouts: dict
Dictionary containing the layout and positioning of cells.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
