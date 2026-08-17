# panel.io.ipywidget module

class panel.io.ipywidget.MessageSentBuffers
Bases: `TypedDict`

class panel.io.ipywidget.MessageSentEventPatched(document: Document, msg_type: str, msg_data: Any \| bytes, setter: Setter \| None = None, callback_invoker: Invoker \| None = None)
Bases: `MessageSentEvent`

Patches MessageSentEvent with fix that ensures MessageSent event does
not define msg_data (which is an assumption in BokehJS
Document.apply_json_patch.)

Methods

|              |     |
|--------------|-----|
| **generate** |     |

class panel.io.ipywidget.PanelKernel(\*args: t.Any, **kwargs: t.Any)
Bases: `Kernel`

Attributes:
**shell_stream**

Methods

|                     |     |
|---------------------|-----|
| **register_widget** |     |

class panel.io.ipywidget.PanelSessionWebsocket(\*args: t.Any, **kwargs: t.Any)
Bases: `SessionWebsocket`

Methods

|  |  |
|----|----|
| [send](#panel.io.ipywidget.PanelSessionWebsocket.send)(stream, msg_type\[, content, parent, ...\]) | Build and send a message via stream or socket. |

send(stream, msg_type, content=None, parent=None, ident=None, buffers=None, track=False, header=None, metadata=None)
Build and send a message via stream or socket.

The message format used by this function internally is as follows:

\[ident1,ident2,…,DELIM,HMAC,p_header,p_parent,p_content,
buffer1,buffer2,…\]

The serialize/deserialize methods convert the nested message dict into
this format.

Parameters:
stream : zmq.Socket or ZMQStream
The socket-like object used to send the data.

msg_or_type : str or Message/dict
Normally, msg_or_type will be a msg_type unless a message is being sent
more than once. If a header is supplied, this can be set to None and the
msg_type will be pulled from the header.

content : dict or None
The content of the message (ignored if msg_or_type is a message).

header : dict or None
The header dict for the message (ignored if msg_to_type is a message).

parent : Message or dict or None
The parent or parent header describing the parent of this message
(ignored if msg_or_type is a message).

ident : bytes or list of bytes
The zmq.IDENTITY routing path.

metadata : dict or None
The metadata describing the message

buffers : list or None
The already-serialized buffers to be appended to the message.

track : bool
Whether to track. Only for use with Sockets, because ZMQStream objects
cannot track messages.

Returns:
msg : dict
The constructed message.

class panel.io.ipywidget.TempComm(target_name: str = 'comm', data: Dict\[str, Any\] \| None = None, metadata: Dict\[str, Any\] \| None = None, buffers: List\[bytes\] \| None = None, comm_id: str \| None = None, primary: bool = True, target_module: str \| None = None, topic: bytes \| None = None, \_open_data: Dict\[str, Any\] \| None = None, \_close_data: Dict\[str, Any\] \| None = None, **kwargs: Any)
Bases: `BaseComm`

Methods

|                 |     |
|-----------------|-----|
| **publish_msg** |     |

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
