import os

from bokeh.models import Model
from bokeh.core.properties import Bool, Dict, Any, List

from ..compiler import CUSTOM_MODELS


class State(Model):

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'state.ts')

    json = Bool(False, help="Whether the values point to json files")

    state = Dict(Any, Any, help="Contains the recorded state")

    widgets = Dict(Any, Any)

    values = List(Any)


CUSTOM_MODELS['panel.models.state.State'] = State
