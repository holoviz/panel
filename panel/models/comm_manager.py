from bokeh.core.properties import (
    Int, Nullable, Required, String,
)
from bokeh.core.serialization import Buffer
from bokeh.models import Model
from bokeh.protocol.message import Message


class CommManager(Model):

    def __init__(self, **properties):
        super().__init__(**properties)

    plot_id = Required(Nullable(String))

    comm_id = Required(Nullable(String))

    client_comm_id = Required(Nullable(String))

    debounce = Int(50)

    timeout = Int(5000)

    def assemble(self, msg):
        header = msg['header']
        buffers = msg.pop('_buffers') or {}
        payloads = [Buffer(str(bid), buff.tobytes()) for bid, buff in buffers.items()]
        return Message(header, msg['content'], payloads)
