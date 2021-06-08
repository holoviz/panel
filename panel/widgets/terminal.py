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


class TerminalSubprocess(param.Parameterized):
    """
    The TerminalSubProcess is a utility class that makes running
    subprocesses via the Terminal easy.
    """

    args = param.ClassSelector(class_=(str, list), doc="""
        The arguments used to run the subprocess. This may be a string
        or a list. The string cannot contain spaces. See subprocess.run
        docs for more details.""")

    kwargs = param.Dict(doc="""
        Any other arguments to run the subprocess. See subprocess.run
        docs for more details.""" )

    running = param.Boolean(default=False, constant=True, doc="""
        Whether or not the subprocess is running.""")

    _child_pid = param.Integer(0, doc="Child process id")

    _fd = param.Integer(0, doc="Child file descriptor.")

    _max_read_bytes = param.Integer(1024 * 20)

    _periodic_callback = param.ClassSelector(class_=PeriodicCallback, doc="""
        Watches the subprocess for output""")

    _period = param.Integer(50, doc="Period length of _periodic_callback")

    _terminal = param.Parameter(constant=True, doc="""
        The Terminal to which the subprocess is connected.""")

    _timeout_sec = param.Integer(0)

    _watcher = param.Parameter(doc="Watches the subprocess for user input")

    def __init__(self, terminal, **kwargs):
        super().__init__(_terminal=terminal, **kwargs)

    @staticmethod
    def _quote(command):
        return "".join([shlex.quote(c) for c in command])

    def _clean_args(self, args):
        if isinstance(args, str):
            return self._quote(args)
        if isinstance(args, list):
            return [self._quote(arg) for arg in args]
        return args

    def run(self, *args, **kwargs):
        """
        Runs a subprocess command.
        """
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

    def kill(self):
        """
        Kills the subprocess.
        """
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

    def __repr__(self, depth=None):
        return f"TerminalSubprocess(args={self.args}, running={self.running})"


class Terminal(StringIO, Widget):
    """
    The Terminal widget renders a live terminal in the browser using
    the xterm.js library making it possible to display logs or even
    provide an interactive terminal in a Panel application.
    """

    options = param.Dict(default={}, precedence=-1, doc="""
        Initial Options for the Terminal Constructor. cf.
        https://xtermjs.org/docs/api/terminal/interfaces/iterminaloptions/""")

    output = param.String(default="", doc="""
        System output written to the Terminal""")

    value = param.String(label="Input", readonly=True, doc="""
        User input received from the Terminal. Sent one character at the time.""")

    write_to_console = param.Boolean(default=False, doc="""
        Weather or not to write to the server console. Default is False""")

    _clears = param.Integer(doc="Sends a signal to clear the terminal")

    _output = param.String(default="")
    
    _value_repeats = param.Integer(
        doc="""
        Hack: Sends a signal that the value has been repeated."""
    )

    _rename = {
        "clear": None,
        "output": None,
        "_output": "output",
        "value": "input",
        "write_to_console": None,
    }

    # Set the Bokeh model to use
    _widget_type = _BkTerminal

    def __init__(self, output=None, **kwargs):
        output = output or ""
        StringIO.__init__(self, output)
        Widget.__init__(self, output=output, _output=output, **kwargs)
        self._subprocess = None

    def write(self, __s):
        cleaned = __s
        if isinstance(__s, str):
            cleaned = __s
        elif isinstance(__s, bytes):
            cleaned = __s.decode("utf8")
        else:
            cleaned = str(__s)

        if self.output == cleaned:
            # Hack to support writing the same string multiple times in a row
            self._output = ""

        self._output = cleaned
        self.output += cleaned

        return StringIO.write(self, cleaned)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        model = super()._get_model(doc, root, parent, comm)
        model.output = self.output
        return model

    def clear(self):
        """
        Clears all output on the terminal.
        """
        self.output = ""
        self._clears += 1

    @param.depends("_output", watch=True)
    def _write(self):
        if self.write_to_console:
            sys.__stdout__.write(self._output)

    @param.depends("_value_repeats", watch=True)
    def _repeat_value_hack(self):
        self.param.trigger('value')

    def fileno(self):
        return -1

    def __repr__(self, depth=None):
        return f"Terminal(id={id(self)})"

    @property
    def subprocess(self):
        """
        The subprocess enables running commands like 'ls', ['ls',
        '-l'], 'bash', 'python' and 'ipython' in the terminal.
        """
        if not self._subprocess:
            self._subprocess = TerminalSubprocess(self)
        return self._subprocess
