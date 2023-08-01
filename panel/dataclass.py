import datetime

from typing import BinaryIO

import param


class ChatMessage(param.Parameterized):

    value = param.Parameter(doc="""
        The message contents. Can be a string, pane, widget, layout, etc.""")

    user = param.String(default="User", doc="""
        Name of the user who sent the message.""")

    avatar = param.ClassSelector(class_=(str, BinaryIO), doc="""
        The avatar to use for the user. Can be a single character text, an emoji,
        a URL, a file path, or a binary IO. If not set, uses the first letter
        of the name.""")

    reactions = param.List(doc="""
        Reactions to associate with the message.""")

    timestamp = param.Date(
        default=datetime.datetime.utcnow(), doc="""
        Timestamp of the message. Defaults to the instantiation time.""")

    def json(self) -> dict:
        """Return the ChatMessage as JSON."""
        return {
            "value": self.value,
            "user": self.user,
            "avatar": self.avatar,
            "reactions": self.reactions,
            "timestamp": self.timestamp.isoformat(),
        }

    def __init__(self, **params):
        super().__init__(**params)
        if not self.avatar and self.user:
            self.avatar = self.user[0]
        else:
            self.avatar = "?"
