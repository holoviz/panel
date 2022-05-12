import logging

import param

from bokeh.document.events import MessageSentEvent
from bokeh.document.json import MessageSent, Literal, TypedDict
from bokeh.util.serialization import make_id

from ipykernel.comm import CommManager
from tornado.ioloop import IOLoop
from ipywidgets_bokeh.kernel import BokehKernel, SessionWebsocket, WebsocketStream


class MessageSentBuffers(TypedDict):
    kind: Literal["MessageSent"]
    msg_type: str


class MessageSentEventPatched(MessageSentEvent):
    """
    Patches MessageSentEvent with fix that ensures MessageSent event
    does not define msg_data (which is an assumption in BokehJS
    Document.apply_json_patch.)
    """

    def generate(self, references, buffers):
        if not isinstance(self.msg_data, bytes):
            msg = MessageSent(
                kind=self.kind,
                msg_type=self.msg_type,
                msg_data=self.msg_data
            )
        else:
            msg = MessageSentBuffers(
                kind=self.kind,
                msg_type=self.msg_type
            )
            assert buffers is not None
            buffer_id = make_id()
            buf = (dict(id=buffer_id), self.msg_data)
            buffers.append(buf)
        return msg


class PanelSessionWebsocket(SessionWebsocket):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._document = kwargs.pop('document', None)
        self._queue = []
        self._document.on_message("ipywidgets_bokeh", self.receive)

    def send(self, stream, msg_type, content=None, parent=None, ident=None, buffers=None, track=False, header=None, metadata=None):
        msg = self.msg(msg_type, content=content, parent=parent, header=header, metadata=metadata)
        msg['channel'] = stream.channel

        packed = self.pack(msg)

        if buffers is not None and len(buffers) != 0:
            buffers = [packed] + buffers
            nbufs = len(buffers)

            start = 4*(1 + nbufs)
            offsets = [start]

            for buffer in buffers[:-1]:
                start += memoryview(buffer).nbytes
                offsets.append(start)

            u32 = lambda n: n.to_bytes(4, "big")
            items = [u32(nbufs)] + [ u32(offset) for offset in offsets ] + buffers
            data = b"".join(items)
        else:
            data = packed.decode("utf-8")

        event = MessageSentEventPatched(self._document, "ipywidgets_bokeh", data)
        self._queue.append(event)
        self._document.add_next_tick_callback(self._dispatch)

    def _dispatch(self):
        try:
            for event in self._queue:
                self._document.callbacks.trigger_on_change(event)
        except Exception as e:
            param.main.warning(f'ipywidgets event dispatch failed with: {e}')
        finally:
            self._queue = []


class PanelKernel(BokehKernel):

    def __init__(self, key=None, document=None):
        super().__init__()

        self.session = PanelSessionWebsocket(document=document, parent=self, key=key)
        self.stream = self.iopub_socket = WebsocketStream(self.session)
        self.io_loop = IOLoop.current()

        self.iopub_socket.channel = 'iopub'
        self.session.stream = self.iopub_socket
        self.comm_manager = CommManager(parent=self, kernel=self)
        self.shell = None
        self.log = logging.getLogger('fake')

        comm_msg_types = ['comm_open', 'comm_msg', 'comm_close']
        for msg_type in comm_msg_types:
            self.shell_handlers[msg_type] = getattr(self.comm_manager, msg_type)
