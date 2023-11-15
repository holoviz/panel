"""
The message module provides a low-level API for rendering chat messages.
"""

from __future__ import annotations

import datetime
import re

from contextlib import ExitStack
from dataclasses import dataclass
from functools import partial
from io import BytesIO
from tempfile import NamedTemporaryFile
from textwrap import indent
from typing import (
    TYPE_CHECKING, Any, ClassVar, Dict, Iterable, List, Union,
)

import param

from ..io.resources import CDN_DIST
from ..layout import Column, Row
from ..pane.base import PaneBase, panel as _panel
from ..pane.image import (
    PDF, FileBase, Image, ImageBase,
)
from ..pane.markup import HTML, DataFrame, HTMLBasePane
from ..pane.media import Audio, Video
from ..param import ParamFunction
from ..viewable import Viewable
from ..widgets.base import Widget
from .icon import ChatCopyIcon, ChatReactionIcons

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

Avatar = Union[str, BytesIO, bytes, ImageBase]
AvatarDict = Dict[str, Avatar]

USER_LOGO = "🧑"
ASSISTANT_LOGO = "🤖"
SYSTEM_LOGO = "⚙️"
ERROR_LOGO = "❌"
GPT_3_LOGO = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/1024px-ChatGPT_logo.svg.png?20230318122128"
GPT_4_LOGO = "https://upload.wikimedia.org/wikipedia/commons/a/a4/GPT-4.png"
WOLFRAM_LOGO = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/WolframCorporateLogo.svg/1920px-WolframCorporateLogo.svg.png"

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

    max_width = param.Integer(default=1200, bounds=(0, None))

    object = param.Parameter(allow_refs=False, doc="""
        The message contents. Can be any Python object that panel can display.""")

    reactions = param.List(doc="""
        Reactions to associate with the message.""")

    reaction_icons = param.ClassSelector(class_=(ChatReactionIcons, dict), doc="""
        A mapping of reactions to their reaction icons; if not provided
        defaults to `{"favorite": "heart"}`.""",)

    timestamp = param.Date(doc="""
        Timestamp of the message. Defaults to the creation time.""")

    timestamp_format = param.String(default="%H:%M", doc="The timestamp format.")

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

    renderers = param.HookList(doc="""
        A callable or list of callables that accept the object and return a
        Panel object to render the object. If a list is provided, will
        attempt to use the first renderer that does not raise an
        exception. If None, will attempt to infer the renderer
        from the object."""
    )

    user = param.Parameter(default="User", doc="""
        Name of the user who sent the message.""")

    _object_panel = param.Parameter(doc="The rendered object panel.")

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_message.css"]

    # Declares whether Pane supports updates to the Bokeh model
    _updates: ClassVar[bool] = True

    def __init__(self, object=None, **params):
        from ..param import ParamMethod  # circular imports

        self._exit_stack = ExitStack()
        self.chat_copy_icon = ChatCopyIcon(
            visible=False, width=15, height=15, css_classes=["copy-icon"]
        )
        if params.get("timestamp") is None:
            params["timestamp"] = datetime.datetime.utcnow()
        if params.get("reaction_icons") is None:
            params["reaction_icons"] = {"favorite": "heart"}
        if isinstance(params["reaction_icons"], dict):
            params["reaction_icons"] = ChatReactionIcons(
                options=params["reaction_icons"], width=15, height=15
            )
        super().__init__(object=object, **params)
        self.reaction_icons.link(self, value="reactions", bidirectional=True)
        self.reaction_icons.link(
            self, visible="show_reaction_icons", bidirectional=True
        )
        self.param.trigger("reactions", "show_reaction_icons")
        if not self.avatar:
            self.param.trigger("avatar_lookup")

        self._composite = Row()
        render_kwargs = {"inplace": True, "stylesheets": self._stylesheets}
        left_col = Column(
            ParamMethod(self._render_avatar, **render_kwargs),
            max_width=60,
            height=100,
            css_classes=["left"],
            stylesheets=self._stylesheets,
            visible=self.param.show_avatar,
            sizing_mode=None,
        )
        center_row = Row(
            ParamMethod(self._render_object, **render_kwargs),
            self.reaction_icons,
            css_classes=["center"],
            stylesheets=self._stylesheets,
            sizing_mode=None
        )
        right_col = Column(
            Row(
                HTML(
                    self.param.user, height=20, css_classes=["name"],
                    visible=self.param.show_user, stylesheets=self._stylesheets,
                ),
                self.chat_copy_icon,
                stylesheets=self._stylesheets,
                sizing_mode="stretch_width",
            ),
            center_row,
            HTML(
                self.param.timestamp.rx().strftime(self.param.timestamp_format),
                css_classes=["timestamp"],
                visible=self.param.show_timestamp
            ),
            css_classes=["right"],
            stylesheets=self._stylesheets,
            sizing_mode=None
        )
        viewable_params = {
            p: self.param[p] for p in self.param if p in Viewable.param
            if p in Viewable.param and p != 'name'
        }
        viewable_params['stylesheets'] = self._stylesheets + self.param.stylesheets.rx()
        self._composite.param.update(**viewable_params)
        self._composite[:] = [left_col, right_col]

    def _get_obj_label(self, obj):
        """
        Get the label for the object; defaults to specified object name;
        if unspecified, defaults to the type name.
        """
        label = obj.name
        type_name = type(obj).__name__
        # If the name is just type + ID, simply use type
        # e.g. Column10241 -> Column
        if label.startswith(type_name) or not label:
            label = type_name
        return label

    def _serialize_recursively(
        self,
        obj: Any,
        prefix_with_viewable_label: bool = True,
        prefix_with_container_label: bool = True
    ) -> str:
        """
        Recursively serialize the object to a string.
        """
        if isinstance(obj, Iterable) and not isinstance(obj, str):
            content = tuple(
                self._serialize_recursively(
                    o,
                    prefix_with_viewable_label=prefix_with_viewable_label,
                    prefix_with_container_label=prefix_with_container_label
                ) for o in obj
            )
            if prefix_with_container_label:
                if len(content) == 1:
                    return f"{self._get_obj_label(obj)}({content[0]})"
                else:
                    indented_content = indent(",\n".join(content), prefix=" " * 4)
                    # outputs like:
                    # Row(
                    #   1,
                    #   "str",
                    # )
                    return f"{self._get_obj_label(obj)}(\n{indented_content}\n)"
            else:
                # outputs like:
                # (1, "str")
                return f"({', '.join(content)})"

        string = obj
        if hasattr(obj, "value"):
            string = obj.value
        elif hasattr(obj, "object"):
            string = obj.object

        if hasattr(string, "decode") or isinstance(string, BytesIO):
            self.param.warning(
                f"Serializing byte-like objects are not supported yet; "
                f"using the label of the object as a placeholder for {obj}"
            )
            return self._get_obj_label(obj)

        if prefix_with_viewable_label and isinstance(obj, Viewable):
            label = self._get_obj_label(obj)
            string = f"{label}={string!r}"
        return string

    def __str__(self) -> str:
        """
        Serialize the message object to a string.
        """
        return self.serialize()

    @property
    def _synced_params(self) -> List[str]:
        return []

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = self._composite._get_model(doc, root, parent, comm)
        ref = (root or model).ref['id']
        self._models[ref] = (model, parent)
        return model

    @staticmethod
    def _to_alpha_numeric(user: str) -> str:
        """
        Convert the user name to an alpha numeric string,
        removing all non-alphanumeric characters.
        """
        return re.sub(r"\W+", "", user).lower()

    def _avatar_lookup(self, user: str) -> Avatar:
        """
        Lookup the avatar for the user.
        """
        alpha_numeric_key = self._to_alpha_numeric(user)
        # always use the default first
        updated_avatars = DEFAULT_AVATARS.copy()
        # update with the user input
        updated_avatars.update(self.default_avatars)
        # correct the keys to be alpha numeric
        updated_avatars = {
            self._to_alpha_numeric(key): value for key, value in updated_avatars.items()
        }
        # now lookup the avatar
        return updated_avatars.get(alpha_numeric_key, self.avatar)

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

    def _set_default_attrs(self, obj):
        """
        Set the sizing mode and height of the object.
        """
        if hasattr(obj, "objects"):
            obj._stylesheets = self._stylesheets
            for subobj in obj.objects:
                self._set_default_attrs(subobj)
            return None

        is_markup = isinstance(obj, HTMLBasePane) and not isinstance(obj, FileBase)
        if is_markup:
            if len(str(obj.object)) > 0:  # only show a background if there is content
                obj.css_classes = [*obj.css_classes, "message"]
            obj.sizing_mode = None
        else:
            if obj.sizing_mode is None and not obj.width:
                obj.sizing_mode = "stretch_width"

            if obj.height is None and not isinstance(obj, ParamFunction):
                obj.height = 500
        return obj

    @staticmethod
    def _is_widget_renderer(renderer):
        return isinstance(renderer, type) and issubclass(renderer, Widget)

    def _create_panel(self, value):
        """
        Create a panel object from the value.
        """
        if isinstance(value, Viewable):
            return value

        renderer = _panel
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
            object_panel = _panel(value)

        self._set_default_attrs(object_panel)
        return object_panel

    @param.depends("avatar", "show_avatar")
    def _render_avatar(self) -> HTML | Image:
        """
        Render the avatar pane as some HTML text or Image pane.
        """
        avatar = self.avatar
        if not avatar and self.user:
            avatar = self.user[0]

        if isinstance(avatar, ImageBase):
            avatar_pane = avatar
            avatar_pane.param.update(width=35, height=35)
        elif not isinstance(avatar, (BytesIO, bytes)) and len(avatar) == 1:
            # single character
            avatar_pane = HTML(avatar)
        else:
            try:
                avatar_pane = Image(avatar, width=35, height=35)
            except ValueError:
                # likely an emoji
                avatar_pane = HTML(avatar)
        avatar_pane.css_classes = ["avatar", *avatar_pane.css_classes]
        avatar_pane.visible = self.show_avatar
        return avatar_pane

    def _update(self, ref, old_models):
        """
        Internals will be updated inplace.
        """

    @param.depends("object")
    def _render_object(self) -> Viewable:
        """
        Renders object as a panel object.
        """
        # used in ChatFeed to extract its contents
        self._object_panel = object_panel = self._create_panel(self.object)
        return object_panel

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
            self.avatar = self._avatar_lookup(self.user)

    @param.depends("_object_panel", watch=True)
    def _update_chat_copy_icon(self):
        object_panel = self._object_panel
        if isinstance(object_panel, HTMLBasePane):
            object_panel = object_panel.object
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

    def stream(self, token: str):
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
        """
        i = -1
        parent_panel = None
        object_panel = self
        attr = "object"
        obj = self.object
        while not isinstance(obj, str) or isinstance(object_panel, ImageBase):
            object_panel = obj
            if hasattr(obj, "objects"):
                parent_panel = obj
                attr = "objects"
                obj = obj.objects[i]
                i = -1
            elif hasattr(obj, "object"):
                attr = "object"
                obj = obj.object
            elif hasattr(obj, "value"):
                attr = "value"
                obj = obj.value
            elif parent_panel is not None:
                obj = parent_panel
                parent_panel = None
                i -= 1
        setattr(object_panel, attr, obj + token)

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

    def serialize(
        self,
        prefix_with_viewable_label: bool = True,
        prefix_with_container_label: bool = True
    ) -> str:
        """
        Format the object to a string.

        Arguments
        ---------
        obj : Any
            The object to format.
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
        return self._serialize_recursively(
            self.object,
            prefix_with_viewable_label=prefix_with_viewable_label,
            prefix_with_container_label=prefix_with_container_label,
        )
