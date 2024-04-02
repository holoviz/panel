from io import BytesIO
from typing import ClassVar, List, Mapping

import param

from ..io.resources import CDN_DIST
from ..layout import Card, Row
from ..pane import Markdown
from ..pane.image import Image
from ..pane.markup import HTML
from ..viewable import Viewable
from ..widgets.indicators import BooleanStatus, LoadingSpinner
from .utils import avatar_lookup, stream_to

DEFAULT_STATUS_AVATARS = {
    "pending": BooleanStatus(value=False, margin=0, color="warning"),
    "running": LoadingSpinner(value=True, margin=0),
    "completed":BooleanStatus(value=True, margin=0, color="success"),
    "failed": BooleanStatus(value=False, margin=0, color="danger")
}


class _ChatStepBase(Card):

    status = param.Selector(
        default="pending", objects=["pending", "running", "completed", "failed"]
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

    _rename: ClassVar[Mapping[str, str | None]] = {
        "default_avatars": None,
        "completed_title": None,
        "status": None,
        **Card._rename,
    }

    def __init__(self, **params):
        self._instance = None
        self._avatar_container = Row(
            align="center", css_classes=["step-avatar-container"]
        )  # placeholder for avatar; weird alignment issue without
        super().__init__(**params)
        self._render_avatar()
        self._title_pane = HTML(
            self.param.title,
            margin=0,
            css_classes=["step-title"],
        )
        self.header = Row(
            self._avatar_container,
            self._title_pane,
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
            css_classes=["step-header"],
        )

    @param.depends("status", watch=True)
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
            "css_classes": ["step-avatar"],
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

    def stream_title(self, token, replace=False):
        if replace:
            self.title = token
        else:
            self.title += token
        return self.title

    def __enter__(self):
        self.status = "running"
        if not self.title:
            self.title = "Running..."
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.status = "completed"
        if self.completed_title:
            self.title = self.completed_title
        elif self.objects:
            obj = self.objects[-1]
            for _ in range(100):
                if hasattr(obj, "objects"):
                    obj = obj.objects[-1]
                else:
                    break

            if hasattr(obj, "object"):
                obj = obj.object

            if isinstance(obj, str):
                self.title = obj
        else:
            self.title = "Completed!"
        self.collapsed = True


class ChatStep(_ChatStepBase):

    completed_title = param.String(
        default="Completed!",
        doc="Title to display when status is completed; if not provided, uses the last object.",
    )

    collapsed = param.Boolean(
        default=True,
        doc="""
        Whether the contents of the Card are collapsed.""",
    )

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_step.css"]

    def stream(self, token, replace=False, message=None):
        if message is None:
            message = Markdown(token, css_classes=["step-message"])
            self.append(message)
        else:
            message = stream_to(message, token, replace=replace)
        return message

    def serialize(self):
        ...


class ChatSteps(_ChatStepBase):

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_steps.css"]

    def step(self, chat_step: ChatStep | None = None, **kwargs):
        if chat_step is None:
            chat_step = ChatStep(margin=0, **kwargs)
        for kwarg in kwargs:
            setattr(chat_step, kwarg, kwargs[kwarg])
        self.append(chat_step)
        return chat_step

    def serialize(self):
        ...
