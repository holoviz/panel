from contextlib import contextmanager
from io import BytesIO
from typing import ClassVar, List, Mapping

import param

from ..io.resources import CDN_DIST
from ..layout import Card, Row
from ..pane import Markdown
from ..pane.image import Image
from ..pane.markup import HTML
from ..viewable import Viewable
from .feed import ChatFeed
from .interface import ChatInterface
from .utils import avatar_lookup, stream_to

DEFAULT_STATUS_AVATARS = {
    "pending": "⏳",
    "completed": "✅",
    "failed": "❌",
}


class ChatSteps(Card):

    status = param.Selector(
        default="pending", objects=["pending", "completed", "failed"]
    )

    pending_title = param.String(
        default="Loading...",
        doc="Title to display when status is pending",
    )

    completed_title = param.String(
        doc="Title to display when status is completed; if not provided, uses the last object.",
    )

    default_avatars = param.Dict(
        default=DEFAULT_STATUS_AVATARS,
        doc="Mapping from status to default status avatar",
    )

    margin = param.Parameter(
        default=(5, 5, 5, 10),
        doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""",
    )

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_steps.css"]

    _rename: ClassVar[Mapping[str, str | None]] = {
        "default_avatars": None,
        "pending_title": None,
        "completed_title": None,
        "status": None,
        **Card._rename,
    }

    def __init__(self, **params):
        self._avatar_container = Row(
            align="center"
        )  # placeholder for avatar; weird alignment issue without
        super().__init__(**params)

        self.header = Row(
            self._avatar_container,
            HTML(
                self.param.title,
                margin=0,
                css_classes=["steps-title"],
            ),
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
        )

    @param.depends("status", watch=True, on_init=True)
    def _render_avatar(self):
        """
        Render the avatar pane as some HTML text or Image pane.
        """
        avatar = avatar_lookup(
            self.status,
            None,
            self.default_avatars,
            DEFAULT_STATUS_AVATARS,
        )

        if not avatar and self.user:
            avatar = self.user[0]

        avatar_params = {
            "css_classes": ["status-avatar"],
            "margin": (0, 5, 0, 0),
            "width": 15,
            "height": 15,
        }
        if isinstance(avatar, Viewable):
            avatar_pane = avatar
            avatar_params["css_classes"] = (
                avatar_params.get("css_classes", []) + avatar_pane.css_classes
            )
            avatar_pane.param.update(avatar_params)
        elif not isinstance(avatar, (BytesIO, bytes)) and len(avatar) == 1:
            # single character
            avatar_pane = HTML(avatar, **avatar_params)
        else:
            try:
                avatar_pane = Image(avatar, **avatar_params)
            except ValueError:
                # likely an emoji
                avatar_pane = HTML(avatar, **avatar_params)
        self._avatar_container.objects = [avatar_pane]

    @contextmanager
    def pending(self, instance: ChatFeed | ChatInterface):
        instance.stream(self)
        self.title = self.pending_title
        yield self
        self.status = "completed"
        self.title = (
            self.completed_title if self.completed_title or not self.objects
            else self.objects[-1].object
        )

    def stream_title(self, token, replace=False):
        if replace:
            self.title = token
        else:
            self.title += token
        return self.title

    def stream(self, token, replace=False, message=None):
        if message is None:
            message = Markdown(token, margin=(0, 0), css_classes=["steps-message"])
            self.append(message)
        else:
            message = stream_to(message, token, replace=replace)
        return message
