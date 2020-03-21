from bokeh.models import Model
from bokeh.core.properties import String, Int
from bokeh.protocol import Protocol


class CommManager(Model):

    plot_id = String()

    comm_id = String()

    client_comm_id = String()

    debounce = Int(50)

    timeout = Int(5000)

    def __init__(self, **properties):
        super().__init__(**properties)
        self._protocol = Protocol()

    def assemble(self, msg):
        header = msg['header']
        cls = self._protocol._messages[header['msgtype']]
        return cls(header, msg['metadata'], msg['content'])
