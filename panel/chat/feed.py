"""
The feed module provides a high-level API for interacting
with a list of `ChatEntry` objects through the backend methods.
"""

from __future__ import annotations

import asyncio
import traceback

from inspect import (
    isasyncgen, isasyncgenfunction, isawaitable, isgenerator,
)
from io import BytesIO
from typing import (
    Any, BinaryIO, ClassVar, Dict, List, Type, Union,
)

import param

from .._param import Margin
from ..io.resources import CDN_DIST
from ..layout import Column, ListPanel
from ..layout.card import Card
from ..layout.spacer import VSpacer
from ..pane.image import SVG, ImageBase
from ..widgets.base import CompositeWidget
from ..widgets.button import Button
from .entry import ChatEntry

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


class ChatFeed(CompositeWidget):
    """
    A widget to display a list of `ChatEntry` objects and interact with them.

    This widget provides methods to:
    - Send (append) messages to the chat log.
    - Stream tokens to the latest `ChatEntry` in the chat log.
    - Execute callbacks when a user sends a message.
    - Undo a number of sent `ChatEntry` objects.
    - Clear the chat log of all `ChatEntry` objects.

    Reference: https://panel.holoviz.org/reference/chat/ChatFeed.html

    :Example:

    >>> async def say_welcome(contents, user, instance):
    >>>    yield "Welcome!"
    >>>    yield "Glad you're here!"

    >>> chat_feed = ChatFeed(callback=say_welcome, header="Welcome Feed")
    >>> chat_feed.send("Hello World!", user="New User", avatar="😊")
    """

    callback = param.Callable(
        allow_refs=False,
        doc="""
        Callback to execute when a user sends a message or
        when `respond` is called. The signature must include
        the previous message value `contents`, the previous `user` name,
        and the component `instance`.""",
    )

    callback_exception = param.ObjectSelector(
        default="summary",
        objects=["raise", "summary", "verbose", "ignore"],
        doc="""
        How to handle exceptions raised by the callback.
        If "raise", the exception will be raised.
        If "summary", a summary will be sent to the chat feed.
        If "verbose", the full traceback will be sent to the chat feed.
        If "ignore", the exception will be ignored.
        """,
    )

    callback_user = param.String(
        default="Assistant",
        doc="""
        The default user name to use for the entry provided by the callback.""",
    )

    card_params = param.Dict(
        default={},
        doc="""
        Params to pass to Card, like `header`,
        `header_background`, `header_color`, etc.""",
    )

    entry_params = param.Dict(
        default={},
        doc="""
        Params to pass to each ChatEntry, like `reaction_icons`, `timestamp_format`,
        `show_avatar`, `show_user`, and `show_timestamp`.""",
    )

    header = param.Parameter(
        doc="""
        The header of the chat feed; commonly used for the title.
        Can be a string, pane, or widget."""
    )

    margin = Margin(
        default=5,
        doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""",
    )

    renderers = param.HookList(
        doc="""
        A callable or list of callables that accept the value and return a
        Panel object to render the value. If a list is provided, will
        attempt to use the first renderer that does not raise an
        exception. If None, will attempt to infer the renderer
        from the value."""
    )

    placeholder_text = param.String(
        default="",
        doc="""
        If placeholder is the default LoadingSpinner,
        the text to display next to it.""",
    )

    placeholder_threshold = param.Number(
        default=1,
        bounds=(0, None),
        doc="""
        Min duration in seconds of buffering before displaying the placeholder.
        If 0, the placeholder will be disabled.""",
    )

    auto_scroll_limit = param.Integer(
        default=200,
        bounds=(0, None),
        doc="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""",
    )

    scroll_button_threshold = param.Integer(
        default=100,
        bounds=(0, None),
        doc="""
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.""",
    )

    view_latest = param.Boolean(
        default=True,
        doc="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""",
    )
    value = param.List(
        item_type=ChatEntry,
        doc="""
        The list of entries in the feed.""",
    )

    _placeholder = param.ClassSelector(
        class_=ChatEntry,
        allow_refs=False,
        doc="""
        The placeholder wrapped in a ChatEntry object;
        primarily to prevent recursion error in _update_placeholder.""",
    )

    _disabled = param.Boolean(
        default=False,
        doc="""
        Whether the chat feed is disabled.""",
    )

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_feed.css"]

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
            "styles": {
                "border": "1px solid var(--panel-border-color, #e1e1e1)",
                "padding": "0px",
            },
            "stylesheets": self._stylesheets,
        }
        card_params.update(**self.card_params)
        if self.sizing_mode is None:
            card_params["height"] = card_params.get("height", 500)
        self._composite.param.update(**card_params)

        # instantiate the card's column
        chat_log_params = {
            p: getattr(self, p)
            for p in Column.param
            if (p in ChatFeed.param and p != "name" and getattr(self, p) is not None)
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
            PLACEHOLDER_SVG, sizing_mode=None, css_classes=["rotating-placeholder"]
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
            entry_params["user"] = user
        if avatar:
            entry_params["avatar"] = avatar
        if self.width:
            entry_params["width"] = int(self.width - 80)
        entry = ChatEntry(**entry_params)
        return entry

    def _upsert_entry(
        self, value: Any, entry: ChatEntry | None = None
    ) -> ChatEntry | None:
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
            user = value.get("user", user)
            avatar = value.get("avatar")
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

        callable_is_async = asyncio.iscoroutinefunction(
            self.callback
        ) or isasyncgenfunction(self.callback)
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
            send_kwargs = dict(user="Exception", respond=False)
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
