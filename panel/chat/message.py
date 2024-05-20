"""
The message module provides a low-level API for rendering chat messages.
"""

from __future__ import annotations

import datetime

from contextlib import ExitStack
from dataclasses import dataclass
from functools import partial
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Optional, Union,
)
from zoneinfo import ZoneInfo

import param

from ..io.resources import CDN_DIST, get_dist_path
from ..io.state import state
from ..layout import Column, Row
from ..pane.base import PaneBase, ReplacementPane, panel as _panel
from ..pane.image import (
    PDF, FileBase, Image, ImageBase,
)
from ..pane.markup import (
    HTML, DataFrame, HTMLBasePane, Markdown,
)
from ..pane.media import Audio, Video
from ..param import ParamFunction
from ..viewable import Viewable
from ..widgets.base import Widget
from .icon import ChatCopyIcon, ChatReactionIcons
from .utils import (
    avatar_lookup, build_avatar_pane, serialize_recursively, stream_to,
)

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

Avatar = Union[str, BytesIO, bytes, ImageBase]
AvatarDict = dict[str, Avatar]

USER_LOGO = "🧑"
ASSISTANT_LOGO = "🤖"
SYSTEM_LOGO = "⚙️"
ERROR_LOGO = "❌"
HELP_LOGO = "❓"
GPT_3_LOGO = "{dist_path}assets/logo/gpt-3.svg"
GPT_4_LOGO = "{dist_path}assets/logo/gpt-4.svg"
WOLFRAM_LOGO = "{dist_path}assets/logo/wolfram.svg"
LUMEN_LOGO = "{dist_path}assets/logo/lumen.svg"
HOLOVIEWS_LOGO = "{dist_path}assets/logo/holoviews.svg"
HVPLOT_LOGO = "{dist_path}assets/logo/hvplot.svg"
PANEL_LOGO = "{dist_path}images/icon-vector.svg"

DEFAULT_AVATARS = {
    # User
    "client": USER_LOGO,
    "customer": USER_LOGO,
    "employee": USER_LOGO,
    "human": USER_LOGO,
    "person": USER_LOGO,
    "user": USER_LOGO,
    # Assistant
    "agent": ASSISTANT_LOGO,
    "ai": ASSISTANT_LOGO,
    "assistant": ASSISTANT_LOGO,
    "bot": ASSISTANT_LOGO,
    "chatbot": ASSISTANT_LOGO,
    "machine": ASSISTANT_LOGO,
    "robot": ASSISTANT_LOGO,
    # System
    "system": SYSTEM_LOGO,
    "exception": ERROR_LOGO,
    "error": ERROR_LOGO,
    "help": HELP_LOGO,
    # Human
    "adult": "🧑",
    "baby": "👶",
    "boy": "👦",
    "child": "🧒",
    "girl": "👧",
    "man": "👨",
    "woman": "👩",
    # Machine
    "chatgpt": GPT_3_LOGO,
    "gpt3": GPT_3_LOGO,
    "gpt4": GPT_4_LOGO,
    "dalle": GPT_4_LOGO,
    "openai": GPT_4_LOGO,
    "huggingface": "🤗",
    "calculator": "🧮",
    "langchain": "🦜",
    "retriever": "📄",
    "tool": "🛠️",
    "translator": "🌐",
    "wolfram": WOLFRAM_LOGO,
    "wolfram alpha": WOLFRAM_LOGO,
    # Llama
    "llama": "🦙",
    "llama2": "🐪",
    # Plotting
    "plot": "📊",
    "lumen": LUMEN_LOGO,
    "holoviews": HOLOVIEWS_LOGO,
    "hvplot": HVPLOT_LOGO,
    "panel": PANEL_LOGO,
}


@dataclass
class _FileInputMessage:
    """
    A dataclass to hold the contents of a file input message.

    Parameters
    ----------
    contents : bytes
        The contents of the file.
    file_name : str
        The name of the file.
    mime_type : str
        The mime type of the file.
    """

    contents: bytes
    file_name: str
    mime_type: str


class ChatMessage(PaneBase):
    """
    A widget for displaying chat messages with support for various content types.

    This widget provides a structured view of chat messages, including features like:
    - Displaying user avatars, which can be text, emoji, or images.
    - Showing the user's name.
    - Displaying the message timestamp in a customizable format.
    - Associating reactions with messages and mapping them to icons.
    - Rendering various content types including text, images, audio, video, and more.

    Reference: https://panel.holoviz.org/reference/chat/ChatMessage.html

    :Example:

    >>> ChatMessage(object="Hello world!", user="New User", avatar="😊")
    """

    avatar = param.ClassSelector(default="", class_=(str, BytesIO, bytes, ImageBase), doc="""
        The avatar to use for the user. Can be a single character
        text, an emoji, or anything supported by `pn.pane.Image`. If
        not set, checks if the user is available in the
        default_avatars mapping; else uses the first character of the
        name.""")

    avatar_lookup = param.Callable(default=None, doc="""
        A function that can lookup an `avatar` from a user name. The
        function signature should be `(user: str) -> Avatar`. If this
        is set, `default_avatars` is disregarded.""")

    css_classes = param.List(default=["chat-message"],doc="""
        The CSS classes to apply to the widget.""")

    default_avatars = param.Dict(default=DEFAULT_AVATARS, doc="""
        A default mapping of user names to their corresponding avatars
        to use when the user is specified but the avatar is. You can
        modify, but not replace the dictionary.""")

    footer_objects = param.List(doc="""
        A list of objects to display in the column of the footer of the message.""")

    header_objects = param.List(doc="""
        A list of objects to display in the row of the header of the message.""")

    max_width = param.Integer(default=1200, bounds=(0, None))

    object = param.Parameter(allow_refs=False, doc="""
        The message contents. Can be any Python object that panel can display.""")

    reactions = param.List(doc="""
        Reactions to associate with the message.""")

    reaction_icons = param.ClassSelector(class_=ChatReactionIcons, doc="""
        A mapping of reactions to their reaction icons; if not provided
        defaults to `{"favorite": "heart"}`.""", allow_refs=False)

    timestamp = param.Date(doc="""
        Timestamp of the message. Defaults to the creation time.""")

    timestamp_format = param.String(default="%H:%M", doc="The timestamp format.")

    timestamp_tz = param.String(default=None, doc="""
        The timezone to used for the creation timestamp; only applicable
        if timestamp is not set. If None, tries to use pn.state.browser_info.timezone,
        else, the default tz of datetime.datetime.now(); see `zoneinfo.available_timezones()`
        for a list of valid timezones.
    """)

    show_avatar = param.Boolean(default=True, doc="""
         Whether to display the avatar of the user.""")

    show_user = param.Boolean(default=True, doc="""
        Whether to display the name of the user.""")

    show_timestamp = param.Boolean(default=True, doc="""
        Whether to display the timestamp of the message.""")

    show_reaction_icons = param.Boolean(default=True, doc="""
        Whether to display the reaction icons.""")

    show_copy_icon = param.Boolean(default=True, doc="""
        Whether to display the copy icon.""")

    show_activity_dot = param.Boolean(default=False, doc="""
        Whether to show the activity dot.""")

    renderers = param.HookList(doc="""
        A callable or list of callables that accept the object and return a
        Panel object to render the object. If a list is provided, will
        attempt to use the first renderer that does not raise an
        exception. If None, will attempt to infer the renderer
        from the object."""
    )

    user = param.Parameter(default="User", doc="""
        Name of the user who sent the message.""")

    _stylesheets: ClassVar[list[str]] = [f"{CDN_DIST}css/chat_message.css"]

    # Declares whether Pane supports updates to the Bokeh model
    _updates: ClassVar[bool] = True

    def __init__(self, object=None, **params):
        self._exit_stack = ExitStack()
        self.chat_copy_icon = ChatCopyIcon(
            visible=False, width=15, height=15, css_classes=["copy-icon"]
        )
        if params.get("timestamp") is None:
            tz = params.get("timestamp_tz")
            if tz is not None:
                tz = ZoneInfo(tz)
            elif state.browser_info and state.browser_info.timezone:
                tz = ZoneInfo(state.browser_info.timezone)
            params["timestamp"] = datetime.datetime.now(tz=tz)

        reaction_icons = params.get("reaction_icons", {"favorite": "heart"})
        if isinstance(reaction_icons, dict):
            params["reaction_icons"] = ChatReactionIcons(options=reaction_icons)
        self._internal = True
        super().__init__(object=object, **params)
        self.chat_copy_icon = ChatCopyIcon(
            visible=False, width=15, height=15, css_classes=["copy-icon"],
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
        )
        if not self.avatar:
            self._update_avatar()
        self._build_layout()

    def _build_layout(self):
        self._activity_dot = HTML(
            "●",
            css_classes=["activity-dot"],
            visible=self.param.show_activity_dot,
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
        )
        self._left_col = left_col = Column(
            self._render_avatar(),
            max_width=60,
            height=100,
            css_classes=["left"],
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
            visible=self.param.show_avatar,
            sizing_mode=None,
        )
        self.param.watch(self._update_avatar_pane, "avatar")

        self._object_panel = self._create_panel(self.object)
        self._update_chat_copy_icon()
        self._center_row = Row(
            self._object_panel,
            self._render_reaction_icons(),
            css_classes=["center"],
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
            sizing_mode=None
        )
        self.param.watch(self._update_object_pane, "object")
        self.param.watch(self._update_reaction_icons, "reaction_icons")

        self._user_html = HTML(
            self.param.user, height=20, css_classes=["name"],
            visible=self.param.show_user, stylesheets=self._stylesheets,
        )

        header_objects = (
            [self._user_html] +
            self.param.header_objects.rx() +
            [self.chat_copy_icon, self._activity_dot]
        )
        header_row = Row(
            objects=header_objects,
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
            sizing_mode="stretch_width",
            css_classes=["header"]
        )

        self._timestamp_html = HTML(
            self.param.timestamp.rx().strftime(self.param.timestamp_format),
            css_classes=["timestamp"],
            visible=self.param.show_timestamp
        )

        footer_col = Column(
            objects=self.param.footer_objects.rx() + [self._timestamp_html],
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
            sizing_mode="stretch_width",
            css_classes=["footer"],
        )

        self._right_col = right_col = Column(
            header_row,
            self._center_row,
            footer_col,
            css_classes=["right"],
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
            sizing_mode=None
        )
        viewable_params = {
            p: self.param[p] for p in self.param if p in Viewable.param
            if p in Viewable.param and p != 'name'
        }
        viewable_params['stylesheets'] = self._stylesheets + self.param.stylesheets.rx()
        self._composite = Row(left_col, right_col, **viewable_params)

    def __str__(self) -> str:
        """
        Serialize the message object to a string.
        """
        return self.serialize()

    @property
    def _synced_params(self) -> list[str]:
        return []

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = self._composite._get_model(doc, root, parent, comm)
        if not comm:
            # If not in a notebook environment we potentially need to
            # replace path to avatar with server URL
            avatar = model.children[0].children[0]
            avatar.text = avatar.text.replace(CDN_DIST, get_dist_path())
        ref = (root or model).ref['id']
        self._models[ref] = (model, parent)
        return model

    def _select_renderer(
        self,
        contents: Any,
        mime_type: str,
    ):
        """
        Determine the renderer to use based on the mime type.
        """
        renderer = _panel
        if mime_type == "application/pdf":
            contents = self._exit_stack.enter_context(BytesIO(contents))
            renderer = partial(PDF, embed=True)
        elif mime_type.startswith("audio/"):
            file = self._exit_stack.enter_context(
                NamedTemporaryFile(suffix=".mp3", delete=False)
            )
            file.write(contents)
            file.seek(0)
            contents = file.name
            renderer = Audio
        elif mime_type.startswith("video/"):
            contents = self._exit_stack.enter_context(BytesIO(contents))
            renderer = Video
        elif mime_type.startswith("image/"):
            contents = self._exit_stack.enter_context(BytesIO(contents))
            renderer = Image
        elif mime_type.endswith("/csv"):
            import pandas as pd

            with BytesIO(contents) as buf:
                contents = pd.read_csv(buf)
            renderer = DataFrame
        elif mime_type.startswith("text"):
            if isinstance(contents, bytes):
                contents = contents.decode("utf-8")
        return contents, renderer

    def _include_stylesheets_inplace(self, obj):
        if hasattr(obj, "objects"):
            obj.objects[:] = [
                self._include_stylesheets_inplace(o) for o in obj.objects
            ]
        else:
            obj = _panel(obj)
        obj.stylesheets = [
            stylesheet for stylesheet in self._stylesheets + self.stylesheets
            if stylesheet not in obj.stylesheets
        ] + obj.stylesheets
        return obj

    def _include_message_css_class_inplace(self, obj):
        if hasattr(obj, "objects"):
            obj.objects[:] = [
                self._include_message_css_class_inplace(o)
                for o in obj.objects
            ]
        else:
            obj = _panel(obj)
        is_markup = isinstance(obj, HTMLBasePane) and not isinstance(obj, FileBase)
        if obj.css_classes or not is_markup:
            return obj
        if len(str(obj.object)) > 0:  # only show a background if there is content
            obj.css_classes = [*(css for css in obj.css_classes if css != "message"), "message"]
        obj.sizing_mode = None
        return obj

    def _set_params(self, obj, **params):
        """
        Set the sizing mode and height of the object.
        """
        self._include_stylesheets_inplace(obj)
        is_markup = isinstance(obj, HTMLBasePane) and not isinstance(obj, FileBase)
        if is_markup:
            self._include_message_css_class_inplace(obj)
        else:
            if obj.sizing_mode is None and not obj.width:
                params['sizing_mode'] = "stretch_width"

            if obj.height is None and not isinstance(obj, ParamFunction):
                params['height'] = 500
        obj.param.update(params)

    @staticmethod
    def _is_widget_renderer(renderer):
        return isinstance(renderer, type) and issubclass(renderer, Widget)

    def _create_panel(self, value, old=None):
        """
        Create a panel object from the value.
        """
        if isinstance(value, Viewable):
            self._internal = False
            self._include_stylesheets_inplace(value)
            self._include_message_css_class_inplace(value)
            return value

        renderer = None
        if isinstance(value, _FileInputMessage):
            contents = value.contents
            mime_type = value.mime_type
            value, renderer = self._select_renderer(contents, mime_type)
        else:
            try:
                import magic

                mime_type = magic.from_buffer(value, mime=True)
                value, renderer = self._select_renderer(value, mime_type)
            except Exception:
                pass

        renderers = self.renderers.copy() or []
        if renderer is not None:
            renderers.append(renderer)
        for renderer in renderers:
            try:
                if self._is_widget_renderer(renderer):
                    object_panel = renderer(value=value)
                else:
                    object_panel = renderer(value)
                if isinstance(object_panel, Viewable):
                    break
            except Exception:
                pass
        else:
            if isinstance(old, Markdown) and isinstance(value, str):
                self._set_params(old, object=value)
                return old
            object_panel = _panel(value)

        self._set_params(object_panel)
        if type(old) is type(object_panel) and self._internal:
            ReplacementPane._recursive_update(old, object_panel)
            return object_panel

        self._internal = True
        return object_panel

    def _render_avatar(self) -> HTML | Image:
        """
        Render the avatar pane as some HTML text or Image pane.
        """
        avatar = self.avatar
        if not avatar and self.user:
            avatar = self.user[0]

        avatar_pane = build_avatar_pane(
            avatar, css_classes=["avatar"], height=35, width=35
        )
        return avatar_pane

    def _update_avatar_pane(self, event=None):
        new_avatar = self._render_avatar()
        old_type = type(self._left_col[0])
        new_type = type(new_avatar)
        if isinstance(event.old, (HTML, ImageBase)) or new_type is not old_type:
            self._left_col[:] = [new_avatar]
        else:
            params = new_avatar.param.values()
            del params['name']
            self._left_col[0].param.update(**params)

    def _render_reaction_icons(self):
        reaction_icons = self.reaction_icons
        reaction_icons.param.update(
            width=15,
            height=15,
            value=self.param.reactions,
            stylesheets=self._stylesheets + self.param.stylesheets.rx(),
            visible=self.param.show_reaction_icons
        )
        reaction_icons.link(self, value="reactions", bidirectional=True)
        return reaction_icons

    def _update_reaction_icons(self, _):
        self._center_row[1] = self._render_reaction_icons()

    def _update(self, ref, old_models):
        """
        Internals will be updated inplace.
        """

    def _update_object_pane(self, event=None):
        old = self._object_panel
        self._object_panel = new = self._create_panel(self.object, old=old)
        if old is not new:
            self._center_row[0] = new
        self._update_chat_copy_icon()

    @param.depends("avatar_lookup", "user", watch=True)
    def _update_avatar(self):
        """
        Update the avatar based on the user name.

        We do not use on_init here because if avatar is set,
        we don't want to override the provided avatar.

        However, if the user is updated, we want to update the avatar.
        """
        if self.avatar_lookup:
            self.avatar = self.avatar_lookup(self.user)
        else:
            self.avatar = avatar_lookup(
                self.user,
                self.avatar,
                self.default_avatars,
                DEFAULT_AVATARS,
            )

    def _update_chat_copy_icon(self):
        object_panel = self._object_panel
        if isinstance(object_panel, HTMLBasePane):
            object_panel = object_panel.object
        elif isinstance(object_panel, Widget):
            object_panel = object_panel.value
        if isinstance(object_panel, str) and self.show_copy_icon:
            self.chat_copy_icon.value = object_panel
            self.chat_copy_icon.visible = True
        else:
            self.chat_copy_icon.value = ""
            self.chat_copy_icon.visible = False

    def _cleanup(self, root=None) -> None:
        """
        Cleanup the exit stack.
        """
        self._composite._cleanup(root)
        return super()._cleanup(root)

    def stream(self, token: str, replace: bool = False):
        """
        Updates the message with the new token traversing the object to
        allow updating nested objects. When traversing a nested Panel
        the last object that supports rendering strings is updated, e.g.
        in a layout of `Column(Markdown(...), Image(...))` the Markdown
        pane is updated.

        Arguments
        ---------
        token: str
          The token to stream to the text pane.
        replace: bool (default=False)
            Whether to replace the existing text.
        """
        stream_to(obj=self.object, token=token, replace=replace)

    def update(
        self,
        value: dict | ChatMessage | Any,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
    ):
        """
        Updates the message with a new value, user and avatar.

        Arguments
        ---------
        value : ChatMessage | dict | Any
            The message contents to send.
        user : str | None
            The user to send as; overrides the message message's user if provided.
        avatar : str | bytes | BytesIO | None
            The avatar to use; overrides the message message's avatar if provided.
        """
        updates = {}
        if isinstance(value, dict):
            updates.update(value)
            if user:
                updates["user"] = user
            if avatar:
                updates["avatar"] = avatar
        elif isinstance(value, ChatMessage):
            if user is not None or avatar is not None:
                raise ValueError(
                    "Cannot set user or avatar when explicitly sending "
                    "a ChatMessage. Set them directly on the ChatMessage."
                )
            updates = value.param.values()
        else:
            updates["object"] = value
        self.param.update(**updates)

    def select(
        self, selector: Optional[type | Callable[[Viewable], bool]] = None
    ) -> list[Viewable]:
        return super().select(selector) + self._composite.select(selector)

    def serialize(
        self,
        prefix_with_viewable_label: bool = True,
        prefix_with_container_label: bool = True
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
            self.object,
            prefix_with_viewable_label=prefix_with_viewable_label,
            prefix_with_container_label=prefix_with_container_label,
        )
