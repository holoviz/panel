"""The Terminal Widget makes it easy to create Panel Applications with Terminals.

- For example apps which streams the output of processes or logs.
- For example apps which provide interactive bash, python or ipython terminals"""
import os
import pty
import select
import shlex
import signal
import subprocess
import sys
from io import StringIO

import param

from ..io.callbacks import PeriodicCallback
from ..models import Terminal as _BkTerminal
from .base import Widget


class TerminalSubProcess(param.Parameterized):
    """The TerminalSubProcess is a utility class that makes running subprocesses via the Terminal
    easy"""

    args = param.ClassSelector(
        class_=(str, list),
        doc="""
        The arguments used to run the subprocess. This may be a string or a list. The string cannot
        contain spaces. See subprocess.run docs for more details.""",
    )
    kwargs = param.Dict(
        doc="""Any other arguments to run the subprocess
        See subprocess.run docs for more details"""
    )

    running = param.Boolean(
        False, constant=True,
        doc="""Whether or not the subprocess is running.
        Defaults to False""",
    )

    run = param.Action(
        doc="""Executes subprocess.run in a child process using the args and kwargs
        parameters. The stdin, stdout and stderr is redirected to the Terminal"""
    )

    kill = param.Action("""Kills the subprocess if it is running""")

    _terminal = param.Parameter(
        constant=True,
        doc="""
        The Terminal to which the subprocess is connected""",
    )

    _periodic_callback = param.ClassSelector(
        class_=PeriodicCallback,
        doc="""
        Watches the subprocess for output""",
    )
    _period = param.Integer(50, doc="Period length of _periodic_callback")
    _watcher = param.Parameter(doc="Watches the subprocess for user input")
    _child_pid = param.Integer(0, doc="Child process id")
    _fd = param.Integer(0, doc="Child file descripter")
    _max_read_bytes = param.Integer(1024 * 20)
    _timeout_sec = param.Integer(0)

    def __init__(self, terminal: "Terminal", **params):
        params["_terminal"] = terminal
        super().__init__(**params)

        self.run = self._run
        self.kill = self._kill

    @staticmethod
    def _quote(command):
        return "".join([shlex.quote(c) for c in command])

    def _clean_args(self, args):
        if isinstance(args, str):
            return self._quote(args)
        if isinstance(args, list):
            return [self._quote(arg) for arg in args]
        return args

    def _run(self, caller=None, args=None, **kwargs):
        # Inspiration: https://github.com/cs01/pyxtermjs
        # Inspiration: https://github.com/jupyter/terminado
        if not args:
            args = self.args
        if not args:
            raise ValueError("Error. No args provided")
        if self.running:
            raise ValueError(
                "Error. A child process is already running. Cannot start another."
            )

        args = self._clean_args(args)  # Clean for security reasons

        if self.kwargs:
            kwargs = {**self.kwargs, **kwargs}

        # A fork is an operation whereby a process creates a copy of itself
        # The two processes will continue from here as a PARENT and a CHILD process
        (child_pid, fd) = pty.fork()

        if child_pid == 0:
            # This is the CHILD process fork.
            # Anything printed here will show up in the pty, including the output
            # of this subprocess
            # The process will end by printing 'CompletedProcess(...)' to signal to the parent
            # that it finished.
            try:
                result = subprocess.run(args, **kwargs)
                print(str(result))
            except FileNotFoundError as e:
                print(str(e) + "\nCompletedProcess('FileNotFoundError')")
        else:
            # this is the PARENT process fork.
            self._child_pid = child_pid
            self._fd = fd

            # Todo: Determine if it is better to run this is seperate thread?
            self._periodic_callback = PeriodicCallback(
                callback=self._forward_subprocess_output_to_terminal,
                period=self._period,
            )
            self._periodic_callback.start()

            self._watcher = self._terminal.param.watch(
                self._forward_terminal_input_to_subprocess, "value"
            )
            with param.edit_constant(self):
                self.running = True

    def _kill(self, *events):
        child_pid = self._child_pid
        self._reset()

        if child_pid:
            os.killpg(os.getpgid(child_pid), signal.SIGTERM)
            self._terminal.write(f"\nThe process {child_pid} was killed\n")
        else:
            self._terminal.write("\nNo running process to kill\n")

    def _reset(self):
        self._fd = 0
        self._child_pid = 0
        if self._periodic_callback:
            self._periodic_callback.stop()
            self._periodic_callback = None
        if self._watcher:
            self._terminal.param.unwatch(self._watcher)
        with param.edit_constant(self):
            self.running = False

    @staticmethod
    def _remove_last_line_from_string(value):
        return value[: value.rfind("CompletedProcess")]

    def _forward_subprocess_output_to_terminal(self):
        if self._fd:
            (data_ready, _, _) = select.select([self._fd], [], [], self._timeout_sec)
            if data_ready:
                output = os.read(self._fd, self._max_read_bytes).decode()
                # If Child Process finished it will signal this by appending "CompletedProcess(...)"
                if "CompletedProcess" in output:
                    self._reset()
                    output = self._remove_last_line_from_string(output)
                self._terminal.write(output)

    def _forward_terminal_input_to_subprocess(self, *events):
        if self._fd:
            os.write(self._fd, self._terminal.value.encode())

    @param.depends("args", watch=True)
    def _validate_args(self):
        args = self.args
        if isinstance(args, str) and " " in args:
            raise ValueError(
                f"""The args '{args}' provided contains spaces. They must instead be provided as the
                list {args.split(" ")}"""
            )

    @param.depends("_period", watch=True)
    def _update_periodic_callback(self):
        if self._periodic_callback:
            self._periodic_callback.period = self._period

    def __repr__(self):
        return f"TerminalSubProcess(args={self.args}, running={self.running})"


class Terminal(StringIO, Widget):
    """The Terminal Widget makes it easy to create Panel Applications with Terminals.

    - For example apps which streams the output of processes or logs.
    - For example apps which provide interactive bash, python or ipython terminals"""

    value = param.String(
        label="Input",
        readonly=True,
        doc="""
        User input received from the Terminal. Sent one character at the time.""",
    )
    object = param.String(
        label="Output",
        doc="""
        System output written to the Terminal""",
    )

    clear = param.Action(
        doc="""
        Clears the Terminal"""
    )

    write_to_console = param.Boolean(
        False,
        doc="""
        Weather or not to write to the server console. Default is False""",
    )
    options = param.Dict(
        precedence=-1,
        doc="""
        Initial Options for the Terminal Constructor. cf.
        https://xtermjs.org/docs/api/terminal/interfaces/iterminaloptions/""",
    )

    _rename = {
        "title": None,
        "clear": None,
        "write_to_console": None,
        "value": "input",
        "object": None,
        "_output": "output",
    }

    _output = param.String()
    _clears = param.Integer(doc="Sends a signal to clear the terminal")
    _value_repeats = param.Integer(
        doc="""
        Hack: Sends a signal that the value has been repeated."""
    )

    # Set the Bokeh model to use
    _widget_type = _BkTerminal

    def __init__(self, **kwargs):
        object = kwargs.get("object", "")
        kwargs["_output"] = object
        kwargs["options"] = kwargs.get("options", {})
        StringIO.__init__(self, object)
        Widget.__init__(self, **kwargs)
        self.clear = self._clear
        self._subprocess = None

    def write(self, __s):
        cleaned = __s
        if isinstance(__s, str):
            cleaned = __s
        elif isinstance(__s, bytes):
            cleaned = __s.decode("utf8")
        else:
            cleaned = str(__s)

        if self.object == cleaned:
            # Hack to support writing the same string multiple times in a row
            self.object = ""

        self.object = cleaned

        return StringIO.write(self, cleaned)

    def _clear(self, *events):
        self.object = ""
        self._clears += 1

    @param.depends("object", watch=True)
    def _write(self):
        self._output = self.object

        if self.write_to_console:
            sys.__stdout__.write(self.object)

    @param.depends("_value_repeats", watch=True)
    def _repeat_value_hack(self):
        value = self.value
        self.value = ""
        self.value = value

    def fileno(self):
        return -1

    def __repr__(self):
        return f"Terminal(id={id(self)})"

    @property
    def subprocess(self):
        """The subprocess enables running commands like 'ls', ['ls', '-l'], 'bash', 'python' and
        'ipython' in the terminal"""
        if not self._subprocess:
            self._subprocess = TerminalSubProcess(self)
        return self._subprocess
