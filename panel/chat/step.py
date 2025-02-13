from __future__ import annotations

import traceback

from collections.abc import Mapping
from typing import ClassVar, Literal

import param

from ..io.resources import CDN_DIST
from ..layout import Card, Row
from ..pane.image import ImageBase
from ..pane.markup import HTML, HTMLBasePane, Markdown
from ..pane.placeholder import Placeholder
from ..util import edit_readonly
from ..widgets.indicators import BooleanStatus
from .utils import (
    avatar_lookup, build_avatar_pane, serialize_recursively, stream_to,
)

DEFAULT_STATUS_BADGES = {
    "pending": BooleanStatus(value=False, margin=0, color="primary"),
    "running": BooleanStatus(value=True, margin=0, color="warning"),
    "success": BooleanStatus(value=True, margin=0, color="success"),
    "failed": BooleanStatus(value=True, margin=0, color="danger"),
}


class ChatStep(Card):
    """
    A component that makes it easy to provide status updates and the
    ability to stream updates to both the output(s) and the title.

    Reference: https://panel.holoviz.org/reference/chat/ChatStep.html

    :Example:

    >>> ChatStep("Hello world!", title="Running calculation...', status="running")
    """

    collapsed = param.Boolean(default=False, doc="""
        Whether the contents of the Card are collapsed.""")

    collapsed_on_success = param.Boolean(default=True, doc="""
        Whether to collapse the card on completion.""")

    context_exception = param.Selector(
        default="raise", objects=["raise", "summary", "verbose", "ignore"], doc="""
        How to handle exceptions raised upon exiting the context manager.
        If "raise", the exception will be raised.
        If "summary", a summary will be sent to the chat step.
        If "verbose", the full traceback will be sent to the chat step.
        If "ignore", the exception will be ignored.
        """)

    success_title = param.String(default=None, doc="""
        Title to display when status is success.""")

    default_badges = param.Dict(default=DEFAULT_STATUS_BADGES, doc="""
        Mapping from status to default status badge; keys must be one of
        'pending', 'running', 'success', 'failed'.
        """)

    default_title = param.String(default="", doc="""
        The default title to display if the other title params are unset.""")

    failed_title = param.String(default=None, doc="""
        Title to display when status is failed.""")

    header = param.Parameter(doc="""
        A Panel component to display in the header bar of the Card.
        Will override the given title if defined.""", readonly=True)

    margin = param.Parameter(default=(5, 5, 5, 10), doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    pending_title = param.String(default=None, doc="""
        Title to display when status is pending.""")

    running_title = param.String(default=None, doc="""
        Title to display when status is running.""")

    status = param.Selector(default="pending", objects=[
        "pending", "running", "success", "failed"])

    title = param.String(default="", constant=True, doc="""
        The title of the chat step. Will redirect to default_title on init.
        After, it cannot be set directly; instead use the *_title params.""")

    _rename: ClassVar[Mapping[str, str | None]] = {
        "collapsed_on_success": None,
        "context_exception": None,
        "default_badges": None,
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
        self._failed_title = ""  # for cases when contextmanager is invoked twice
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

        with edit_readonly(self):
            self.header = Row(
                self._avatar_placeholder,
                self._title_pane,
                stylesheets=self._stylesheets + self.param.stylesheets.rx(),
                css_classes=["step-header"],
                margin=(5, 0),
                width=self.width,
                max_width=self.max_width,
                min_width=self.min_width,
                sizing_mode=self.sizing_mode,
            )

    def __enter__(self):
        self.status = "running"
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None and self.context_exception != "ignore":
            if self.failed_title is None:
                # convert to str to wrap repr in apostrophes
                self._failed_title = f"Error: {exc_type.__name__!r}"
                if self.context_exception == "summary" or self.context_exception == "raise":
                    exc_msg = f"{exc_value}"
                elif self.context_exception == "verbose":
                    exc_msg = "```python\n" + "\n".join(traceback.format_exception(exc_type, exc_value, tb)) + "\n```"
                else:
                    exc_msg = None

                if len(self.objects) == 1:
                    exc_msg = f"\n{exc_msg}"
                self.stream(exc_msg)
            self.status = "failed"
            if self.context_exception == "raise":
                return False
        else:
            self.status = "success"
        return True  # suppress exception if any

    @param.depends("status", "default_badges", watch=True)
    def _render_avatar(self):
        """
        Render the avatar pane as some HTML text or Image pane.
        """
        extra_keys = set(self.default_badges.keys()) - set(DEFAULT_STATUS_BADGES.keys())
        if extra_keys:
            raise ValueError(
                f"Invalid status avatars. Must be one of 'pending', 'running', 'success', 'failed'; "
                f"got {extra_keys}."
            )

        avatar = avatar_lookup(
            self.status,
            None,
            self.default_badges,
            DEFAULT_STATUS_BADGES,
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
        elif self.status == "failed" and self._failed_title:
            title = self._failed_title
        else:
            title = self.default_title

        with param.edit_constant(self):
            self.title = title

    @param.depends("status", "collapsed_on_success", watch=True)
    def _update_collapsed(self):
        if self.status == "success" and self.collapsed_on_success:
            self.collapsed = True

    def stream_title(
        self,
        token: str,
        status: Literal["pending", "running", "success", "failed", "default"] = "running",
        replace: bool = False
    ):
        """
        Stream a token to the title header.

        Parameters
        ----------
        token : str
            The token to stream.
        status : str
            The status title to stream to, one of 'pending', 'running', 'success', 'failed', or "default".
        replace : bool
            Whether to replace the existing text.
        """
        if replace:
            setattr(self, f"{status}_title", token)
        else:
            original = getattr(self, f"{status}_title") or ""
            setattr(self, f"{status}_title", original + token)

    def stream(self, token: str | None, replace: bool = False):
        """
        Stream a token to the last available string-like object.

        Parameters
        ----------
        token : str
            The token to stream.
        replace : bool
            Whether to replace the existing text.

        Returns
        -------
        Viewable
            The updated message pane.
        """
        if token is None:
            token = ""

        if (
            len(self.objects) == 0 or not isinstance(self.objects[-1], HTMLBasePane) or isinstance(self.objects[-1], ImageBase)
        ):
            message = Markdown(token, css_classes=["step-message"])
            self.append(message)
        else:
            stream_to(self.objects[-1], token, replace=replace)

        if self._instance is not None:
            self._instance._chat_log.scroll_to_latest(self._instance.auto_scroll_limit)

    def serialize(
        self,
        prefix_with_viewable_label: bool = True,
        prefix_with_container_label: bool = True,
    ) -> str:
        """
        Format the object to a string.

        Parameters
        ----------
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
