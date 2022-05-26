from bokeh.core.properties import (
    Any, Dict, Either, Null, String, Tuple,
)
from bokeh.models import HTMLBox


class IDOM(HTMLBox):

    importSourceUrl = String()

    event = Tuple(Any, Any)

    msg = Either(Dict(String, Any), Null)
