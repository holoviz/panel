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
from . import langchain  # noqa
from .feed import ChatFeed  # noqa
from .icon import ChatReactionIcons  # noqa
from .interface import ChatInterface  # noqa
from .message import ChatMessage  # noqa

__all__ = (
    "ChatFeed",
    "ChatInterface",
    "ChatMessage",
    "ChatReactionIcons",
    "langchain",
)
