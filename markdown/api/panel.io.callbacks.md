# panel.io.callbacks module

Defines callbacks to be executed on a thread or by scheduling it on a
running bokeh server.

class panel.io.callbacks.PeriodicCallback(\*, callback, count, counter, log, period, running, session_scoped, timeout, name)
Bases: `Parameterized`

Periodic encapsulates a periodic callback which will run both in tornado
based notebook environments and on bokeh server. By default the callback
will run until the stop method is called, but count and timeout values
can be set to limit the number of executions or the maximum length of
time for which the callback will run. The callback may also be started
and stopped by setting the running parameter to True or False
respectively.

Methods

|  |  |
|----|----|
| [start](#panel.io.callbacks.PeriodicCallback.start)() | Starts running the periodic callback. |
| [stop](#panel.io.callbacks.PeriodicCallback.stop)() | Stops running the periodic callback. |

**Parameter Definitions**

------------------------------------------------------------------------

`callback`` ``=`` ``Callable(allow_None=True,`` ``label='Callback')`
The callback to execute periodically.

`counter`` ``=`` ``Integer(default=0,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Counter')`
Counts the number of executions.

`count`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Count')`
Number of times the callback will be executed, by default this is
unlimited.

`log`` ``=`` ``Boolean(default=True,`` ``label='Log')`
Whether the periodic callback should log its actions.

`period`` ``=`` ``Integer(default=500,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Period')`
Period in milliseconds at which the callback is executed.

`running`` ``=`` ``Boolean(default=False,`` ``label='Running')`
Toggles whether the periodic callback is currently running.

`session_scoped`` ``=`` ``Boolean(default=True,`` ``label='Session`` ``scoped')`
If scheduled from inside a user session scopes the callback to that
session.

`timeout`` ``=`` ``Integer(allow_None=True,`` ``inclusive_bounds=(True,`` ``True),`` ``label='Timeout')`
Timeout in milliseconds from the start time at which the callback
expires.

start()
Starts running the periodic callback.

stop()
Stops running the periodic callback.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
