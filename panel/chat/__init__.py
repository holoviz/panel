"""
Panel chat makes creating chat components easy
==============================================================

Check out the widget gallery
https://panel.holoviz.org/reference/index.html#chat for inspiration.

How to use Panel widgets in 3 simple steps
------------------------------------------

1. Define your function

>>> async def repeat_contents(contents, user, instance):
>>>     yield contents

2. Define your widgets and callback.

>>> chat_interface = ChatInterface(callback=repeat_contents)

3. Layout the chat interface in a template

>>> template = pn.template.FastListTemplate(
>>>     title="Panel Chat",
>>>     main=[chat_interface],
>>> )
>>> template.servable()

For more detail see the Reference Gallery guide.
https://panel.holoviz.org/reference/chat/ChatInterface.html
"""

from typing import TYPE_CHECKING

from .feed import ChatFeed  # noqa
from .icon import ChatReactionIcons  # noqa
from .input import ChatAreaInput  # noqa
from .interface import ChatInterface  # noqa
from .message import ChatMessage  # noqa
from .step import ChatStep  # noqa

__all__ = (
    "ChatAreaInput",
    "ChatFeed",
    "ChatInterface",
    "ChatMessage",
    "ChatReactionIcons",
    "ChatStep",
    "langchain",
)

def __getattr__(name):
    """
    Lazily import langchain module when accessed.
    """
    if name == "langchain":
        import importlib
        return importlib.import_module("panel.chat.langchain")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__dir__ = lambda: list(__all__)

if TYPE_CHECKING:
    from . import langchain
