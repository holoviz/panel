import logging

from bokeh.document.events import MessageSentEvent
from ipykernel.comm import CommManager
from ipywidgets_bokeh.kernel import BokehKernel, SessionWebsocket, WebsocketStream


class PanelSessionWebsocket(SessionWebsocket):

    def __init__(self, *args, **kwargs):
        self._document = kwargs.pop('document', None)
        self._queue = []
        super().__init__(*args, **kwargs)

    def send(self, stream, msg_type, content=None, parent=None, ident=None, buffers=None, track=False, header=None, metadata=None):
        msg = self.msg(msg_type, content=content, parent=parent, header=header, metadata=metadata)
        msg['channel'] = stream.channel

        doc = self._document
        doc.on_message("ipywidgets_bokeh", self.receive)

        packed = self.pack(msg)

        if buffers is not None and len(buffers) != 0:
            buffers = [packed] + buffers
            nbufs = len(buffers)

            start = 4*(1 + nbufs)
            offsets = [start]

            for buffer in buffers[:-1]:
                start += len(buffer)
                offsets.append(start)

            u32 = lambda n: n.to_bytes(4, "big")
            items = [u32(nbufs)] + [ u32(offset) for offset in offsets ] + buffers
            data = b"".join(items)
        else:
            data = packed.decode("utf-8")

        event = MessageSentEvent(doc, "ipywidgets_bokeh", data)
        self._queue.append(event)
        doc.add_next_tick_callback(self._dispatch)

    def _dispatch(self):
        try:
            for event in self._queue:
                self._document._trigger_on_change(event)
        except Exception:
            pass
        finally:
            self._queue = []


class PanelKernel(BokehKernel):

    def __init__(self, key=None, document=None):
        super(BokehKernel, self).__init__()

        self.session = PanelSessionWebsocket(document=document, parent=self, key=key)
        self.stream = self.iopub_socket = WebsocketStream(self.session)

        self.iopub_socket.channel = 'iopub'
        self.session.stream = self.iopub_socket
        self.comm_manager = CommManager(parent=self, kernel=self)
        self.shell = None
        self.log = logging.getLogger('fake')

        comm_msg_types = ['comm_open', 'comm_msg', 'comm_close']
        for msg_type in comm_msg_types:
            self.shell_handlers[msg_type] = getattr(self.comm_manager, msg_type)
