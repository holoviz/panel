import param

from panel.widgets.base import Widget

from ..models import Terminal as _BkTerminal


class Terminal(Widget):
    # Set the Bokeh model to use
    _widget_type = _BkTerminal

    # Rename Panel Parameters -> Bokeh Model properties
    # Parameters like title that does not exist on the Bokeh model should be renamed to None
    _rename = {
        "title": None,
    }

    # Parameters to be mapped to Bokeh model properties
    object = param.String(doc="""
        The text to write in the terminal""")
    out = param.String(doc="""
        Any text written by the user in the terminal""")
