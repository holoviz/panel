from __future__ import annotations

from typing import ClassVar, Mapping

import param

from ..io.resources import CDN_DIST
from ..layout import Card, Column, Row
from ..pane.image import ImageBase
from ..pane.markup import HTML, HTMLBasePane, Markdown
from ..pane.placeholder import Placeholder
from ..widgets.indicators import BooleanStatus
from .utils import (
    avatar_lookup, build_avatar_pane, serialize_recursively, stream_to,
)

DEFAULT_STATUS_AVATARS = {
    "pending": BooleanStatus(value=False, margin=0, color="primary"),
    "running": BooleanStatus(value=True, margin=0, color="warning"),
    "completed": BooleanStatus(value=True, margin=0, color="success"),
    "failed": BooleanStatus(value=True, margin=0, color="danger"),
}


class ChatStep(Card):
    collapsed = param.Boolean(
        default=False,
        doc="Whether the contents of the Card are collapsed.")

    collapse_on_completed = param.Boolean(
        default=True,
        doc="Whether to collapse the card on completion.")

    completed_title = param.String(default=None, doc="""
        Title to display when status is completed; if not provided and collapse_on_completed
        uses the last object's string.""")

    default_avatars = param.Dict(
        default=DEFAULT_STATUS_AVATARS,
        doc="Mapping from status to default status avatar")

    default_title = param.String(
        default="",
        doc="The default title to display if the other title params are unset.")

    failed_title = param.String(
        default=None,
        doc="Title to display when status is failed.")

    margin = param.Parameter(
        default=(5, 5, 5, 10), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    pending_title = param.String(
        default=None,
        doc="Title to display when status is pending."
    )

    running_title = param.String(
        default=None,
        doc="Title to display when status is running."
    )

    status = param.Selector(
        default="pending", objects=["pending", "running", "completed", "failed"])

    title = param.String(default="", constant=True, doc="""
        The title of the chat step. Will redirect to default_title on init.
        After, it cannot be set directly; instead use the *_title params.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        "collapse_on_completed": None,
        "default_avatars": None,
        "default_title": None,
        "pending_title": None,
        "running_title": None,
        "completed_title": None,
        "failed_title": None,
        "status": None,
        **Card._rename,
    }

    _stylesheets: ClassVar[list[str]] = [f"{CDN_DIST}css/chat_step.css"]

    def __init__(self, **params):
        self._instance = None
        self._avatar_placeholder = Placeholder(css_classes=["step-avatar-container"])

        if params.get("title"):
            if params.get("default_title"):
                raise ValueError("Cannot set both title and default_title.")
            params["default_title"] = params["title"]

        super().__init__(**params)
        self._render_avatar()
        self._title_pane = HTML(
            self.param.title,
            margin=0,
            css_classes=["step-title"],
        )
        self.header = Row(
            self._avatar_placeholder,
            self._title_pane,
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
            css_classes=["step-header"],
        )
    def __enter__(self):
        self.status = "running"
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.status = "failed"
            if self.failed_title is None:
                # convert to str to wrap repr in apostrophes
                self.failed_title = f"Failed due to: {str(exc_value)!r}"
            raise exc_value
        self.status = "completed"

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
        avatar_pane = build_avatar_pane(avatar, ["step-avatar"])
        self._avatar_placeholder.update(avatar_pane)

    @param.depends(
        "status",
        "default_title",
        "pending_title",
        "running_title",
        "completed_title",
        "failed_title",
        watch=True,
        on_init=True,
    )
    def _update_title_on_status(self):
        with param.edit_constant(self):
            if self.status == "pending" and self.pending_title is not None:
                self.title = self.pending_title

            elif self.status == "running" and self.running_title is not None:
                self.title = self.running_title

            elif self.status == "completed":
                if self.completed_title:
                    self.title = self.completed_title
                elif self.objects and self.collapse_on_completed:
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
                    self.title = self.default_title
            elif self.status == "failed" and self.failed_title is not None:
                self.title = self.failed_title

            else:
                self.title = self.default_title

    @param.depends("status", "collapse_on_completed", watch=True)
    def _update_collapsed(self):
        if self.status == "completed" and self.collapse_on_completed:
            self.collapsed = True

    def stream_title(self, token: str, replace: bool = False):
        """
        Stream a token to the title header.

        Arguments:
        ---------
        token : str
            The token to stream.
        replace : bool
            Whether to replace the existing text.
        """
        if replace:
            self.title = token
        else:
            self.title += token

    def stream(self, token: str, replace: bool = False):
        """
        Stream a token to the last available string-like object.

        Arguments
        ---------
        token : str
            The token to stream.
        replace : bool
            Whether to replace the existing text.

        Returns
        -------
        Viewable
            The updated message pane.
        """
        if (
            len(self.objects) == 0 or not isinstance(self.objects[-1], HTMLBasePane) or isinstance(self.objects[-1], ImageBase)):
            message = Markdown(token, css_classes=["step-message"])
            self.append(message)
        else:
            stream_to(self.objects[-1], token, replace=replace)

    def serialize(
        self,
        prefix_with_viewable_label: bool = True,
        prefix_with_container_label: bool = True,
    ) -> str:
        """
        Format the object to a string.

        Arguments
        ---------
        prefix_with_viewable_label : bool
            Whether to include the name of the Viewable, or type
            of the viewable if no name is specified.
        prefix_with_container_label : bool
            Whether to include the name of the container, or type
            of the container if no name is specified.

        Returns
        -------
        str
            The serialized string.
        """
        return serialize_recursively(
            self,
            prefix_with_viewable_label=prefix_with_viewable_label,
            prefix_with_container_label=prefix_with_container_label,
        )

    def __str__(self):
        return self.serialize()


class ChatSteps(Column):

    _stylesheets = [f"{CDN_DIST}css/chat_steps.css"]

    css_classes = param.List(
        default=["chat-steps"],
        doc="CSS classes to apply to the component.",
    )

    @param.depends("objects", watch=True, on_init=True)
    def _validate_steps(self):
        for step in self.objects:
            if not isinstance(step, ChatStep):
                raise ValueError(f"Expected ChatStep, got {step.__class__.__name__}")

    def append_step(self, objects: str | list[str] | None = None, **step_params):
        """
        Create a new ChatStep and append it to the ChatSteps.

        Arguments
        ---------
        **step_params : dict
            Parameters to pass to the ChatStep constructor.

        Returns
        -------
        ChatStep
            The newly created ChatStep.
        """
        if objects is not None:
            if not isinstance(objects, list):
                objects = [objects]
                step_params["objects"] = objects
        step = ChatStep(**step_params)
        self.append(step)
        return step

    def serialize(
        self,
        prefix_with_viewable_label: bool = True,
        prefix_with_container_label: bool = True,
    ) -> str:
        """
        Format the objects to a string.

        Arguments
        ---------
        prefix_with_viewable_label : bool
            Whether to include the name of the Viewable, or type
            of the viewable if no name is specified.
        prefix_with_container_label : bool
            Whether to include the name of the container, or type
            of the container if no name is specified.

        Returns
        -------
        str
            The serialized string.
        """
        return serialize_recursively(
            self,
            prefix_with_viewable_label=prefix_with_viewable_label,
            prefix_with_container_label=prefix_with_container_label,
        )
