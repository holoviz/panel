import asyncio
import datetime

from contextlib import ExitStack
from dataclasses import dataclass
from inspect import isasyncgen, isawaitable, isgenerator
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import (
    Any, BinaryIO, ClassVar, List, Optional, Tuple, Type, Union,
)

import param

from ..io.resources import CDN_DIST
from ..layout import (
    Column, ListPanel, Row, Tabs,
)
from ..layout.card import Card
from ..layout.spacer import VSpacer
from ..pane.base import panel as _panel
from ..pane.image import PDF, Image, ImageBase
from ..pane.markup import HTML, DataFrame, Markdown
from ..pane.media import Audio, Video
from ..reactive import ReactiveHTML
from ..viewable import Viewable
from .base import CompositeWidget, Widget
from .button import Button
from .indicators import LoadingSpinner
from .input import FileInput, TextInput


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
    icon_size : str
        The size of each icon.
    active_icons : Dict
        The mapping of reactions to their corresponding active icon names;
        if not set, the active icon name will default to its "filled" version.

    Reference: https://panel.holoviz.org/reference/widgets/ChatReactionIcons.html

    :Example:

    >>> ChatReactionIcons(value=["like"], options={"like": "thumb-up", "dislike": "thumb-down"})
    """

    value = param.List(doc="The selected reactions.")

    options = param.Dict(default={"favorite": "heart"}, doc="""
        A key-value pair of reaction values and their corresponding tabler icon names
        found on https://tabler-icons.io.""")

    icon_size = param.String(default="15px", doc="""The size of each icon.""")

    active_icons = param.Dict(default={}, doc="""
        The mapping of reactions to their corresponding active icon names;
        if not set, the active icon name will default to its "filled" version.""")

    _icon_base_url = param.String("https://tabler-icons.io/static/tabler-icons/icons/")

    _template = """
        <div id="reaction-icons" class="reaction-icons">
            {% for reaction, icon_name in options.items() %}
            <img id="icon-{{ loop.index0 }}" alt="{{ reaction }}"
                {% if reaction in value and reaction in active_icons %}
                src="${_icon_base_url}{{ active_icons[reaction] }}.svg"
                {% elif reaction in value %}
                src="${_icon_base_url}{{ icon_name }}-filled.svg"
                {% else %}
                src="${_icon_base_url}{{ icon_name }}.svg"
                {% endif %}
                style="width: ${icon_size}; height: ${icon_size}; cursor: pointer;"
                onclick="${script('update_value')}">
            </img>
            {% endfor %}
        </div>
    """

    _scripts = {
        "update_value": """
            const reaction = event.target.alt;
            const icon_name = data.options[reaction];

            let src;
            if (data.value.includes(reaction)) {
                src = `${data._icon_base_url}${icon_name}.svg`;
                data.value = data.value.filter(r => r !== reaction);
            } else {
                src = reaction in data.active_icons
                    ? `${data._icon_base_url}${data.active_icons[reaction]}.svg`
                    : `${data._icon_base_url}${icon_name}-filled.svg`;
                data.value = [...data.value, reaction];
            }
            event.target.src = src;
        """
    }

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_reaction_icons.css"
    ]

    def __init__(self, **params):
        super().__init__(**params)
        if self.icon_size.endswith("px"):
            self.max_width = int(self.icon_size[:-2])


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

    Parameters
    ----------
    value : object
        The message contents. Can be a string, pane, widget, layout, etc.
    user : str
        Name of the user who sent the message.
    avatar : str | BinaryIO
        The avatar to use for the user. Can be a single character text, an emoji,
        or anything supported by `pn.pane.Image`. If not set, uses the
        first character of the name.
    reactions : List
        Reactions to associate with the message.
    reaction_icons : ChatReactionIcons | dict
        A mapping of reactions to their reaction icons; if not provided
        defaults to `{"favorite": "heart"}`.
    timestamp : datetime
        Timestamp of the message. Defaults to the instantiation time.
    timestamp_format : str
        The timestamp format.
    show_avatar : bool
        Whether to display the avatar of the user.
    show_user : bool
        Whether to display the name of the user.
    show_timestamp : bool
        Whether to display the timestamp of the message.
    """
    _ignored_refs: ClassVar[Tuple[str,...]] = ('value',)

    value = param.Parameter(doc="""
        The message contents. Can be any Python object that panel can display.""")

    user = param.Parameter(default="User", doc="""
        Name of the user who sent the message.""")

    avatar = param.ClassSelector(default="😊", class_=(str, BinaryIO), doc="""
        The avatar to use for the user. Can be a single character text, an emoji,
        or anything supported by `pn.pane.Image`. If not set, uses the
        first character of the name.""")

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

    _value_panel = param.Parameter(doc="The rendered value panel.")

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_entry.css"
    ]

    _exit_stack: ExitStack = None

    def __init__(self, **params):
        from ..param import ParamMethod  # circular imports

        self._exit_stack = ExitStack()

        if params.get("timestamp") is None:
            params["timestamp"] = datetime.datetime.utcnow()
        if params.get("reaction_icons") is None:
            params["reaction_icons"] = {"favorite": "heart"}
        if isinstance(params["reaction_icons"], dict):
            params["reaction_icons"] = ChatReactionIcons(
                options=params["reaction_icons"])
        super().__init__(**params)
        self.reaction_icons.link(self, value="reactions", bidirectional=True)
        self.param.trigger("reactions")

        render_kwargs = dict(
            inplace=True, stylesheets=self._stylesheets
        )
        left_col = Column(
            ParamMethod(self._render_avatar, **render_kwargs),
            max_width=60,
            height=100,
            css_classes=["left"],
            stylesheets=self._stylesheets,
        )
        center_row = Row(
            ParamMethod(self._render_value, **render_kwargs),
            self.reaction_icons,
            css_classes=["center"],
            stylesheets=self._stylesheets,
        )
        right_col = Column(
            ParamMethod(self._render_user, **render_kwargs),
            center_row,
            ParamMethod(self._render_timestamp, **render_kwargs),
            css_classes=["right"],
            stylesheets=self._stylesheets,
        )
        self._composite._stylesheets = self._stylesheets
        self._composite[:] = [left_col, right_col]

    def _select_renderer(
            self,
            contents: Any,
            mime_type: str,
            file_name: str = None,
        ):
        """
        Determine the renderer to use based on the mime type.
        """
        renderer = _panel
        if mime_type == "application/pdf":
            contents = self._exit_stack.enter_context(
                BytesIO(contents)
            )
            renderer = PDF
        elif mime_type.startswith("audio/"):
            f = self._exit_stack.enter_context(
                NamedTemporaryFile(suffix=".mp3", delete=False)
            )
            f.write(contents)
            f.seek(0)
            contents = f.name
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
        elif file_name is not None:
            contents = f"`{file_name}`"
        return contents, renderer

    def _create_panel(self, value):
        """
        Create a panel object from the value.
        """
        if isinstance(value, Viewable):
            return value

        if isinstance(value, _FileInputMessage):
            contents = value.contents
            mime_type = value.mime_type
            file_name = value.file_name
            value, renderer = self._select_renderer(
                contents, mime_type, file_name=file_name
            )
        else:
            try:
                import magic
                mime_type = magic.from_buffer(value, mime=True)
                value, renderer = self._select_renderer(
                    value, mime_type, file_name=None
                )
            except Exception:
                renderer = _panel

        try:
            if isinstance(renderer, Widget):
                value_panel = renderer(value=value)
            else:
                value_panel = renderer(value)
        except ValueError:
            value_panel = _panel(value)
        return value_panel

    @param.depends("avatar", "show_avatar")
    def _render_avatar(self) -> None:
        """
        Render the avatar pane as some HTML text or Image pane.
        """
        avatar = self.avatar
        if not avatar and self.user:
            avatar = self.user[0]

        if len(avatar) == 1:
            # single character
            avatar_pane = HTML(avatar)
        else:
            try:
                avatar_pane = Image(avatar, width=35, height=35)
            except ValueError:
                # likely an emoji
                avatar_pane = HTML(avatar)
        avatar_pane.css_classes = ["avatar"]
        avatar_pane.visible = self.show_avatar
        return avatar_pane

    @param.depends("user", "show_user")
    def _render_user(self) -> None:
        """
        Render the user pane as some HTML text or Image pane.
        """
        return HTML(self.user, css_classes=["name"], visible=self.show_user)

    @param.depends("value")
    def _render_value(self):
        """
        Renders value as a panel object.
        """
        value = self.value
        if isinstance(value, str):
            value_panel = Markdown(value)
        elif isinstance(value, Viewable):
            value_panel = value
        else:
            value_panel = self._create_panel(value)
        value_panel.css_classes = [*value_panel.css_classes, "message"]

        # used in ChatFeed to extract its contents
        self._value_panel = value_panel
        return value_panel

    @param.depends("timestamp", "timestamp_format", "show_timestamp")
    def _render_timestamp(self) -> None:
        """
        Formats the timestamp and renders it as HTML pane.
        """
        return HTML(
            self.timestamp.strftime(self.timestamp_format),
            css_classes=["timestamp"],
            visible=self.show_timestamp,
        )

    def _cleanup(self, root=None) -> None:
        """
        Cleanup the exit stack.
        """
        if self._exit_stack is not None:
            self._exit_stack.close()
            self._exit_stack = None
        super()._cleanup()


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

    Parameters
    ----------
    value : List[ChatEntry]
        The entries added to the chat feed.
    header : Any
        The header of the chat feed; commonly used for the title.
        Can be a string, pane, or widget.
    callback : Callable
        Callback to execute when a user sends a message or
        when `respond` is called. The signature must include
        the previous message value `contents`, the previous `user` name,
        and the component `instance`.
    callback_user : str
        The default user name to use for the entry provided by the callback.
    callback_avatar : str | BinaryIO
        The default avatar to use for the entry provided by the callback.
    placeholder : Any
        Placeholder to display while the callback is running.
        If not set, defaults to a LoadingSpinner.
    placeholder_text : str
        If placeholder is the default LoadingSpinner,
        the text to display next to it.
    placeholder_threshold : float
        Min duration in seconds of buffering before displaying the placeholder.
        If 0, the placeholder will be disabled.
    auto_scroll_limit : int
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.
    scroll_button_threshold : int
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.
    view_latest : bool
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.
    card_params : Dict
        Params to pass to Card, like `header`,
        `header_background`, `header_color`, etc.
    entry_params : Dict
        Params to pass to each ChatEntry, like `reaction_icons`, `timestamp_format`,
        `show_avatar`, `show_user`, and `show_timestamp`.
    """
    value = param.List(item_type=ChatEntry, doc="""
        The list of entries in the feed.""")

    header = param.Parameter(doc="""
        The header of the chat feed; commonly used for the title.
        Can be a string, pane, or widget.""")

    callback = param.Callable(doc="""
        Callback to execute when a user sends a message or
        when `respond` is called. The signature must include
        the previous message value `contents`, the previous `user` name,
        and the component `instance`.""")

    callback_user = param.String(default="Assistant", doc="""
        The default user name to use for the entry provided by the callback.""")

    callback_avatar = param.ClassSelector(default="🤖", class_=(str, BinaryIO), doc="""
        The default avatar to use for the entry provided by the callback.""")

    placeholder = param.Parameter(doc="""
        Placeholder to display while the callback is running.
        If not set, defaults to a LoadingSpinner.""")

    placeholder_text = param.String(default="Loading...", doc="""
        If placeholder is the default LoadingSpinner,
        the text to display next to it.""")

    placeholder_threshold = param.Number(default=0.2, bounds=(0, None), doc="""
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

    card_params = param.Dict(default={}, doc="""
        Params to pass to Card, like `header`,
        `header_background`, `header_color`, etc.""")

    entry_params = param.Dict(default={}, doc="""
        Params to pass to each ChatEntry, like `reaction_icons`, `timestamp_format`,
        `show_avatar`, `show_user`, and `show_timestamp`.""")

    _placeholder = param.ClassSelector(class_=ChatEntry, doc="""
        The placeholder wrapped in a ChatEntry object;
        primarily to prevent recursion error in _update_placeholder.""")

    _disabled = param.Boolean(default=False, doc="""
        Whether the chat feed is disabled.""")

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_feed.css"
    ]

    _composite_type: ClassVar[Type[ListPanel]] = Card

    def __init__(self, **params):
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
        }
        card_params.update(**self.card_params)
        if self.sizing_mode is None:
            card_params["height"] = card_params.get("height", 500)
        self._composite.param.update(**card_params)
        self._composite._stylesheets = self._stylesheets

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

    @param.depends("placeholder", watch=True, on_init=True)
    def _update_placeholder(self):
        plain_entry = dict(
            show_avatar=False,
            show_user=False,
            show_timestamp=False,
            reaction_icons={},
        )
        if self.placeholder is None:
            self._placeholder = ChatEntry(
                value=LoadingSpinner(
                    name=self.param.placeholder_text,
                    value=True,
                    width=40,
                    height=40,
                ),
                **plain_entry,
            )
        else:
            self._placeholder = ChatEntry(value=self.placeholder, **plain_entry)
        self._placeholder.margin = (25, 30)

    @param.depends("header", watch=True)
    def _hide_header(self):
        """
        Hide the header if there is no title or header.
        """
        self._composite.hide_header = not self.header

    def _replace_placeholder(self, entry: Optional[ChatEntry] = None) -> None:
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
        elif entry is not None and entry.value:
            self._chat_log.append(entry)

    def _build_entry(
            self,
            value: Union[ChatEntry, dict, Any],
            user: Optional[str] = None,
            avatar: Optional[Union[str, BinaryIO]] = None,
        ) -> ChatEntry:
        """
        Builds a ChatEntry from the value.
        """
        if value is None:
            return

        if not isinstance(value, (ChatEntry, dict)):
            value = {"value": value}

        new_params = {}
        if user is not None:
            new_params["user"] = user
        if avatar is not None:
            new_params["avatar"] = avatar

        if isinstance(value, dict):
            if "value" not in value:
                raise ValueError(
                    f"If 'value' is a dict, it must contain a 'value' key, "
                    f"e.g. {{'value': 'Hello World'}}; got {value!r}"
                )
            value.update(**new_params)
            if self.width:
                entry_params = {"width": int(self.width - 80), **self.entry_params}
            else:
                entry_params = self.entry_params
            entry = ChatEntry(**value, **entry_params)
        else:
            value.param.update(**new_params)
            entry = value
        return entry

    def _upsert_entry(self, value: Any, entry: Optional[ChatEntry] = None) -> ChatEntry:
        """
        Replace the placeholder entry with the response or update
        the entry's value with the response.
        """
        user = self.callback_user
        avatar = self.callback_avatar
        if isinstance(value, ChatEntry):
            user = value.user
            avatar = value.avatar
        elif isinstance(value, dict):
            user = value.get("user", user)
            avatar = value.get("avatar", avatar)

        updated_entry = self._build_entry(value, user=user, avatar=avatar)
        if entry is None:
            self._replace_placeholder(updated_entry)
            return updated_entry
        entry.param.update(**updated_entry.param.values())
        return entry

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

    async def _serialize_response(self, response: Any) -> Optional[ChatEntry]:
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

    async def _handle_callback(self, entry: ChatEntry) -> Optional[ChatEntry]:
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

        start = asyncio.get_event_loop().time()
        while not task.done() and num_entries == len(self._chat_log):
            duration = asyncio.get_event_loop().time() - start
            if duration > self.placeholder_threshold:
                self._chat_log.append(self._placeholder)
                return
            await asyncio.sleep(0.05)

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
            if isawaitable(self.callback):
                task = asyncio.create_task(self._handle_callback(entry))
                await self._schedule_placeholder(task, num_entries)
                await task
                task.result()
            else:
                if self.placeholder_threshold > 0:
                    self._chat_log.append(self._placeholder)
                await self._handle_callback(entry)
        finally:
            self._replace_placeholder(None)
            self.disabled = disabled

    def _stream(self, token: str, entry: ChatEntry) -> ChatEntry:
        """
        Updates the entry with the token and handles nested
        objects by traversing the entry's value and updating the
        last panel in the column that supports strings; e.g.
        updates Markdown here: `Column(Markdown(...), Image(...))`
        """
        i = -1
        parent_panel = None
        value_panel = entry
        attr = "value"
        value = entry.value
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

    # public API

    def send(
        self,
        value: Union[ChatEntry, dict, Any],
        user: Optional[str] = None,
        avatar: Optional[Union[str, BinaryIO]] = None,
        respond: bool = True,
    ) -> ChatEntry:
        """
        Sends a value and creates a new entry in the chat log.

        If `respond` is `True`, additionally executes the callback, if provided.

        Parameters
        ----------
        value : Union[ChatEntry, dict, Any]
            The message contents to send.
        user : Optional[str]
            The user to send as; overrides the message entry's user if provided.
        avatar : Optional[Union[str, BinaryIO]]
            The avatar to use; overrides the message entry's avatar if provided.
        respond : bool
            Whether to execute the callback.

        Returns
        -------
        The entry that was created.
        """
        entry = self._build_entry(value, user=user, avatar=avatar)
        self._chat_log.append(entry)

        if respond:
            self.respond()
        return entry

    def stream(
            self,
            value: str,
            user: Optional[str] = None,
            avatar: Optional[Union[str, BinaryIO]] = None,
            entry: Optional[ChatEntry] = None,
        ) -> ChatEntry:
        """
        Streams a token and updates the provided entry, if provided.
        Otherwise creates a new entry in the chat log, so be sure the
        returned entry is passed back into the method, e.g.
        `entry = chat.stream(token, entry=entry)`.

        This method is primarily for outputs that are not generators--
        notably LangChain. For most cases, use the send method instead.

        Parameters
        ----------
        value : str
            The new token value to stream.
        user : Optional[str]
            The user to stream as; overrides the entry's user if provided.
        avatar : Optional[Union[str, BinaryIO]]
            The avatar to use; overrides the entry's avatar if provided.
        entry : Optional[ChatEntry]
            The entry to update.

        Returns
        -------
        The entry that was updated.
        """
        replace = entry is None
        entry = self._build_entry(entry or value, user=user, avatar=avatar)
        if replace:
            self._replace_placeholder(entry)
        else:
            self._stream(value, entry)
        return entry

    def respond(self):
        """
        Executes the callback with the latest entry in the chat log.
        """
        self._callback_trigger.param.trigger("clicks")

    def undo(self, count: Optional[int] = 1) -> List[Any]:
        """
        Removes the last `count` of entries from
        the chat log and returns them.

        Parameters
        ----------
        count : Optional[int]
            The number of entries to remove, starting from the last entry.

        Returns
        -------
        The entries that were removed.
        """
        if count == 0:
            return []
        entries = self._chat_log.objects
        undone_entries = entries[-count:]
        self._chat_log.objects = entries[:-count]
        return undone_entries

    def clear(self) -> List[Any]:
        """
        Clears the chat log and returns
        the entries that were cleared.

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

    widgets = param.List(doc="""
        Widgets to use for the input. If not provided, defaults to
        `[TextInput]`.""")

    user = param.String(default="User", doc="Name of the ChatInterface user.")

    avatar = param.ClassSelector(class_=(str, BinaryIO), doc="""
        The avatar to use for the user. Can be a single character text, an emoji,
        or anything supported by `pn.pane.Image`. If not set, uses the
        first character of the name.""")

    reset_on_send = param.Boolean(default=False, doc="""
        Whether to reset the widget's value after sending a message;
        has no effect for `TextInput`.""")

    show_rerun = param.Boolean(default=True, doc="""
        Whether to show the rerun button.""")

    show_undo = param.Boolean(default=True, doc="""
        Whether to show the undo button.""")

    show_clear = param.Boolean(default=True, doc="""
        Whether to show the clear button.""")

    show_button_name = param.Boolean(default=True, doc="""
        Whether to show the button name.""")

    _input_layout = param.ClassSelector(class_=Viewable, doc="""
        The input layout.""")

    _button_data = param.Dict(default={}, doc="""
        Metadata and data related to the buttons.""")

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_interface.css"
    ]

    def __init__(self, **params):
        if params.get("widgets") is None:
            params["widgets"] = [TextInput(placeholder="Send a message")]
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
        self._init_widgets()
        self._composite[:] = [*self._composite[:], self._input_layout]

    def _link_disabled_loading(self, obj: Viewable):
        """
        Link the disabled and loading attributes of the chat box to the
        given object.
        """
        for attr in ["disabled", "loading"]:
            setattr(obj, attr, getattr(self, attr))
            self.link(obj, **{attr: attr})

    @param.depends("widgets", watch=True)
    def _init_widgets(self) -> Union[Tabs, Row]:
        """
        Initialize the input widgets.

        Returns
        -------
        The input widgets.
        """
        self._widgets = {}
        for widget in self.widgets:
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
        input_layout = Tabs(sizing_mode=sizing_mode)
        for name, widget in self._widgets.items():
            # for longer form messages, like TextArea / Ace, don't
            # submit when clicking away; only if they manually click
            # the send button
            if isinstance(widget, TextInput):
                widget.param.watch(self._click_send, "value")
            widget.sizing_mode = sizing_mode

            buttons = []
            for button_data in self._button_data.values():
                name = button_data.name.title() if self.show_button_name else ""
                button = Button(
                    name=name,
                    icon=button_data.icon,
                    sizing_mode=None,
                    margin=(5, 2)
                )
                self._link_disabled_loading(button)
                action = button_data.name
                button.on_click(getattr(self, f"_click_{action}"))
                buttons.append(button)
                button_data.buttons.append(button)

            message_row = Row(widget, *buttons, sizing_mode=sizing_mode)
            input_layout.append((name, message_row))

        # if only a single input, don't use tabs
        if len(self._widgets) == 1:
            input_layout = input_layout[0]
        self._input_layout = input_layout

    def _click_send(self, _: Optional[param.parameterized.Event] = None) -> None:
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
            if isinstance(active_widget, TextInput) or self.reset_on_send:
                if hasattr(active_widget, "value_input"):
                    active_widget.value_input = ""
                active_widget.value = ""
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
                button.button_type = "warning"
                button.name = f"Revert {button.name}"
            else:
                button.button_type = "default"
                button.name = button.name.replace("Revert ", "")

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
            active = self._input_layout.active
            return self._input_layout[active].objects[0]
        else:
            return self._input_layout.objects[0]

    @property
    def active_tab(self) -> int:
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
        else:
            return -1

    @active_tab.setter
    def active_tab(self, tab: int) -> None:
        """
        Set the active input widget tab index.

        Parameters
        ----------
        tab : int
            The tab index to set.
        """
        if isinstance(self._input_layout, Tabs):
            self._input_layout.active = tab
