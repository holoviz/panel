from bokeh.core.properties import Any, Dict, Either, String, Null, Tuple
from bokeh.models.widgets import Markup


class IDOM(Markup):

    importSourceUrl = String()

    event = Tuple(Any, Any)

    msg = Either(Dict(String, Any), Null)
