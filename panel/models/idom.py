from bokeh.core.properties import Any, Dict, String
from bokeh.models.widgets import Markup


class IDOM(Markup):

    importSourceUrl = String()

    event = Dict(String, Any)

    msg = Dict(String, Any)
