# panel.widgets.terminal module

The Terminal Widget makes it easy to create Panel Applications with
Terminals.

- For example apps which streams the output of processes or logs.

- For example apps which provide interactive bash, python or ipython
  terminals

class panel.widgets.terminal.Terminal(output=None, **params)
Bases: [Widget](panel.widgets.base.md#panel.widgets.base.Widget)

The Terminal widget renders a live terminal in the browser using the
xterm.js library making it possible to display logs or even provide an
interactive terminal in a Panel application.

Reference:
[https://panel.holoviz.org/reference/widgets/Terminal.html](https://panel.holoviz.org/reference/widgets/Terminal.html)

Example:

\>\>\>
Terminal(
...  "Welcome to the Panel
Terminal!",
options={"cursorBlink":
True}
... )

Attributes:
**closed**

[subprocess](#panel.widgets.terminal.Terminal.subprocess)
The subprocess enables running commands like ‘ls’, \[‘ls’, ‘-l’\],
‘bash’, ‘python’ and ‘ipython’ in the terminal.

Methods

|                |     |
|----------------|-----|
| **fileno**     |     |
| **flush**      |     |
| **getvalue**   |     |
| **read**       |     |
| **readable**   |     |
| **readlines**  |     |
| **seekable**   |     |
| **writable**   |     |
| **write**      |     |
| **writelines** |     |

**Parameter Definitions**

------------------------------------------------------------------------

Parameters inherited from:

>
>
> [class="reference internal" title="panel.widgets.base.WidgetBase"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.WidgetBase](panel.widgets.base.md#panel.widgets.base.WidgetBase):
> label
>
> [class="reference internal" title="panel.viewable.Layoutable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Layoutable](panel.viewable.md#panel.viewable.Layoutable):
> align, aspect_ratio, css_classes, design, min_width, min_height,
> max_width, max_height, styles, stylesheets, tags, width_policy,
> height_policy, sizing_mode, visible
>
> [class="reference internal" title="panel.viewable.Viewable"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.viewable.Viewable](panel.viewable.md#panel.viewable.Viewable):
> loading
>
> [class="reference internal" title="panel.widgets.base.Widget"> class="pre"> class="sourceCode python xref py py-class docutils literal notranslate">panel.widgets.base.Widget](panel.widgets.base.md#panel.widgets.base.Widget):
> height, margin, width, disabled
>
>

`value`` ``=`` ``String(constant=True,`` ``default='',`` ``readonly=True)`
User input received from the Terminal. Sent one character at the time.

`clear`` ``=`` ``Action(allow_None=True,`` ``constant=True,`` ``label='Clear')`
Clears the Terminal.

`options`` ``=`` ``Dict(class_=<class`` ``'dict'>,`` ``default={},`` ``label='Options')`
Initial Options for the Terminal Constructor. cf. [https://xtermjs.org/docs/api/terminal/interfaces/iterminaloptions/](https://xtermjs.org/docs/api/terminal/interfaces/iterminaloptions/)

`output`` ``=`` ``String(default='',`` ``label='Output')`
System output written to the Terminal

`ncols`` ``=`` ``Integer(constant=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Ncols',`` ``readonly=True)`
The number of columns in the terminal.

`nrows`` ``=`` ``Integer(constant=True,`` ``default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Nrows',`` ``readonly=True)`
The number of rows in the terminal.

`write_to_console`` ``=`` ``Boolean(default=False,`` ``label='Write`` ``to`` ``console')`
Whether or not to write to the server console.

`_clears`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``clears')`
Sends a signal to clear the terminal

`_output`` ``=`` ``String(default='',`` ``label='`` ``output')`

property subprocess
The subprocess enables running commands like ‘ls’, \[‘ls’, ‘-l’\],
‘bash’, ‘python’ and ‘ipython’ in the terminal.

class panel.widgets.terminal.TerminalSubprocess(terminal, **kwargs)
Bases: `Parameterized`

The TerminalSubProcess is a utility class that makes running
subprocesses via the Terminal easy.

Methods

|  |  |
|----|----|
| [run](#panel.widgets.terminal.TerminalSubprocess.run)(\*args, **kwargs) | Runs a subprocess command. |

**Parameter Definitions**

------------------------------------------------------------------------

`args`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=(<class`` ``'str'>,`` ``<class`` ``'list'>),`` ``label='Args')`
The arguments used to run the subprocess. This may be a string or a
list. The string cannot contain spaces. See subprocess.run docs for more
details.

`kill`` ``=`` ``Action(allow_None=True,`` ``constant=True,`` ``label='Kill')`
Kills the running process

`kwargs`` ``=`` ``Dict(allow_None=True,`` ``class_=<class`` ``'dict'>,`` ``label='Kwargs')`
Any other arguments to run the subprocess. See subprocess.run docs for
more details.

`running`` ``=`` ``Boolean(constant=True,`` ``default=False,`` ``label='Running')`
Whether or not the subprocess is running.

`_child_pid`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``child`` ``pid')`
Child process id

`_fd`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``fd')`
Child file descriptor.

`_max_read_bytes`` ``=`` ``Integer(default=20480,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``max`` ``read`` ``bytes')`

`_periodic_callback`` ``=`` ``ClassSelector(allow_None=True,`` ``class_=<class`` ``'panel.io.callbacks.PeriodicCallback'>,`` ``label='`` ``periodic`` ``callback')`
Watches the subprocess for output

`_period`` ``=`` ``Integer(default=50,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``period')`
Period length of \_periodic_callback

`_terminal`` ``=`` ``Parameter(allow_None=True,`` ``constant=True,`` ``label='`` ``terminal')`
The Terminal to which the subprocess is connected.

`_timeout_sec`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='`` ``timeout`` ``sec')`

`_watcher`` ``=`` ``Parameter(allow_None=True,`` ``label='`` ``watcher')`
Watches the subprocess for user input

run(\*args, **kwargs)
Runs a subprocess command.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
