from bokeh.models import Model
from bokeh.core.properties import Bool, Dict, Any, List


class State(Model):

    json = Bool(False, help="Whether the values point to json files")

    state = Dict(Any, Any, help="Contains the recorded state")

    widgets = Dict(Any, Any)

    values = List(Any)
