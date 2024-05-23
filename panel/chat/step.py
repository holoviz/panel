from __future__ import annotations

from typing import ClassVar, Mapping

import param

from ..io.resources import CDN_DIST
from ..layout import Card, Row
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
    "success": BooleanStatus(value=True, margin=0, color="success"),
    "failed": BooleanStatus(value=True, margin=0, color="danger"),
}


class ChatStep(Card):
    collapsed = param.Boolean(
        default=False,
        doc="Whether the contents of the Card are collapsed.")

    collapsed_on_success = param.Boolean(
        default=True,
        doc="Whether to collapse the card on completion.")

    success_title = param.String(default=None, doc="""
        Title to display when status is success.""")

    default_avatars = param.Dict(
        default=DEFAULT_STATUS_AVATARS,
        doc="Mapping from status to default status avatar.")

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
        default="pending", objects=["pending", "running", "success", "failed"])

    title = param.String(default="", constant=True, doc="""
        The title of the chat step. Will redirect to default_title on init.
        After, it cannot be set directly; instead use the *_title params.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        "collapsed_on_success": None,
        "default_avatars": None,
        "default_title": None,
        "pending_title": None,
        "running_title": None,
        "success_title": None,
        "failed_title": None,
        "status": None,
        **Card._rename,
    }

    _stylesheets: ClassVar[list[str]] = [f"{CDN_DIST}css/chat_step.css"]

    def __init__(self, *objects, **params):
        self._instance = None
        self._avatar_placeholder = Placeholder(css_classes=["step-avatar-container"])

        if params.get("title"):
            if params.get("default_title"):
                raise ValueError("Cannot set both title and default_title.")
            params["default_title"] = params["title"]

        super().__init__(*objects, **params)
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
        self.status = "success"

    @param.depends("status", "default_avatars", watch=True)
    def _render_avatar(self):
        """
        Render the avatar pane as some HTML text or Image pane.
        """
        extra_keys = set(self.default_avatars.keys()) - set(DEFAULT_STATUS_AVATARS.keys())
        if extra_keys:
            raise ValueError(
                f"Invalid status avatars. Must be one of 'pending', 'running', 'success', 'failed'; "
                f"got {extra_keys}."
            )

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
        "success_title",
        "failed_title",
        watch=True,
        on_init=True,
    )
    def _update_title_on_status(self):
        if self.status == "pending" and self.pending_title is not None:
            title = self.pending_title
        elif self.status == "running" and self.running_title is not None:
            title = self.running_title
        elif self.status == "success" and self.success_title is not None:
            title = self.success_title
        elif self.status == "failed" and self.failed_title is not None:
            title = self.failed_title
        else:
            title = self.default_title
        with param.edit_constant(self):
            self.title = title

    @param.depends("status", "collapsed_on_success", watch=True)
    def _update_collapsed(self):
        if self.status == "success" and self.collapsed_on_success:
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
