# panel.io.mime_render module

Utilities for executing Python code and rendering the resulting output
using a similar MIME-type based rendering system as implemented by
IPython.

Attempts to limit the actual MIME types that have to be rendered on to a
minimum simplifying frontend implementation:

>
>
> - application/bokeh: Model JSON representation
>
> - text/plain: HTML escaped string output
>
> - text/html: HTML code to insert into the DOM
>
>

class panel.io.mime_render.WriteCallbackStream(on_write=None, escape=True)
Bases: `StringIO`

Methods

|  |  |
|----|----|
| [write](#panel.io.mime_render.WriteCallbackStream.write)(s) | Write string to file. |

write(s)
Write string to file.

Returns the number of characters written, which is always equal to the
length of the string.

panel.io.mime_render.eval_formatter(obj, print_method)
Evaluates a formatter method.

panel.io.mime_render.exec_with_return(code: str, global_context: dict\[str, Any\] \| None = None, stdout: IO \| None = None, stderr: IO \| None = None) → Any
Executes a code snippet and returns the resulting output of the last
line.

Parameters:
**code: str**
The code to execute

**global_context: dict\[str, Any\] \| None**
The globals to inject into the execution context.

**stdout: io.StringIO**
The stream to redirect stdout to.

**stderr: io.StringIO**
The stream to redirect stderr to.

Returns:
The return value of the executed code.

panel.io.mime_render.find_requirements(code: str) → list\[str\]
Finds the packages required in a string of code.

Parameters:
code : str
the Python code to run.

Returns:
`List[str]`
A list of package names that are to be installed for the code to be able
to run.

Examples

\>\>\> code
= "import numpy as np; import
scipy.stats" \>\>\>
find_imports(code)
\['numpy', 'scipy'\]

panel.io.mime_render.format_mime(obj)
Formats object using \_repr_x\_ methods.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
