from bokeh.core.properties import (
    Int, Nullable, Required, String,
)
from bokeh.models import Model
from bokeh.protocol import Protocol


class CommManager(Model):

    plot_id = Required(Nullable(String))

    comm_id = Required(Nullable(String))

    client_comm_id = Required(Nullable(String))

    debounce = Int(50)

    timeout = Int(5000)

    def __init__(self, **properties):
        super().__init__(**properties)
        self._protocol = Protocol()

    def assemble(self, msg):
        header = msg['header']
        cls = self._protocol._messages[header['msgtype']]
        return cls(header, msg['metadata'], msg['content'])
