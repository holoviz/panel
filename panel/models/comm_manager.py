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
        buffers = msg.pop('_buffers') or {}
        header['num_buffers'] = len(buffers)
        cls = self._protocol._messages[header['msgtype']]
        msg_obj = cls(header, msg['metadata'], msg['content'])
        for (bid, buff) in buffers.items():
            msg_obj.assemble_buffer({'id': bid}, buff.tobytes())
        return msg_obj
