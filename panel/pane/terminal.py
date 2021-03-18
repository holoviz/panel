from io import StringIO
import sys
import param

from panel.widgets.base import Widget

from ..models import Terminal as _BkTerminal


class Terminal(StringIO, Widget):
    # Set the Bokeh model to use
    _widget_type = _BkTerminal

    # Rename Panel Parameters -> Bokeh Model properties
    # Parameters like title that does not exist on the Bokeh model should be renamed to None
    _rename = {
        "title": None,
        "write_to_console": None,
    }

    # Parameters to be mapped to Bokeh model properties
    object = param.String(doc="""
        The text to write in the terminal""")
    out = param.String(doc="""
        Any text written by the user in the terminal""")
    write_to_console = param.Boolean(False, doc="Weather or not to write to the console. Default is False")

    def __init__(self, **kwargs):
        object = kwargs.get("object", "")
        StringIO.__init__(self, object)
        Widget.__init__(self, **kwargs)

    def write(self, __s):
        if self.object == __s:
            # Hack: for now
            self.object = ""
        self.object = __s

        return StringIO.write(self, __s)

    @param.depends("object", watch=True)
    def _write_to_console(self):
        print("hello")
        if self.write_to_console and self.object:
            sys.__stdout__.write(self.object)

    def fileno(self):
        return -1

    def __repr__(self):
        return "Terminal"
