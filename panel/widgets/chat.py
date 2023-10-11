"""The chat module provides components for building and using chat interfaces

For example `ChatEntry`, `ChatFeed` and `ChatInterface`.
"""
from __future__ import annotations

import asyncio
import datetime
import re
import traceback

from contextlib import ExitStack
from dataclasses import dataclass
from functools import partial
from inspect import (
    isasyncgen, isasyncgenfunction, isawaitable, isgenerator,
)
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import (
    Any, BinaryIO, ClassVar, Dict, List, Type, Union,
)

import param
import requests

from .._param import Margin
from ..io.cache import cache
from ..io.resources import CDN_DIST
from ..io.state import state
from ..layout import (
    Column, ListPanel, Row, Tabs,
)
from ..layout.card import Card
from ..layout.spacer import VSpacer
from ..pane.base import panel as _panel
from ..pane.image import (
    PDF, SVG, FileBase, Image, ImageBase,
)
from ..pane.markup import HTML, DataFrame, HTMLBasePane
from ..pane.media import Audio, Video
from ..reactive import ReactiveHTML
from ..viewable import Viewable
from .base import CompositeWidget, Widget
from .button import Button
from .input import FileInput, TextInput

Avatar = Union[str, BytesIO, ImageBase]
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
    "translator": "🌐",
    "wolfram": WOLFRAM_LOGO,
    "wolfram alpha": WOLFRAM_LOGO,
    # Llama
    "llama": "🦙",
    "llama2": "🐪",
}

PLACEHOLDER_SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-loader-3" width="40" height="40" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M3 12a9 9 0 0 0 9 9a9 9 0 0 0 9 -9a9 9 0 0 0 -9 -9"></path>
        <path d="M17 12a5 5 0 1 0 -5 5"></path>
    </svg>
"""  # noqa: E501

# if user cannot connect to internet
MISSING_SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-help-square" width="15" height="15" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M3 5a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14z"></path>
        <path d="M12 16v.01"></path>
        <path d="M12 13a2 2 0 0 0 .914 -3.782a1.98 1.98 0 0 0 -2.414 .483"></path>
    </svg>
"""  # noqa: E501

MISSING_FILLED_SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-help-square-filled" width="15" height="15" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M19 2a3 3 0 0 1 2.995 2.824l.005 .176v14a3 3 0 0 1 -2.824 2.995l-.176 .005h-14a3 3 0 0 1 -2.995 -2.824l-.005 -.176v-14a3 3 0 0 1 2.824 -2.995l.176 -.005h14zm-7 13a1 1 0 0 0 -.993 .883l-.007 .117l.007 .127a1 1 0 0 0 1.986 0l.007 -.117l-.007 -.127a1 1 0 0 0 -.993 -.883zm1.368 -6.673a2.98 2.98 0 0 0 -3.631 .728a1 1 0 0 0 1.44 1.383l.171 -.18a.98 .98 0 0 1 1.11 -.15a1 1 0 0 1 -.34 1.886l-.232 .012a1 1 0 0 0 .111 1.994a3 3 0 0 0 1.371 -5.673z" stroke-width="0" fill="currentColor"></path>
    </svg>
"""  # noqa: E501


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


@dataclass
class _ChatButtonData:
    """
    A dataclass to hold the metadata and data related to the
    chat buttons.

    Parameters
    ----------
    index : int
        The index of the button.
    name : str
        The name of the button.
    icon : str
        The icon to display.
    objects : List
        The objects to display.
    buttons : List
        The buttons to display.
    """
    index: int
    name: str
    icon: str
    objects: List
    buttons: List


class ChatReactionIcons(ReactiveHTML):
    """
    A widget to display reaction icons that can be clicked on.

    Parameters
    ----------
    value : List
        The selected reactions.
    options : Dict
        A key-value pair of reaction values and their corresponding tabler icon names
        found on https://tabler-icons.io.
    active_icons : Dict
        The mapping of reactions to their corresponding active icon names;
        if not set, the active icon name will default to its "filled" version.

    Reference: https://panel.holoviz.org/reference/widgets/ChatReactionIcons.html

    :Example:

    >>> ChatReactionIcons(value=["like"], options={"like": "thumb-up", "dislike": "thumb-down"})
    """

    active_icons = param.Dict(default={}, doc="""
        The mapping of reactions to their corresponding active icon names;
        if not set, the active icon name will default to its "filled" version.""")

    options = param.Dict(default={"favorite": "heart"}, doc="""
        A key-value pair of reaction values and their corresponding tabler icon names
        found on https://tabler-icons.io.""")

    value = param.List(doc="The active reactions.")

    _reactions = param.List(doc="""
        The list of reactions, which is the same as the keys of the options dict;
        primarily needed as a workaround for quirks of ReactiveHTML.""")

    _svgs = param.List(doc="""
        The list of SVGs corresponding to the active reactions.""")

    _base_url = param.String(default="https://tabler-icons.io/static/tabler-icons/icons/", doc="""
        The base URL for the SVGs.""")

    _template = """
    <div id="reaction-icons" class="reaction-icons">
        {% for option in options %}
        <span
            type="button"
            id="reaction-{{ loop.index0 }}"
            onclick="${script('toggle_value')}"
            style="cursor: pointer; width: ${model.width}px; height: ${model.height}px;"
            title="{{ _reactions[loop.index0]|title }}"
        >
            ${_svgs[{{ loop.index0 }}]}
        </span>
        {% endfor %}
    </div>
    """

    _scripts = {
        "toggle_value": """
            svg = event.target.shadowRoot.querySelector("svg");
            const reaction = svg.getAttribute("alt");
            const icon_name = data.options[reaction];
            let src;
            if (data.value.includes(reaction)) {
                src = `${data._base_url}${icon_name}.svg`;
                data.value = data.value.filter(r => r !== reaction);
            } else {
                src = reaction in data.active_icons
                    ? `${data._base_url}${data.active_icons[reaction]}.svg`
                    : `${data._base_url}${icon_name}-filled.svg`;
                data.value = [...data.value, reaction];
            }
            event.target.src = src;
        """
    }

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_reaction_icons.css"
    ]

    def _get_label(self, active: bool, reaction: str, icon: str):
        if active and reaction in self.active_icons:
            icon_label = self.active_icons[reaction]
        elif active:
            icon_label = f"{icon}-filled"
        else:
            icon_label = icon
        return icon_label

    @cache
    def _fetch_svg(self, icon_label: str):
        src = f"{self._base_url}{icon_label}.svg"
        with requests.get(src) as response:
            response.raise_for_status()
            svg = response.text
        return svg

    def _stylize_svg(self, svg, reaction):
        if b"dark" in state.session_args.get("theme", []):
            svg = svg.replace('stroke="currentColor"', 'stroke="white"')
            svg = svg.replace('fill="currentColor"', 'fill="white"')
        if self.width:
            svg = svg.replace('width="24"', f'width="{self.width}px"')
        if self.height:
            svg = svg.replace('height="24"', f'height="{self.height}px"')
        svg = svg.replace("<svg", f'<svg alt="{reaction}"')
        return svg

    @param.depends(
        "value",
        "options",
        "active_icons",
        "width",
        "height",
        watch=True,
        on_init=True,
    )
    def _update_icons(self):
        self._reactions = list(self.options.keys())
        svgs = []
        for reaction, icon in self.options.items():
            active = reaction in self.value
            icon_label = self._get_label(active, reaction, icon)
            try:
                svg = self._fetch_svg(icon_label)
            except Exception:
                svg = MISSING_FILLED_SVG if active else MISSING_SVG
            svg = self._stylize_svg(svg, reaction)
            # important not to encode to keep the alt text!
            svg_pane = SVG(
                svg,
                sizing_mode=None,
                alt_text=reaction,
                encode=False,
                margin=0,
            )
            svgs.append(svg_pane)
        self._svgs = svgs

        for reaction in self.value:
            if reaction not in self._reactions:
                self.value.remove(reaction)


class ChatCopyIcon(ReactiveHTML):

    value = param.String(default=None, doc="The text to copy to the clipboard.")

    _template = """
        <div
            type="button"
            id="copy-button"
            onclick="${script('copy_to_clipboard')}"
            style="cursor: pointer; width: ${model.width}px; height: ${model.height}px;"
            title="Copy message to clipboard"
        >
            <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-copy"
                width="${model.width}" height="${model.height}" viewBox="0 0 24 24"
                stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"
            >
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                <path d="M8 8m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z"></path>
                <path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2"></path>
            </svg>
        </div>
    """

    _scripts = {"copy_to_clipboard": "navigator.clipboard.writeText(`${data.value}`)"}

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_copy_icon.css"
    ]


class ChatEntry(CompositeWidget):
    """
    A widget for displaying chat messages with support for various content types.

    This widget provides a structured view of chat messages, including features like:
    - Displaying user avatars, which can be text, emoji, or images.
    - Showing the user's name.
    - Displaying the message timestamp in a customizable format.
    - Associating reactions with messages and mapping them to icons.
    - Rendering various content types including text, images, audio, video, and more.

    Reference: https://panel.holoviz.org/reference/widgets/ChatEntry.html

    :Example:

    >>> ChatEntry(value="Hello world!", user="New User", avatar="😊")
    """

    avatar = param.ClassSelector(default="", class_=(str, BinaryIO, ImageBase), doc="""
        The avatar to use for the user. Can be a single character text, an emoji,
        or anything supported by `pn.pane.Image`. If not set, checks if
        the user is available in the default_avatars mapping; else uses the
        first character of the name.""")

    avatar_lookup = param.Callable(default=None, doc="""
        A function that can lookup an `avatar` from a user name. The function signature should be
        `(user: str) -> Avatar`. If this is set, `default_avatars` is disregarded.""")

    css_classes = param.List(default=["chat-entry"], doc="""
        The CSS classes to apply to the widget.""")

    default_avatars = param.Dict(default=DEFAULT_AVATARS, doc="""
        A default mapping of user names to their corresponding avatars
        to use when the user is specified but the avatar is. You can modify, but not replace the
        dictionary.""")

    reactions = param.List(doc="""
        Reactions to associate with the message.""")

    reaction_icons = param.ClassSelector(class_=(ChatReactionIcons, dict), doc="""
        A mapping of reactions to their reaction icons; if not provided
        defaults to `{"favorite": "heart"}`.""")

    timestamp = param.Date(doc="""
        Timestamp of the message. Defaults to the creation time.""")

    timestamp_format = param.String(default="%H:%M", doc="The timestamp format.")

    show_avatar = param.Boolean(default=True, doc="Whether to display the avatar of the user.")

    show_user = param.Boolean(default=True, doc="Whether to display the name of the user.")

    show_timestamp = param.Boolean(default=True, doc="Whether to display the timestamp of the message.")

    show_reaction_icons = param.Boolean(default=True, doc="Whether to display the reaction icons.")

    show_copy_icon = param.Boolean(default=True, doc="Whether to display the copy icon.")

    renderers = param.HookList(doc="""
        A callable or list of callables that accept the value and return a
        Panel object to render the value. If a list is provided, will
        attempt to use the first renderer that does not raise an
        exception. If None, will attempt to infer the renderer
        from the value.""")

    user = param.Parameter(default="User", doc="""
        Name of the user who sent the message.""")

    value = param.Parameter(doc="""
        The message contents. Can be any Python object that panel can display.""", allow_refs=False)

    _value_panel = param.Parameter(doc="The rendered value panel.")

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_entry.css"
    ]

    def __init__(self, **params):
        from ..param import ParamMethod  # circular imports

        self._exit_stack = ExitStack()

        self.chat_copy_icon = ChatCopyIcon(
            visible=False, width=15, height=15, css_classes=["copy-icon"])
        if params.get("timestamp") is None:
            params["timestamp"] = datetime.datetime.utcnow()
        if params.get("reaction_icons") is None:
            params["reaction_icons"] = {"favorite": "heart"}
        if isinstance(params["reaction_icons"], dict):
            params["reaction_icons"] = ChatReactionIcons(
                options=params["reaction_icons"], width=15, height=15)
        super().__init__(**params)
        self.reaction_icons.link(self, value="reactions", bidirectional=True)
        self.reaction_icons.link(self, visible="show_reaction_icons", bidirectional=True)
        self.param.trigger("reactions", "show_reaction_icons")
        if not self.avatar:
            self.param.trigger("avatar_lookup")

        render_kwargs = {
            "inplace": True, "stylesheets": self._stylesheets
        }
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
            ParamMethod(self._render_value, **render_kwargs),
            self.reaction_icons,
            css_classes=["center"],
            stylesheets=self._stylesheets,
            sizing_mode=None,
        )
        right_col = Column(
            Row(
                ParamMethod(self._render_user, **render_kwargs),
                self.chat_copy_icon,
                stylesheets=self._stylesheets,
                sizing_mode="stretch_width",
            ),
            center_row,
            ParamMethod(self._render_timestamp, **render_kwargs),
            css_classes=["right"],
            stylesheets=self._stylesheets,
            sizing_mode=None,
        )
        self._composite.param.update(
            stylesheets = self._stylesheets,
            css_classes = self.css_classes
        )
        self._composite[:] = [left_col, right_col]

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
        alpha_numeric_key =  self._to_alpha_numeric(user)
        # always use the default first
        updated_avatars = DEFAULT_AVATARS.copy()
        # update with the user input
        updated_avatars.update(self.default_avatars)
        # correct the keys to be alpha numeric
        updated_avatars = {
            self._to_alpha_numeric(key): value
            for key, value in updated_avatars.items()
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
            contents = self._exit_stack.enter_context(
                BytesIO(contents)
            )
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
            contents = self._exit_stack.enter_context(
                BytesIO(contents)
            )
            renderer = Video
        elif mime_type.startswith("image/"):
            contents = self._exit_stack.enter_context(
                BytesIO(contents)
            )
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

        is_markup = (
            isinstance(obj, HTMLBasePane) and
            not isinstance(obj, FileBase)
        )
        if is_markup:
            if len(str(obj.object)) > 0:  # only show a background if there is content
                obj.css_classes = [*obj.css_classes, "message"]
            obj.sizing_mode = None
        else:
            if obj.sizing_mode is None and not obj.width:
                obj.sizing_mode = "stretch_width"

            if obj.height is None:
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
            value, renderer = self._select_renderer(
                contents, mime_type
            )
        else:
            try:
                import magic
                mime_type = magic.from_buffer(value, mime=True)
                value, renderer = self._select_renderer(
                    value, mime_type
                )
            except Exception:
                pass

        renderers = self.renderers.copy() or []
        renderers.append(renderer)
        for renderer in renderers:
            try:
                if self._is_widget_renderer(renderer):
                    value_panel = renderer(value=value)
                else:
                    value_panel = renderer(value)
                if isinstance(value_panel, Viewable):
                    break
            except Exception:
                pass
        else:
            value_panel = _panel(value)

        self._set_default_attrs(value_panel)
        return value_panel

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
        elif len(avatar) == 1:
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

    @param.depends("user", "show_user")
    def _render_user(self) -> HTML:
        """
        Render the user pane as some HTML text or Image pane.
        """
        return HTML(self.user, height=20, css_classes=["name"], visible=self.show_user)

    @param.depends("value")
    def _render_value(self) -> Viewable:
        """
        Renders value as a panel object.
        """
        value = self.value
        value_panel = self._create_panel(value)

        # used in ChatFeed to extract its contents
        self._value_panel = value_panel
        return value_panel

    @param.depends("timestamp", "timestamp_format", "show_timestamp")
    def _render_timestamp(self) -> HTML:
        """
        Formats the timestamp and renders it as HTML pane.
        """
        return HTML(
            self.timestamp.strftime(self.timestamp_format),
            css_classes=["timestamp"],
            visible=self.show_timestamp,
        )

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

    @param.depends("_value_panel", watch=True)
    def _update_chat_copy_icon(self):
        value = self._value_panel
        if isinstance(value, HTMLBasePane):
            value = value.object
        if isinstance(value, str) and self.show_copy_icon:
            self.chat_copy_icon.value = value
            self.chat_copy_icon.visible = True
        else:
            self.chat_copy_icon.value = ""
            self.chat_copy_icon.visible = False

    def _cleanup(self, root=None) -> None:
        """
        Cleanup the exit stack.
        """
        if self._exit_stack is not None:
            self._exit_stack.close()
            self._exit_stack = None
        super()._cleanup()

    def stream(self, token: str):
        """
        Updates the entry with the new token traversing the value to
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
        value_panel = self
        attr = "value"
        value = self.value
        while not isinstance(value, str) or isinstance(value_panel, ImageBase):
            value_panel = value
            if hasattr(value, "objects"):
                parent_panel = value
                attr = "objects"
                value = value.objects[i]
                i = -1
            elif hasattr(value, "object"):
                attr = "object"
                value = value.object
            elif hasattr(value, "value"):
                attr = "value"
                value = value.value
            elif parent_panel is not None:
                value = parent_panel
                parent_panel = None
                i -= 1
        setattr(value_panel, attr, value + token)

    def update(
        self,
        value: dict | ChatEntry | Any,
        user: str | None = None,
        avatar: str | BinaryIO | None = None
    ):
        """
        Updates the entry with a new value, user and avatar.

        Arguments
        ---------
        value : ChatEntry | dict | Any
            The message contents to send.
        user : str | None
            The user to send as; overrides the message entry's user if provided.
        avatar : str | BinaryIO | None
            The avatar to use; overrides the message entry's avatar if provided.
        """
        updates = {}
        if isinstance(value, dict):
            updates.update(value)
            if user:
                updates['user'] = user
            if avatar:
                updates['avatar'] = avatar
        elif isinstance(value, ChatEntry):
            if user is not None or avatar is not None:
                raise ValueError(
                    "Cannot set user or avatar when explicitly sending "
                    "a ChatEntry. Set them directly on the ChatEntry."
                )
            updates = value.param.values()
        else:
            updates["value"] = value
        self.param.update(**updates)


class ChatFeed(CompositeWidget):
    """
    A widget to display a list of `ChatEntry` objects and interact with them.

    This widget provides methods to:
    - Send (append) messages to the chat log.
    - Stream tokens to the latest `ChatEntry` in the chat log.
    - Execute callbacks when a user sends a message.
    - Undo a number of sent `ChatEntry` objects.
    - Clear the chat log of all `ChatEntry` objects.

    Reference: https://panel.holoviz.org/reference/widgets/ChatFeed.html

    :Example:

    >>> async def say_welcome(contents, user, instance):
    >>>    yield "Welcome!"
    >>>    yield "Glad you're here!"

    >>> chat_feed = ChatFeed(callback=say_welcome, header="Welcome Feed")
    >>> chat_feed.send("Hello World!", user="New User", avatar="😊")
    """

    callback = param.Callable(allow_refs=False, doc="""
        Callback to execute when a user sends a message or
        when `respond` is called. The signature must include
        the previous message value `contents`, the previous `user` name,
        and the component `instance`.""")

    callback_exception = param.ObjectSelector(
        default="summary",
        objects=["raise", "summary", "verbose", "ignore"],
        doc="""
        How to handle exceptions raised by the callback.
        If "raise", the exception will be raised.
        If "summary", a summary will be sent to the chat feed.
        If "verbose", the full traceback will be sent to the chat feed.
        If "ignore", the exception will be ignored.
        """)

    callback_user = param.String(default="Assistant", doc="""
        The default user name to use for the entry provided by the callback.""")

    card_params = param.Dict(default={}, doc="""
        Params to pass to Card, like `header`,
        `header_background`, `header_color`, etc.""")

    entry_params = param.Dict(default={}, doc="""
        Params to pass to each ChatEntry, like `reaction_icons`, `timestamp_format`,
        `show_avatar`, `show_user`, and `show_timestamp`.""")

    header = param.Parameter(doc="""
        The header of the chat feed; commonly used for the title.
        Can be a string, pane, or widget.""")

    margin = Margin(default=5, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    renderers = param.HookList(doc="""
        A callable or list of callables that accept the value and return a
        Panel object to render the value. If a list is provided, will
        attempt to use the first renderer that does not raise an
        exception. If None, will attempt to infer the renderer
        from the value.""")

    placeholder_text = param.String(default="", doc="""
        If placeholder is the default LoadingSpinner,
        the text to display next to it.""")

    placeholder_threshold = param.Number(default=1, bounds=(0, None), doc="""
        Min duration in seconds of buffering before displaying the placeholder.
        If 0, the placeholder will be disabled.""")

    auto_scroll_limit = param.Integer(default=200, bounds=(0, None), doc="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""")

    scroll_button_threshold = param.Integer(default=100, bounds=(0, None), doc="""
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.""")

    view_latest = param.Boolean(default=True, doc="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""")
    value = param.List(item_type=ChatEntry, doc="""
        The list of entries in the feed.""")

    _placeholder = param.ClassSelector(class_=ChatEntry, allow_refs=False, doc="""
        The placeholder wrapped in a ChatEntry object;
        primarily to prevent recursion error in _update_placeholder.""")

    _disabled = param.Boolean(default=False, doc="""
        Whether the chat feed is disabled.""")

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_feed.css"
    ]

    _composite_type: ClassVar[Type[ListPanel]] = Card

    def __init__(self, **params):
        if params.get("renderers") and not isinstance(params["renderers"], list):
            params["renderers"] = [params["renderers"]]
        super().__init__(**params)
        # instantiate the card
        card_params = {
            "header": self.header,
            "hide_header": self.header is None,
            "collapsed": False,
            "collapsible": False,
            "css_classes": ["chat-feed"],
            "header_css_classes": ["chat-feed-header"],
            "title_css_classes": ["chat-feed-title"],
            "sizing_mode": self.sizing_mode,
            "height": self.height,
            "width": self.width,
            "max_width": self.max_width,
            "max_height": self.max_height,
            "styles": {"border": "1px solid var(--panel-border-color, #e1e1e1)", "padding": "0px"},
            "stylesheets": self._stylesheets
        }
        card_params.update(**self.card_params)
        if self.sizing_mode is None:
            card_params["height"] = card_params.get("height", 500)
        self._composite.param.update(**card_params)

        # instantiate the card's column
        chat_log_params = {
            p: getattr(self, p)
            for p in Column.param
            if (
                p in ChatFeed.param and
                p != "name" and
                getattr(self, p) is not None
            )
        }
        chat_log_params["css_classes"] = ["chat-feed-log"]
        chat_log_params["stylesheets"] = self._stylesheets
        chat_log_params["objects"] = self.value
        chat_log_params["margin"] = 0
        self._chat_log = Column(**chat_log_params)
        self._composite[:] = [self._chat_log, VSpacer()]

        # handle async callbacks using this trick
        self._callback_trigger = Button(visible=False)
        self._callback_trigger.on_click(self._prepare_response)

        self.link(self._chat_log, value="objects", bidirectional=True)

    @param.depends("placeholder_text", watch=True, on_init=True)
    def _update_placeholder(self):
        loading_avatar = SVG(
            PLACEHOLDER_SVG,
            sizing_mode=None,
            css_classes=["rotating-placeholder"]
        )
        self._placeholder = ChatEntry(
            user=" ",
            value=self.placeholder_text,
            show_timestamp=False,
            avatar=loading_avatar,
            reaction_icons={},
            show_copy_icon=False,
        )

    @param.depends("header", watch=True)
    def _hide_header(self):
        """
        Hide the header if there is no title or header.
        """
        self._composite.hide_header = not self.header

    def _replace_placeholder(self, entry: ChatEntry | None = None) -> None:
        """
        Replace the placeholder from the chat log with the entry
        if placeholder, otherwise simply append the entry.
        Replacing helps lessen the chat log jumping around.
        """
        index = None
        if self.placeholder_threshold > 0:
            try:
                index = self.value.index(self._placeholder)
            except ValueError:
                pass

        if index is not None:
            if entry is not None:
                self._chat_log[index] = entry
            elif entry is None:
                self._chat_log.remove(self._placeholder)
        elif entry is not None:
            self._chat_log.append(entry)

    def _build_entry(
        self,
        value: dict,
        user: str | None = None,
        avatar: str | BinaryIO | None = None,
    ) -> ChatEntry | None:
        """
        Builds a ChatEntry from the value.
        """
        if "value" not in value:
            raise ValueError(
                f"If 'value' is a dict, it must contain a 'value' key, "
                f"e.g. {{'value': 'Hello World'}}; got {value!r}"
            )
        entry_params = dict(value, renderers=self.renderers, **self.entry_params)
        if user:
            entry_params['user'] = user
        if avatar:
            entry_params['avatar'] = avatar
        if self.width:
            entry_params['width'] = int(self.width - 80)
        entry = ChatEntry(**entry_params)
        return entry

    def _upsert_entry(self, value: Any, entry: ChatEntry | None = None) -> ChatEntry | None:
        """
        Replace the placeholder entry with the response or update
        the entry's value with the response.
        """
        if value is None:
            # don't add new entry if the callback returns None
            return

        user = self.callback_user
        avatar = None
        if isinstance(value, dict):
            user = value.get('user', user)
            avatar = value.get('avatar')
        if entry is not None:
            entry.update(value, user=user, avatar=avatar)
            return entry
        elif isinstance(value, ChatEntry):
            return value

        if not isinstance(value, dict):
            value = {"value": value}
        new_entry = self._build_entry(value, user=user, avatar=avatar)
        self._replace_placeholder(new_entry)
        return new_entry

    def _extract_contents(self, entry: ChatEntry) -> Any:
        """
        Extracts the contents from the entry's panel object.
        """
        value = entry._value_panel
        if hasattr(value, "object"):
            contents = value.object
        elif hasattr(value, "objects"):
            contents = value.objects
        elif hasattr(value, "value"):
            contents = value.value
        else:
            contents = value
        return contents

    async def _serialize_response(self, response: Any) -> ChatEntry | None:
        """
        Serializes the response by iterating over it and
        updating the entry's value.
        """
        response_entry = None
        if isasyncgen(response):
            async for token in response:
                response_entry = self._upsert_entry(token, response_entry)
        elif isgenerator(response):
            for token in response:
                response_entry = self._upsert_entry(token, response_entry)
        elif isawaitable(response):
            response_entry = self._upsert_entry(await response, response_entry)
        else:
            response_entry = self._upsert_entry(response, response_entry)
        return response_entry

    async def _handle_callback(self, entry: ChatEntry) -> ChatEntry | None:
        contents = self._extract_contents(entry)
        response = self.callback(contents, entry.user, self)
        response_entry = await self._serialize_response(response)
        return response_entry

    async def _schedule_placeholder(
        self,
        task: asyncio.Task,
        num_entries: int,
    ) -> None:
        """
        Schedules the placeholder to be added to the chat log
        if the callback takes longer than the placeholder threshold.
        """
        if self.placeholder_threshold == 0:
            return

        callable_is_async = (
            asyncio.iscoroutinefunction(self.callback) or
            isasyncgenfunction(self.callback)
        )
        start = asyncio.get_event_loop().time()
        while not task.done() and num_entries == len(self._chat_log):
            duration = asyncio.get_event_loop().time() - start
            if duration > self.placeholder_threshold or not callable_is_async:
                self._chat_log.append(self._placeholder)
                return
            await asyncio.sleep(0.28)

    async def _prepare_response(self, _) -> None:
        """
        Prepares the response by scheduling the placeholder and
        executing the callback.
        """
        if self.callback is None:
            return

        disabled = self.disabled
        try:
            self.disabled = True
            entry = self._chat_log[-1]
            if not isinstance(entry, ChatEntry):
                return

            num_entries = len(self._chat_log)
            task = asyncio.create_task(self._handle_callback(entry))
            await self._schedule_placeholder(task, num_entries)
            await task
            task.result()
        except Exception as e:
            send_kwargs = dict(
                user="Exception",
                respond=False
            )
            if self.callback_exception == "summary":
                self.send(str(e), **send_kwargs)
            elif self.callback_exception == "verbose":
                self.send(f"```python\n{traceback.format_exc()}\n```", **send_kwargs)
            elif self.callback_exception == "ignore":
                return
            else:
                raise e
        finally:
            self._replace_placeholder(None)
            self.disabled = disabled

    # Public API

    def send(
        self,
        value: ChatEntry | dict | Any,
        user: str | None = None,
        avatar: str | BinaryIO | None = None,
        respond: bool = True,
    ) -> ChatEntry | None:
        """
        Sends a value and creates a new entry in the chat log.

        If `respond` is `True`, additionally executes the callback, if provided.

        Arguments
        ---------
        value : ChatEntry | dict | Any
            The message contents to send.
        user : str | None
            The user to send as; overrides the message entry's user if provided.
        avatar : str | BinaryIO | None
            The avatar to use; overrides the message entry's avatar if provided.
        respond : bool
            Whether to execute the callback.

        Returns
        -------
        The entry that was created.
        """
        if isinstance(value, ChatEntry):
            if user is not None or avatar is not None:
                raise ValueError(
                    "Cannot set user or avatar when explicitly sending "
                    "a ChatEntry. Set them directly on the ChatEntry."
                )
            entry = value
        else:
            if not isinstance(value, dict):
                value = {"value": value}
            entry = self._build_entry(value, user=user, avatar=avatar)
        self._chat_log.append(entry)
        if respond:
            self.respond()
        return entry

    def stream(
        self,
        value: str,
        user: str | None = None,
        avatar: str | BinaryIO | None = None,
        entry: ChatEntry | None = None,
    ) -> ChatEntry | None:
        """
        Streams a token and updates the provided entry, if provided.
        Otherwise creates a new entry in the chat log, so be sure the
        returned entry is passed back into the method, e.g.
        `entry = chat.stream(token, entry=entry)`.

        This method is primarily for outputs that are not generators--
        notably LangChain. For most cases, use the send method instead.

        Arguments
        ---------
        value : str | dict | ChatEntry
            The new token value to stream.
        user : str | None
            The user to stream as; overrides the entry's user if provided.
        avatar : str | BinaryIO | None
            The avatar to use; overrides the entry's avatar if provided.
        entry : ChatEntry | None
            The entry to update.

        Returns
        -------
        The entry that was updated.
        """
        if isinstance(value, ChatEntry) and (user is not None or avatar is not None):
            raise ValueError(
                "Cannot set user or avatar when explicitly streaming "
                "a ChatEntry. Set them directly on the ChatEntry."
            )
        elif entry:
            if isinstance(value, (str, dict)):
                entry.stream(value)
                if user:
                    entry.user = user
                if avatar:
                    entry.avatar = avatar
            else:
                entry.update(value, user=user, avatar=avatar)
            return entry

        if isinstance(value, ChatEntry):
            entry = value
        else:
            if not isinstance(value, dict):
                value = {"value": value}
            entry = self._build_entry(value, user=user, avatar=avatar)
        self._replace_placeholder(entry)
        return entry

    def respond(self):
        """
        Executes the callback with the latest entry in the chat log.
        """
        self._callback_trigger.param.trigger("clicks")

    def undo(self, count: int = 1) -> List[Any]:
        """
        Removes the last `count` of entries from the chat log and returns them.

        Parameters
        ----------
        count : int
            The number of entries to remove, starting from the last entry.

        Returns
        -------
        The entries that were removed.
        """
        if count <= 0:
            return []
        entries = self._chat_log.objects
        undone_entries = entries[-count:]
        self._chat_log.objects = entries[:-count]
        return undone_entries

    def clear(self) -> List[Any]:
        """
        Clears the chat log and returns the entries that were cleared.

        Returns
        -------
        The entries that were cleared.
        """
        cleared_entries = self._chat_log.objects
        self._chat_log.clear()
        return cleared_entries


class ChatInterface(ChatFeed):
    """
    High level widget that contains the chat log and the chat input.

    Reference: https://panel.holoviz.org/reference/widgets/ChatInterface.html

    :Example:

    >>> async def repeat_contents(contents, user, instance):
    >>>     yield contents

    >>> chat_interface = ChatInterface(
        callback=repeat_contents, widgets=[TextInput(), FileInput()]
    )
    """

    auto_send_types = param.List(doc="""
        The widget types to automatically send when the user presses enter
        or clicks away from the widget. If not provided, defaults to
        `[TextInput]`.""")

    avatar = param.ClassSelector(class_=(str, BinaryIO), doc="""
        The avatar to use for the user. Can be a single character text, an emoji,
        or anything supported by `pn.pane.Image`. If not set, uses the
        first character of the name.""")

    reset_on_send = param.Boolean(default=False, doc="""
        Whether to reset the widget's value after sending a message;
        has no effect for `TextInput`.""")

    show_send = param.Boolean(default=True, doc="""
        Whether to show the send button.""")

    show_rerun = param.Boolean(default=True, doc="""
        Whether to show the rerun button.""")

    show_undo = param.Boolean(default=True, doc="""
        Whether to show the undo button.""")

    show_clear = param.Boolean(default=True, doc="""
        Whether to show the clear button.""")

    show_button_name = param.Boolean(default=None, doc="""
        Whether to show the button name.""")

    user = param.String(default="User", doc="Name of the ChatInterface user.")

    widgets = param.ClassSelector(class_=(Widget, list), allow_refs=False, doc="""
        Widgets to use for the input. If not provided, defaults to
        `[TextInput]`.""")

    _widgets = param.Dict(default={}, allow_refs=False, doc="""
        The input widgets.""")

    _input_container = param.ClassSelector(class_=Row, doc="""
        The input message row that wraps the input layout (Tabs / Row)
        to easily swap between Tabs and Rows, depending on
        number of widgets.""")

    _input_layout = param.ClassSelector(class_=(Row, Tabs), doc="""
        The input layout that contains the input widgets.""")

    _button_data = param.Dict(default={}, doc="""
        Metadata and data related to the buttons.""")

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_interface.css"
    ]

    def __init__(self, **params):
        widgets = params.get("widgets")
        if widgets is None:
            params["widgets"] = [TextInput(placeholder="Send a message")]
        elif not isinstance(widgets, list):
            params["widgets"] = [widgets]
        active = params.pop("active", None)
        super().__init__(**params)

        button_icons = {
            "send": "send",
            "rerun": "repeat-once",
            "undo": "arrow-back",
            "clear": "trash",
        }
        for action in list(button_icons):
            if not getattr(self, f"show_{action}", True):
                button_icons.pop(action)
        self._button_data = {
            name: _ChatButtonData(
                index=index, name=name, icon=icon, objects=[], buttons=[]
            ) for index, (name, icon) in enumerate(button_icons.items())
        }
        self._input_container = Row(
            css_classes=["chat-interface-input-container"],
            stylesheets=self._stylesheets
        )
        self._update_input_width()
        self._init_widgets()
        if active is not None:
            self.active = active
        self._composite.param.update(
            objects=self._composite.objects+[self._input_container],
            css_classes=["chat-interface"],
            stylesheets=self._stylesheets
        )

    def _link_disabled_loading(self, obj: Viewable):
        """
        Link the disabled and loading attributes of the chat box to the
        given object.
        """
        for attr in ["disabled", "loading"]:
            setattr(obj, attr, getattr(self, attr))
            self.link(obj, **{attr: attr})

    @param.depends("width", watch=True)
    def _update_input_width(self):
        """
        Update the input width.
        """
        self.show_button_name = self.width is None or self.width >= 400

    @param.depends(
        "width",
        "widgets",
        "show_send",
        "show_rerun",
        "show_undo",
        "show_clear",
        "show_button_name",
        watch=True,
    )
    def _init_widgets(self):
        """
        Initialize the input widgets.

        Returns
        -------
        The input widgets.
        """
        widgets = self.widgets
        if isinstance(self.widgets, Widget):
            widgets = [self.widgets]

        self._widgets = {}
        for widget in widgets:
            key = widget.name or widget.__class__.__name__
            if isinstance(widget, type):  # check if instantiated
                widget = widget()
            self._widgets[key] = widget

        sizing_mode = self.sizing_mode
        if sizing_mode is not None:
            if "both" in sizing_mode or "scale_height" in sizing_mode:
                sizing_mode = "stretch_width"
            elif "height" in sizing_mode:
                sizing_mode = None
        input_layout = Tabs(
            sizing_mode=sizing_mode,
            css_classes=["chat-interface-input-tabs"],
            stylesheets=self._stylesheets,
            dynamic=True,
        )
        for name, widget in self._widgets.items():
            # for longer form messages, like TextArea / Ace, don't
            # submit when clicking away; only if they manually click
            # the send button
            auto_send_types = tuple(self.auto_send_types) or (TextInput,)
            if isinstance(widget, auto_send_types):
                widget.param.watch(self._click_send, "value")
            widget.param.update(
                sizing_mode="stretch_width",
                css_classes=["chat-interface-input-widget"]
            )

            buttons = []
            for button_data in self._button_data.values():
                if self.show_button_name:
                    button_name = button_data.name.title()
                else:
                    button_name = ""
                button = Button(
                    name=button_name,
                    icon=button_data.icon,
                    sizing_mode="stretch_width",
                    max_width=90 if self.show_button_name else 45,
                    max_height=50,
                    margin=(5, 5, 5, 0),
                    align="center",
                )
                self._link_disabled_loading(button)
                action = button_data.name
                button.on_click(getattr(self, f"_click_{action}"))
                buttons.append(button)
                button_data.buttons.append(button)

            message_row = Row(
                widget,
                *buttons,
                sizing_mode="stretch_width",
                css_classes=["chat-interface-input-row"],
                stylesheets=self._stylesheets,
                align="center",
            )
            input_layout.append((name, message_row))

        # if only a single input, don't use tabs
        if len(self._widgets) == 1:
            input_layout = input_layout[0]
        else:
            self._chat_log.css_classes = ["chat-feed-log-tabbed"]

        self._input_container.objects = [input_layout]
        self._input_layout = input_layout

    def _click_send(self, _: param.parameterized.Event | None = None) -> None:
        """
        Send the input when the user presses Enter.
        """
        # wait until the chat feed's callback is done executing
        # before allowing another input
        if self.disabled:
            return

        active_widget = self.active_widget
        value = active_widget.value
        if value:
            if isinstance(active_widget, FileInput):
                value = _FileInputMessage(
                    contents=value,
                    mime_type=active_widget.mime_type,
                    file_name=active_widget.filename,
                )
            # don't use isinstance here; TextAreaInput subclasses TextInput
            if type(active_widget) is TextInput or self.reset_on_send:
                updates = {"value": ""}
                if hasattr(active_widget, "value_input"):
                    updates["value_input"] = ""
                try:
                    active_widget.param.update(updates)
                except ValueError:
                    pass
        else:
            return  # no message entered
        self._reset_button_data()
        self.send(value=value, user=self.user, avatar=self.avatar, respond=True)

    def _get_last_user_entry_index(self) -> int:
        """
        Get the index of the last user entry.
        """
        entries = self.value[::-1]
        for index, entry in enumerate(entries, 1):
            if entry.user == self.user:
                return index
        return 0

    def _toggle_revert(self, button_data: _ChatButtonData, active: bool):
        """
        Toggle the button's icon and name to indicate
        whether the action can be reverted.
        """
        for button in button_data.buttons:
            if active and button_data.objects:
                button_update = {
                    "button_type": "warning",
                    "name": "Revert",
                    "width": 90
                }
            else:
                button_update = {
                    "button_type": "default",
                    "name": button_data.name.title() if self.show_button_name else "",
                    "width": 90 if self.show_button_name else 45
                }
            button.param.update(button_update)

    def _reset_button_data(self):
        """
        Clears all the objects in the button data
        to prevent reverting.
        """
        for button_data in self._button_data.values():
            button_data.objects.clear()
            self._toggle_revert(button_data, False)

    def _click_rerun(self, _):
        """
        Upon clicking the rerun button, rerun the last user entry,
        which can trigger the callback again.
        """
        count = self._get_last_user_entry_index()
        entries = self.undo(count)
        if not entries:
            return
        self.send(value=entries[0], respond=True)

    def _click_undo(self, _):
        """
        Upon clicking the undo button, undo (remove) entries
        up to the last user entry. If the button is clicked
        again without performing any other actions, revert the undo.
        """
        undo_data = self._button_data["undo"]
        undo_objects = undo_data.objects
        if not undo_objects:
            self._reset_button_data()
            count = self._get_last_user_entry_index()
            undo_data.objects = self.undo(count)
            self._toggle_revert(undo_data, True)
        else:
            self.value = [*self.value, *undo_objects.copy()]
            self._reset_button_data()

    def _click_clear(self, _):
        """
        Upon clicking the clear button, clear the chat log.
        If the button is clicked again without performing any
        other actions, revert the clear.
        """
        clear_data = self._button_data["clear"]
        clear_objects = clear_data.objects
        if not clear_objects:
            self._reset_button_data()
            clear_data.objects = self.clear()
            self._toggle_revert(clear_data, True)
        else:
            self.value = clear_objects.copy()
            self._reset_button_data()

    @property
    def active_widget(self) -> Widget:
        """
        The currently active widget.

        Returns
        -------
        The active widget.
        """
        if isinstance(self._input_layout, Tabs):
            return self._input_layout[self.active].objects[0]
        return self._input_layout.objects[0]

    @property
    def active(self) -> int:
        """
        The currently active input widget tab index;
        -1 if there is only one widget available
        which is not in a tab.

        Returns
        -------
        The active input widget tab index.
        """
        if isinstance(self._input_layout, Tabs):
            return self._input_layout.active
        return -1

    @active.setter
    def active(self, index: int) -> None:
        """
        Set the active input widget tab index.

        Arguments
        ---------
        index : int
            The active index to set.
        """
        if isinstance(self._input_layout, Tabs):
            self._input_layout.active = index
