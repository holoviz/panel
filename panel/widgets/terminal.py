from io import StringIO
import sys
import param

from panel.widgets.base import Widget

from ..models import Terminal as _BkTerminal


class Terminal(StringIO, Widget):
    # Parameters to be mapped to Bokeh model properties
    value = param.String(doc="""
        User input from the terminal""")
    object = param.String(doc="""
        System output to the terminal""")
    write_to_console = param.Boolean(False, doc="Weather or not to write to the console. Default is False")
    clear = param.Action()

    _output = param.String()
    _clears = param.Integer(doc="Sends a signal to clear the terminal")

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
        StringIO.__init__(self, object)
        Widget.__init__(self, **kwargs)

        self.clear = self._clear

    def write(self, __s):
        cleaned = __s
        if isinstance(__s, str):
            cleaned=__s
        elif isinstance(__s, bytes):
            cleaned=__s.decode("utf8")
        else:
            cleaned = str(s)

        if self.object == cleaned:
            # Hack: for now
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

    def fileno(self):
        return -1

    def __repr__(self):
        return "Terminal"
