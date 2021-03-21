from io import StringIO
import sys
import param
import signal
import shlex
import pty
import os
import select
import subprocess

from .base import Widget
from ..io.callbacks import PeriodicCallback
from ..models import Terminal as _BkTerminal
import panel as pn

_MAX_READ_BYTES = 1024 * 20

class TerminalSubProcess(param.Parameterized):
    command = param.String()
    # Todo: Determine if `start` is a better name
    run = param.Action(label="Start")
    # Todo: Determine if `stop` is a better name
    kill = param.Action(label="Stop")

    # Todo: Set this to read only
    running = param.Boolean(False)

    _periodic_callback = param.ClassSelector(class_=PeriodicCallback)
    _watcher = param.Parameter()
    # Todo: Determine how this could be ClassSelector with class_=Terminal
    terminal = param.Parameter(constant=True)



    _child_pid = param.Integer(0, doc="""
        Process id of the child process that is running the command.
        """)
    _fd = param.Integer(0, doc="""
        A file descriptor connected to the controlling terminal of the child process that is
        running the command""")
    _max_read_bytes = param.Integer(1024 * 20)
    _timeout_sec = param.Integer(0)
    _exit_message = param.String("\nexit")

    def __init__(self, terminal: 'Terminal', **params):
        params["terminal"]=terminal
        super().__init__(**params)

        self.run = self._run
        self.kill = self._kill

    def _run(self, caller=None, command=None):
        if not command:
            command = self.command
        if not command:
            raise ValueError("Error. No command provided")
        if self._child_pid or self._fd or self.running:
            raise ValueError("Error. A child process is already running. Cannot start another.")

        command = "".join(shlex.quote(c) for c in command) # Clean for security reasons

        # A fork is an operation whereby a process creates a copy of itself
        # The two processes will continue from here as a PARENT and a CHILD process
        (child_pid, fd) = pty.fork()

        if child_pid == 0:
            # this is the CHILD process fork.
            # anything printed here will show up in the pty, including the output
            # of this subprocess
            try:
                result = subprocess.run(command)
                print(str(result))
            except FileNotFoundError as e:
                print(str(e) + "\nCompletedProcess('FileNotFoundError')")
            # Hack: Used to signal to Parent that the process finished

        else:
            # this is the PARENT process fork.
            # store child fd and pid
            self._child_pid=child_pid
            self._fd=fd

            # and start running
            # Todo: Determine if it is better to run this is seperate thread?
            self._periodic_callback = PeriodicCallback(callback=self.read_and_forward_pty_output, period=50)
            self._periodic_callback.start()

            self._watcher = self.terminal.param.watch(self._update_pty, "value")
            self.running = True

    def _kill(self, *events):
        child_pid = self._child_pid
        self._reset()

        if child_pid:
            os.killpg(os.getpgid(child_pid), signal.SIGTERM)
        self.terminal.write(f"\nThe process {child_pid} was killed\n")

    def _reset(self):
        self._fd = 0
        self._child_pid = 0
        if self._periodic_callback:
            self._periodic_callback.stop()
            self._periodic_callback = None
        if self._watcher:
            self.terminal.param.unwatch(self._watcher)
        self.running=False

    @staticmethod
    def remove_last_line_from_string(s):
        return s[:s.rfind('CompletedProcess')]

    def read_and_forward_pty_output(self):
        if self._fd:
            (data_ready, _, _) = select.select([self._fd], [], [], self._timeout_sec)
            if data_ready:
                output = os.read(self._fd, self._max_read_bytes).decode()
                # If Child Process finished it will signal this by appending "CompletedProcess(...)"
                if "CompletedProcess" in output:
                    self._reset()
                    output = self.remove_last_line_from_string(output)
                self.terminal.write(output)
            elif not self._pid_is_running():
                self._reset()

    def _pid_is_running(self):
        """ Check For the existence of a unix pid. """
        try:
            os.kill(self._child_pid, 0)
        except OSError:
            return False # It is not running
        else:
            return True # It is running

    def _update_pty(self, *events):
        if self._fd:
            os.write(self._fd, self.terminal.value.encode())

    def __repr__(self):
        return "TerminalSubProcess"


class Terminal(StringIO, Widget):
    # Parameters to be mapped to Bokeh model properties
    value = param.String(label="Input", readonly=True, doc="""
        User input from the terminal""")
    object = param.String(label="Output", doc="""
        System output to the terminal""")
    line_feeds = param.Integer(readonly=True)
    clear = param.Action()
    write_to_console = param.Boolean(False, doc="Weather or not to write to the console. Default is False")
    options = param.Dict(doc="""
        Initial Options for the Terminal Constructor. cf.
        https://xtermjs.org/docs/api/terminal/interfaces/iterminaloptions/""")
    _output = param.String()
    _clears = param.Integer(doc="Sends a signal to clear the terminal")
    _value_repeats = param.Integer(doc="Hack: Sends a signal that the value has been repeated.")

        # Set the Bokeh model to use
    _widget_type = _BkTerminal

    # Rename Panel Parameters -> Bokeh Model properties
    # Parameters like title that does not exist on the Bokeh model should be renamed to None
    _rename = {
        "title": None,
        "clear": None,
        "write_to_console": None,
        "value": "input",
        "object": None,
        "_output": "output",
    }

    def __init__(self, **kwargs):
        object = kwargs.get("object", "")
        kwargs["_output"]=object
        kwargs["options"]=kwargs.get("options", {})
        StringIO.__init__(self, object)
        Widget.__init__(self, **kwargs)
        self.clear = self._clear
        self._subprocess = None

    def write(self, __s):
        cleaned = __s
        if isinstance(__s, str):
            cleaned=__s
        elif isinstance(__s, bytes):
            cleaned=__s.decode("utf8")
        else:
            cleaned = str(s)

        if self.object == cleaned:
            # Hack for now
            self.object = ""

        self.object = cleaned

        return StringIO.write(self, cleaned)

    def _clear(self, *events):
        self.object = ""
        self._clears +=1

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
        return "Terminal"

    @property
    def subprocess(self):
        if not self._subprocess:
            self._subprocess = TerminalSubProcess(self)
        return self._subprocess