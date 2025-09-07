"""
The feed module provides a high-level API for interacting
with a list of `ChatMessage` objects through the backend methods.
"""

from __future__ import annotations

import asyncio
import traceback

from collections.abc import Callable
from enum import Enum
from functools import partial
from inspect import (
    getfullargspec, isasyncgen, isasyncgenfunction, isawaitable,
    iscoroutinefunction, isgenerator, isgeneratorfunction, ismethod,
)
from io import BytesIO
from typing import (
    TYPE_CHECKING, Any, ClassVar, Literal,
)

import param

from .._param import Margin
from ..io.resources import CDN_DIST
from ..layout import (
    Column, Feed, ListPanel, WidgetBox,
)
from ..layout.card import Card
from ..pane.image import SVG, ImageBase
from ..pane.markup import HTML, Markdown
from ..util import to_async_gen
from ..viewable import Children, Viewable
from ..widgets import Widget
from ..widgets.button import Button
from ._param import CallbackException
from .icon import ChatReactionIcons
from .message import ChatMessage
from .step import ChatStep

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


PLACEHOLDER_SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-loader-3" width="35" height="35" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M3 12a9 9 0 0 0 9 9a9 9 0 0 0 9 -9a9 9 0 0 0 -9 -9"></path>
        <path d="M17 12a5 5 0 1 0 -5 5"></path>
    </svg>
"""  # noqa: E501


class CallbackState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    GENERATING = "generating"
    STOPPING = "stopping"
    STOPPED = "stopped"


class StopCallback(Exception):
    pass


def _stretches_height(obj: Viewable) -> param.rx:
    return obj.param.sizing_mode.rx().rx.pipe(
        lambda sm: 'max' if sm is not None and ('height' in sm or 'both' in sm) else 'auto'
    )


class ChatFeed(ListPanel):
    """
    A ChatFeed holds a list of `ChatMessage` objects and provides convenient APIs.
    to interact with them.

    This includes methods to:
    - Send (append) messages to the chat log.
    - Stream tokens to the latest `ChatMessage` in the chat log.
    - Execute callbacks when a user sends a message.
    - Undo a number of sent `ChatMessage` objects.
    - Clear the chat log of all `ChatMessage` objects.

    Reference: https://panel.holoviz.org/reference/chat/ChatFeed.html

    :Example:

    >>> async def say_welcome(contents, user, instance):
    >>>    yield "Welcome!"
    >>>    yield "Glad you're here!"

    >>> chat_feed = ChatFeed(callback=say_welcome, header="Welcome Feed")
    >>> chat_feed.send("Hello World!", user="New User", avatar="😊")
    """

    adaptive = param.Boolean(default=False, doc="""
        Whether to allow interrupting and restarting the callback when
        new messages are sent while a callback is already running.
        When True, sending a new message will cancel the current callback
        and start a new one with the latest message.""")

    auto_scroll_limit = param.Integer(default=200, bounds=(0, None), doc="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""")

    callback = param.Callable(allow_refs=False, doc="""
        Callback to execute when a user sends a message or
        when `respond` is called. The signature must include
        the previous message value `contents`, the previous `user` name,
        and the component `instance`.""")

    callback_exception = CallbackException(
        default="summary", allow_refs=False, doc="""
        How to handle exceptions raised by the callback.
        If "raise", the exception will be raised.
        If "summary", a summary will be sent to the chat feed.
        If "verbose" or "traceback", the full traceback will be sent to the chat feed.
        If "ignore", the exception will be ignored.
        If a callable is provided, the signature must contain the
        `exception` and `instance` arguments and it
        will be called with the exception.
        """)

    callback_user = param.String(default="Assistant", doc="""
        The default user name to use for the message provided by the callback.""")

    callback_avatar = param.ClassSelector(class_=(str, BytesIO, bytes, ImageBase), doc="""
        The default avatar to use for the entry provided by the callback.
        Takes precedence over `ChatMessage.default_avatars` if set; else, if None,
        defaults to the avatar set in `ChatMessage.default_avatars` if matching key exists.
        Otherwise defaults to the first character of the `callback_user`.""")

    edit_callback = param.Callable(allow_refs=False, doc="""
        Callback to execute when a user edits a message.
        The signature must include the new message value `contents`,
        the `message_index`, and the `instance`.""")

    card_params = param.Dict(default={}, doc="""
        Params to pass to Card, like `header`, `header_background`, `header_color`, etc.""")

    collapsible = param.Boolean(default=False, readonly=True, doc="""
        Whether the Card should be expandable and collapsible.""")

    disabled = param.Boolean(default=False, doc="""
       Whether the feed is disabled.""")

    message_params = param.Dict(default={}, doc="""
        Params to pass to each ChatMessage, like `reaction_icons`, `timestamp_format`,
        `show_avatar`, `show_user`, and `show_timestamp`. Params passed
        that are not ChatFeed params will be forwarded into `message_params`.""")

    header = param.Parameter(doc="""
        The header of the chat feed; commonly used for the title.
        Can be a string, pane, or widget.""")

    margin = Margin(default=5, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    objects = Children(default=[], doc="""
        The list of child objects that make up the layout.""")

    help_text = param.String(default="", doc="""
        If provided, initializes a chat message in the chat log
        using the provided help text as the message object and
        `help` as the user. This is useful for providing instructions,
        and will not be included in the `serialize` method by default.""")

    load_buffer = param.Integer(default=50, bounds=(0, None), doc="""
        The number of objects loaded on each side of the visible objects.
        When scrolled halfway into the buffer, the feed will automatically
        load additional objects while unloading objects on the opposite side.""")

    placeholder_text = param.String(default="", doc="""
        The text to display next to the placeholder icon.""")

    placeholder_params = param.Dict(default={
        "user": " ",
        "reaction_icons": {},
        "show_copy_icon": False,
        "show_timestamp": False,
        "show_edit_icon": False
    }, doc="""
        Params to pass to the placeholder ChatMessage, like `reaction_icons`,
        `timestamp_format`, `show_avatar`, `show_user`, `show_timestamp`.
        """
    )

    placeholder_threshold = param.Number(default=1, bounds=(0, None), doc="""
        Min duration in seconds of buffering before displaying the placeholder.
        If 0, the placeholder will be disabled.""")

    post_hook = param.Callable(allow_refs=False, doc="""
        A hook to execute after a new message is *completely* added,
        i.e. the generator is exhausted. The `stream` method will trigger
        this callback on every call. The signature must include the
        `message` and `instance` arguments.""")

    renderers = param.HookList(doc="""
        A callable or list of callables that accept the value and return a
        Panel object to render the value. If a list is provided, will
        attempt to use the first renderer that does not raise an
        exception. If None, will attempt to infer the renderer
        from the value.""")

    scroll_button_threshold = param.Integer(default=100, bounds=(0, None),doc="""
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.""")

    show_activity_dot = param.Boolean(default=True, doc="""
        Whether to show an activity dot on the ChatMessage while
        streaming the callback response.""")

    view_latest = param.Boolean(default=True, doc="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""")

    _placeholder = param.ClassSelector(class_=ChatMessage, allow_refs=False, doc="""
        The placeholder wrapped in a ChatMessage object;
        primarily to prevent recursion error in _update_placeholder.""")

    _callback_state = param.Selector(objects=list(CallbackState), doc="""
        The current state of the callback.""")

    _prompt_trigger = param.Event(doc="Triggers the prompt input.")

    _callback_trigger = param.Event(doc="Triggers the callback to respond.")

    _disabled_stack = param.List(doc="""
        The previous disabled state of the feed.""")

    _card_type: ClassVar[type[Card]] = Card
    _message_type: ClassVar[type[ChatMessage]] = ChatMessage
    _step_type: ClassVar[type[ChatStep]] = ChatStep

    _stylesheets: ClassVar[list[str]] = [f"{CDN_DIST}css/chat_feed.css"]

    def __init__(self, *objects, **params):
        # Task management for proper cancellation
        self._callback_ids = set()
        self._callback_future = None
        self._callback_task = None
        self._current_callback_id = None

        if params.get("renderers") and not isinstance(params["renderers"], list):
            params["renderers"] = [params["renderers"]]
        if params.get("width") is None and params.get("sizing_mode") is None:
            params["sizing_mode"] = "stretch_width"

        # forward message params to ChatMessage for convenience
        message_params = params.get("message_params", {})
        for param_key in params.copy():
            if param_key not in self.param and param_key in self._message_type.param:
                message_params[param_key] = params.pop(param_key)
        params["message_params"] = message_params

        super().__init__(*objects, **params)

        if self.help_text:
            self.objects = [
                self._message_type(
                    self.help_text,
                    user="Help",
                    show_edit_icon=False,
                    show_copy_icon=False,
                    show_reaction_icons=False,
                    **message_params
                ), *self.objects
            ]

        # instantiate the card's column
        linked_params = dict(
            design=self.param.design,
            sizing_mode=self.param.sizing_mode,
            width=self.param.width,
            max_width=self.param.max_width,
            min_width=self.param.min_width,
            visible=self.param.visible,
        )
        # we separate out chat log for the auto scroll feature
        self._chat_log = Feed(
            *self.objects,
            load_buffer=self.load_buffer,
            auto_scroll_limit=self.auto_scroll_limit,
            scroll_button_threshold=self.scroll_button_threshold,
            height=None,
            view_latest=self.view_latest,
            css_classes=["chat-feed-log"],
            stylesheets=self._stylesheets,
            height_policy=_stretches_height(self),
            **linked_params
        )
        card_params = linked_params.copy()
        card_stylesheets = (
            self._stylesheets +
            self.param.stylesheets.rx() +
            self.param.card_params.rx().get('stylesheets', [])
        )
        card_params.update(
            align=self.param.align,
            collapsible=False,
            css_classes=["chat-feed"] + self.param.css_classes.rx(),
            header=self.header,
            header_css_classes=["chat-feed-header"],
            height=self.param.height,
            hide_header=self.param.header.rx().rx.in_((None, "")),
            margin=self.param.margin,
            max_height=self.param.max_height,
            min_height=self.param.min_height,
            styles={"padding": "0px"},
            stylesheets=card_stylesheets,
            title_css_classes=["chat-feed-title"],
        )
        card_overrides = self.card_params.copy()
        card_overrides.pop('stylesheets', None)
        card_params.update(card_overrides)
        self.link(self._chat_log, objects='objects', bidirectional=True)
        # we have a card for the title
        self._card = self._card_type(
            self._chat_log,
            **card_params
        )
        self.link(self._card, header='header')

        # handle async callbacks using this trick
        self.param.watch(self._prepare_response, '_callback_trigger')

    def _is_current_task(self, callback_id: int) -> bool:
        """Check if the given task ID is the current active task."""
        return callback_id == self._current_callback_id

    def _cleanup_callback_ids(self, callback_id: int) -> None:
        """Remove messages created by a cancelled task."""
        if callback_id in self._callback_ids:
            self._callback_ids.remove(callback_id)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = self._card._get_model(doc, root, parent, comm)
        ref = (root or model).ref['id']
        self._models[ref] = (model, parent)
        return model

    def _update_model(
        self, events: dict[str, param.parameterized.Event], msg: dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None
    ) -> None:
        return

    def _cleanup(self, root: Model | None = None) -> None:
        self._card._cleanup(root)
        super()._cleanup(root)

    @param.depends("message_params", watch=True, on_init=True)
    def _validate_message_params(self):
        reaction_icons = self.message_params.get("reaction_icons")
        if isinstance(reaction_icons, ChatReactionIcons):
            raise ValueError(
                "Cannot pass a ChatReactionIcons instance to message_params; "
                "use a dict of the options instead."
            )

    @param.depends("load_buffer", "auto_scroll_limit", "scroll_button_threshold", watch=True)
    def _update_chat_log_params(self):
        self._chat_log.load_buffer = self.load_buffer
        self._chat_log.auto_scroll_limit = self.auto_scroll_limit
        self._chat_log.scroll_button_threshold = self.scroll_button_threshold

    @param.depends("card_params", watch=True)
    def _update_card_params(self):
        card_params = self.card_params.copy()
        card_params.pop('stylesheets', None)
        self._card.param.update(**card_params)

    @param.depends("placeholder_text", "placeholder_params", watch=True, on_init=True)
    def _update_placeholder(self):
        loading_avatar = SVG(
            PLACEHOLDER_SVG, sizing_mode="fixed", width=35, height=35,
            css_classes=["rotating-placeholder"]
        )
        self._placeholder = self._message_type(
            self.placeholder_text,
            avatar=loading_avatar,
            css_classes=["message"],
            **self.placeholder_params
        )

    @param.depends("loading", watch=True, on_init=True)
    def _show_placeholder(self):
        if self.loading:
            self.append(self._placeholder)
        else:
            self._replace_placeholder(None)

    def _replace_placeholder(self, message: ChatMessage | None = None) -> None:
        """
        Replace the placeholder from the chat log with the message
        if placeholder, otherwise simply append the message.
        Replacing helps lessen the chat log jumping around.
        """
        with param.parameterized.batch_call_watchers(self):
            if message is not None:
                self.append(message)

            try:
                if self.loading:
                    return
                self.remove(self._placeholder)
            except ValueError:
                pass

    async def _on_edit_message(self, event):
        if self.edit_callback is None:
            return
        message = event.obj
        contents = message.serialize()
        index = self._chat_log.index(message)
        if iscoroutinefunction(self.edit_callback):
            await self.edit_callback(contents, index, self)
        else:
            self.edit_callback(contents, index, self)

    def _build_message(
        self,
        value: dict,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
        **input_message_params
    ) -> ChatMessage | None:
        """
        Builds a ChatMessage from the value.
        """
        if "value" in value and "object" in value:
            raise ValueError(f"Cannot pass both 'value' and 'object' together; got {value!r}")
        elif "value" in value:
            value["object"] = value.pop("value")
        elif "object" not in value:
            raise ValueError(
                f"If 'value' is a dict, it must contain an 'object' key, "
                f"e.g. {{'object': 'Hello World'}}; got {value!r}"
            )
        message_params = dict(value, renderers=self.renderers, **self.message_params)
        if user:
            message_params["user"] = user
        if avatar:
            message_params["avatar"] = avatar
        if self.width:
            message_params["width"] = int(self.width - 80)
        message_params.update(input_message_params)

        if "show_edit_icon" not in message_params:
            user = message_params.get("user", "")
            message_params["show_edit_icon"] = (
                bool(self.edit_callback) and
                (isinstance(user, str) and user.lower() not in (self.callback_user.lower(), "help"))
            )

        message = self._message_type(**message_params)
        message.param.watch(self._on_edit_message, "edited")
        return message

    def _upsert_message(
        self, value: Any, message: ChatMessage | None = None, callback_id: int | None = None
    ) -> ChatMessage | None:
        """
        Replace the placeholder message with the response or update
        the message's value with the response.

        Now includes task tracking to prevent orphaned callbacks from adding messages.
        """
        # Check if this task has been cancelled/replaced
        if callback_id is not None and not self._is_current_task(callback_id):
            raise StopCallback(f"Task {callback_id} was cancelled.")

        is_stopping = self._callback_state == CallbackState.STOPPING
        is_stopped = self._callback_future is not None and self._callback_future.cancelled()
        if value is None:
            # don't add new message if the callback returns None
            return None
        elif is_stopping or is_stopped:
            raise StopCallback("Callback was stopped.")

        user = self.callback_user
        avatar = self.callback_avatar
        if isinstance(value, dict):
            user = value.get("user", user)
            avatar = value.get("avatar", avatar)

        if message is not None:
            # ChatMessage is already created; updating existing ChatMessage
            if isinstance(value, ChatMessage):
                # Cannot set user or avatar when explicitly sending
                # a ChatMessage; need to set them directly on the ChatMessage.
                user = value.user
                avatar = value.avatar
                value = value.object
            message.update(value, user=user, avatar=avatar)
            return message
        elif isinstance(value, ChatMessage):
            # ChatMessage is not created yet, but a ChatMessage is passed; use it
            self._replace_placeholder(value)
            return value

        # ChatMessage is not created yet, create a ChatMessage from string/dict
        if not isinstance(value, dict):
            value = {"object": value}
        new_message = self._build_message(value, user=user, avatar=avatar)
        self._replace_placeholder(new_message)
        return new_message

    def _gather_callback_args(self, message: ChatMessage) -> Any:
        """
        Extracts the contents from the message's panel object.
        """
        value = message._object_panel
        if hasattr(value, "object"):
            contents = value.object
        elif hasattr(value, "objects"):
            contents = value.objects
        elif hasattr(value, "value"):
            contents = value.value
        else:
            contents = value

        input_kwargs = {
            "contents": contents,
            "user": message.user,
            "instance": self
        }
        input_args = tuple(input_kwargs.values())
        callback_arg_spec = getfullargspec(self.callback)
        callback_args = callback_arg_spec.args
        if ismethod(self.callback):
            callback_args = callback_args[1:]
        num_args = len(callback_args)
        if callback_arg_spec.varargs:
            return input_args, {}
        elif callback_arg_spec.varkw:
            args_keys = list(input_kwargs)[:num_args]
            for arg_key in args_keys:
                input_kwargs.pop(arg_key)
            return input_args[:num_args], input_kwargs
        elif len(callback_args) <= 3:
            return input_args[:num_args], {}
        elif len(callback_args) > 3:
            raise ValueError("Function should have at most 3 arguments")
        elif len(callback_args) == 0:
            raise ValueError("Function should have at least one argument")

    async def _serialize_response(self, response: Any, callback_id: int) -> ChatMessage | None:
        """
        Serializes the response by iterating over it and
        updating the message's value.
        """
        response_message = None
        try:
            if isasyncgen(response):
                self._callback_state = CallbackState.GENERATING
                async for token in response:
                    # Check if task is still current before processing
                    if not self._is_current_task(callback_id):
                        raise StopCallback(f"Task {callback_id} was cancelled.")
                    response_message = self._upsert_message(token, response_message, callback_id)
                    if response_message is not None:
                        response_message.show_activity_dot = self.show_activity_dot
            elif isgenerator(response):
                self._callback_state = CallbackState.GENERATING
                for token in response:
                    # Check if task is still current before processing
                    if not self._is_current_task(callback_id):
                        raise StopCallback(f"Task {callback_id} was cancelled.")
                    response_message = self._upsert_message(token, response_message, callback_id)
                    if response_message is not None:
                        response_message.show_activity_dot = self.show_activity_dot
            elif isawaitable(response):
                response_message = self._upsert_message(await response, response_message, callback_id)
            else:
                response_message = self._upsert_message(response, response_message, callback_id)
            if response_message is not None:
                self._run_post_hook(response_message)
        finally:
            if response_message:
                response_message.show_activity_dot = False
        return response_message

    async def _schedule_placeholder(
        self,
        task: asyncio.Task,
        num_entries: int,
        callback_id: int
    ) -> None:
        """
        Schedules the placeholder to be added to the chat log
        if the callback takes longer than the placeholder threshold.
        """
        if self.placeholder_threshold == 0:
            return

        start = asyncio.get_event_loop().time()
        while not task.done() and num_entries == len(self._chat_log) and self._is_current_task(callback_id):
            duration = asyncio.get_event_loop().time() - start
            if duration > self.placeholder_threshold:
                if self._is_current_task(callback_id):  # Double-check before adding placeholder
                    self.append(self._placeholder)
                return
            await asyncio.sleep(0.1)

    async def _handle_callback(self, message, loop: asyncio.AbstractEventLoop, callback_id: int):
        """Handle the callback execution with task tracking."""
        callback_args, callback_kwargs = self._gather_callback_args(message)
        if iscoroutinefunction(self.callback):
            response = await self.callback(*callback_args, **callback_kwargs)
        elif isasyncgenfunction(self.callback):
            response = self.callback(*callback_args, **callback_kwargs)
        elif isgeneratorfunction(self.callback):
            response = to_async_gen(self.callback(*callback_args, **callback_kwargs))
            # printing type(response) -> <class 'async_generator'>
        else:
            response = await asyncio.to_thread(self.callback, *callback_args, **callback_kwargs)
        await self._serialize_response(response, callback_id)
        self._callback_ids = set()
        self._callback_state = CallbackState.IDLE
        return response

    async def _prepare_response(self, *_) -> None:
        """
        Prepares the response by scheduling the placeholder and
        executing the callback.

        Improved with proper task cancellation and cleanup.
        """
        if self.callback is None:
            return

        self._disabled_stack.append(self.disabled)
        old_callback_id = self._current_callback_id
        callback_id = (self._current_callback_id or 0) + 1
        self._callback_ids.add(callback_id)
        self._current_callback_id = callback_id
        # Cancel any existing callback task if in adaptive mode
        if self.adaptive and self._callback_task is not None and not self._callback_task.done():
            self._callback_task.cancel()
            try:
                await self._callback_task
            except asyncio.CancelledError:
                pass  # Expected when cancelling

            # Clean up messages from the cancelled task
            if old_callback_id is not None:
                self._cleanup_callback_ids(old_callback_id)

        try:
            with param.parameterized.batch_call_watchers(self):
                self.disabled = True
                self._callback_state = CallbackState.RUNNING

            message = self._chat_log[-1]
            if not isinstance(message, ChatMessage):
                return

            num_entries = len(self._chat_log)
            loop = asyncio.get_event_loop()
            task = loop.create_task(self._handle_callback(message, loop, callback_id))
            self._callback_task = task
            self._callback_future = task

            await asyncio.gather(
                self._schedule_placeholder(task, num_entries, callback_id), task,
            )
        except (StopCallback, asyncio.CancelledError):
            self._cleanup_callback_ids(callback_id)
            if not self.adaptive or len(self._callback_ids) == 0:
                self._callback_state = CallbackState.STOPPED
        except Exception as e:
            send_kwargs: dict[str, Any] = dict(user="Exception", respond=False)
            if callable(self.callback_exception):
                if iscoroutinefunction(self.callback_exception):
                    await self.callback_exception(e, self)
                else:
                    self.callback_exception(e, self)
            elif self.callback_exception == "summary":
                self.send(
                    f"Encountered `{e!r}`. "
                    f"Set `callback_exception='verbose'` to see the full traceback.",
                    **send_kwargs
                )
            elif self.callback_exception in ("verbose", "traceback"):
                self.send(f"```python\n{traceback.format_exc()}\n```", **send_kwargs)
            elif self.callback_exception == "ignore":
                return
            else:
                raise e
        finally:
            await self._cleanup_response()

    async def _cleanup_response(self):
        """
        Events to always execute after the callback is done.
        """
        with param.parameterized.batch_call_watchers(self):
            self._replace_placeholder(None)
            # In adaptive mode, only reset to idle if we're not already starting a new callback
            if not (self.adaptive and self._callback_state in (CallbackState.RUNNING, CallbackState.GENERATING, CallbackState.STOPPING)):
                self._callback_state = CallbackState.IDLE
                self.disabled = self._disabled_stack.pop() if self._disabled_stack else False

    # Public API
    def scroll_to(self, index: int):
        """
        Scrolls the chat log to the provided index.

        Arguments
        ---------
        index : int
            The index to scroll to.
        """
        self._chat_log.scroll_to(index)

    def send(
        self,
        value: ChatMessage | dict | Any,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
        respond: bool = True,
        trigger_post_hook: bool = True,
        **message_params
    ) -> ChatMessage | None:
        """
        Sends a value and creates a new message in the chat log.

        If `respond` is `True`, additionally executes the callback, if provided.

        Parameters
        ----------
        value : ChatMessage | dict | Any
            The message contents to send.
        user : str | None
            The user to send as; overrides the message message's user if provided.
        avatar : str | bytes | BytesIO | None
            The avatar to use; overrides the message message's avatar if provided.
        respond : bool
            Whether to execute the callback.
        trigger_post_hook: bool
            Whether to trigger the post hook after sending.
        message_params : dict
            Additional parameters to pass to the ChatMessage.

        Returns
        -------
        The message that was created.
        """
        if (self.adaptive and respond and self.callback is not None and
            self._callback_state in (CallbackState.RUNNING, CallbackState.GENERATING)):
            self.stop()

        if isinstance(value, ChatMessage):
            if user is not None or avatar is not None:
                raise ValueError(
                    "Cannot set user or avatar when explicitly sending "
                    "a ChatMessage. Set them directly on the ChatMessage."
                )
            message: ChatMessage | None = value
        else:
            if not isinstance(value, dict):
                value = {"object": value}
            message = self._build_message(value, user=user, avatar=avatar, **message_params)
        self.append(message)
        if trigger_post_hook:
            self._run_post_hook(message)
        if respond:
            self.respond()
        return message

    def stream(
        self,
        value: str | dict | ChatMessage,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
        message: ChatMessage | None = None,
        replace: bool = False,
        trigger_post_hook: bool = False,
        **message_params
    ) -> ChatMessage | None:
        """
        Streams a token and updates the provided message, if provided.
        Otherwise creates a new message in the chat log, so be sure the
        returned message is passed back into the method, e.g.
        `message = chat.stream(token, message=message)`.

        This method is primarily for outputs that are not generators--
        notably LangChain. For most cases, use the send method instead.

        Parameters
        ----------
        value : str | dict | ChatMessage
            The new token value to stream.
        user : str | None
            The user to stream as; overrides the message's user if provided.
        avatar : str | bytes | BytesIO | None
            The avatar to use; overrides the message's avatar if provided.
        message : ChatMessage | None
            The message to update.
        replace : bool
            Whether to replace the existing text when streaming a string or dict.
        trigger_post_hook: bool
            Whether to trigger the post hook after streaming.
        message_params : dict
            Additional parameters to pass to the ChatMessage.

        Returns
        -------
        The message that was updated.
        """
        if self._callback_future is not None and self._callback_future.cancelled():
            raise StopCallback("Callback was stopped.")

        if isinstance(value, ChatMessage) and (user is not None or avatar is not None):
            raise ValueError(
                "Cannot set user or avatar when explicitly streaming "
                "a ChatMessage. Set them directly on the ChatMessage."
            )
        elif message:
            if isinstance(value, str):
                message.stream(value, replace=replace)
                if user:
                    message.user = user
                if avatar:
                    message.avatar = avatar
            else:
                message.update(value, user=user, avatar=avatar)

            if message_params:
                message.param.update(**message_params)
            self._chat_log.scroll_to_latest(scroll_limit=self.auto_scroll_limit)
            if trigger_post_hook:
                self._run_post_hook(message)
            return message

        if isinstance(value, ChatMessage):
            message = value
        else:
            if not isinstance(value, dict):
                value = {"object": value}
            message = self._build_message(value, user=user, avatar=avatar, **message_params)
        self._replace_placeholder(message)
        self._chat_log.scroll_to_latest(scroll_limit=self.auto_scroll_limit)
        if trigger_post_hook:
            self._run_post_hook(message)
        return message

    def _match_step_status(self, event):
        """
        Matches the status of the ChatStep with the ChatFeed.
        """
        if event.new in ("running", "pending"):
            self._callback_state = CallbackState.RUNNING
        elif event.new in ("failed", "success"):
            self._callback_state = CallbackState.IDLE
            self._run_post_hook(event.obj)

    def _build_steps_layout(self, step, layout_params, default_layout):
        layout_params = layout_params or {}
        input_layout_params = dict(
            min_width=100,
            styles={
                "margin-inline": "10px",
            },
            css_classes=["chat-steps"],
            stylesheets=[f"{CDN_DIST}css/chat_steps.css"]
        )
        if default_layout == "column":
            layout = Column
        elif default_layout == "card":
            layout = self._card_type
            input_layout_params["header_css_classes"] = ["card-header"]
            title = layout_params.pop("title", None)
            input_layout_params["header"] = HTML(
                title or "🪜 Steps",
                css_classes=["card-title"],
                stylesheets=[f"{CDN_DIST}css/chat_steps.css"]
            )
        else:
            raise ValueError(
                f"Invalid default_layout {default_layout!r}; "
                f"expected 'column' or 'card'."
            )
        if layout_params:
            input_layout_params.update(layout_params)
        return layout(step, **input_layout_params)

    def add_step(
        self,
        step: str | list[str] | ChatStep | None = None,
        append: bool = True,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
        steps_layout: Column | Card | None = None,
        default_layout: Literal["column", "card"] = "card",
        layout_params: dict | None = None,
        last_messages: int = 1,
        **step_params
    ) -> ChatStep:
        """
        Adds a ChatStep component either by appending it to an existing
        ChatMessage or creating a new ChatMessage.

        Parameters
        ----------
        step : str | list(str) | ChatStep | None
            The objects to stream to the step.
        append : bool
            Whether to append to existing steps or create new steps.
        user : str | None
            The user to stream as; overrides the message's user if provided.
            Will default to the user parameter. Only applicable if steps is "new".
        avatar : str | bytes | BytesIO | None
            The avatar to use; overrides the message's avatar if provided.
            Will default to the avatar parameter. Only applicable if steps is "new".
        steps_layout : Column | None
            An existing layout of steps to stream to, if None is provided
            it will default to the last Column of steps or create a new one.
        default_layout : str
            The default layout to use if steps_layout is None.
            'column' will create a new Column layout.
            'card' will create a new Card layout.
        layout_params : dict | None
            Additional parameters to pass to the layout.
        last_messages: int
            The number of messages to go back to find the last message.
        step_params : dict
            Parameters to pass to the ChatStep.
        """
        self._callback_state = CallbackState.RUNNING
        if not isinstance(step, ChatStep):
            if step is None:
                step = []
            elif not isinstance(step, list):
                step = [step]
            if "margin" not in step_params:
                step_params["margin"] = (5, 1)
            step_params["objects"] = [
                (
                    Markdown(obj, css_classes=["step-message"])
                    if isinstance(obj, str)
                    else obj
                )
                for obj in step
            ]
            if "context_exception" not in step_params:
                step_params["context_exception"] = self.callback_exception
            step = self._step_type(**step_params)

        step._instance = self
        step.param.watch(self._match_step_status, "status")

        if append:
            for i in range(1, last_messages + 1):
                if not self._chat_log:
                    break

                last = self._chat_log[-i]
                if last is not None and isinstance(last.object, Column) and (
                    all(isinstance(o, ChatStep) for o in last.object) or
                    last.object.css_classes == 'chat-steps'
                ) and (user is None or last.user == user):
                    steps_layout = last.object

        if steps_layout is None:
            steps_layout = self._build_steps_layout(step, layout_params, default_layout)
            self.stream(steps_layout, user=user or self.callback_user, avatar=avatar, trigger_post_hook=False)
        else:
            steps_layout.append(step)
            self._chat_log.scroll_to_latest(scroll_limit=self.auto_scroll_limit)
        step._layout = steps_layout
        return step

    def prompt_user(
        self,
        component: Widget | ListPanel,
        callback: Callable | None = None,
        predicate: Callable | None = None,
        timeout: int = 120,
        timeout_message: str = "Timed out",
        button_params: dict | None = None,
        timeout_button_params: dict | None = None,
        **send_kwargs
    ) -> None:
        """
        Prompts the user to interact with a form component.

        Parameters
        ----------
        component : Widget | ListPanel
            The component to prompt the user with.
        callback : Callable
            The callback to execute once the user submits the form.
            The callback should accept two arguments: the component
            and the ChatFeed instance.
        predicate : Callable | None
            A predicate to evaluate the component's state, e.g. widget has value.
            If provided, the button will be enabled when the predicate returns True.
            The predicate should accept the component as an argument.
        timeout : int
            The duration in seconds to wait before timing out.
        timeout_message : str
            The message to display when the timeout is reached.
        button_params : dict | None
            Additional parameters to pass to the submit button.
        timeout_button_params : dict | None
            Additional parameters to pass to the timeout button.
        """
        async def _prepare_prompt(*args) -> None:
            input_button_params = button_params or {}
            if "name" not in input_button_params:
                input_button_params["name"] = "Submit"
            if "margin" not in input_button_params:
                input_button_params["margin"] = (5, 10)
            if "button_type" not in input_button_params:
                input_button_params["button_type"] = "primary"
            if "icon" not in input_button_params:
                input_button_params["icon"] = "check"
            submit_button = Button(**input_button_params)

            form = WidgetBox(component, submit_button, margin=(5, 10), css_classes=["message"])
            if "user" not in send_kwargs:
                send_kwargs["user"] = "Input"
            self.send(form, respond=False, **send_kwargs)

            for _ in range(timeout * 10):  # sleeping for 0.1 seconds
                is_fulfilled = predicate(component) if predicate else True
                submit_button.disabled = not is_fulfilled
                if submit_button.clicks > 0:
                    with param.parameterized.batch_call_watchers(self):
                        submit_button.visible = False
                        form.disabled = True
                    if callback is not None:
                        result = callback(component, self)
                        if isawaitable(result):
                            await result
                    break
                await asyncio.sleep(0.1)
            else:
                input_timeout_button_params = timeout_button_params or {}
                if "name" not in input_timeout_button_params:
                    input_timeout_button_params["name"] = timeout_message
                if "button_type" not in input_timeout_button_params:
                    input_timeout_button_params["button_type"] = "light"
                if "icon" not in input_timeout_button_params:
                    input_timeout_button_params["icon"] = "x"
                with param.parameterized.batch_call_watchers(self):
                    submit_button.param.update(**input_timeout_button_params)
                    form.disabled = True

        param.parameterized.async_executor(_prepare_prompt)

    def trigger_post_hook(self):
        """
        Triggers the post hook with the latest message in the chat log.

        Typically called after streaming is completed, i.e. after a for loop where `stream` is called multiple times.
        If not streaming, use the `trigger_post_hook` keyword argument inside the `send` method instead.
        """
        message = self._chat_log.objects[-1]
        self._run_post_hook(message)

    def respond(self):
        """
        Executes the callback with the latest message in the chat log.

        Typically called after streaming is completed, i.e. after a for loop where `stream` is called multiple times.
        If not streaming, use the `respond` keyword argument inside the `send` method instead.
        """
        self.param.trigger("_callback_trigger")

    def stop(self) -> bool:
        """
        Cancels the current callback task if possible.

        Improved to properly cancel asyncio tasks.

        Returns
        -------
        Whether the task was successfully stopped or done.
        """
        if self._callback_task is None:
            cancelled = False
        elif self._callback_task.done():
            cancelled = False
        else:
            # For both generators and regular async functions, cancel the task
            cancelled = self._callback_task.cancel()
            if cancelled:
                # Mark current task as cancelled to prevent further message additions
                old_callback_id = self._current_callback_id
                self._current_callback_id = None

                # Clean up any messages from the cancelled task
                if old_callback_id is not None:
                    self._cleanup_callback_ids(old_callback_id)

        if cancelled:
            # In adaptive mode, don't restore disabled state immediately
            if not self.adaptive or self._callback_state != CallbackState.STOPPING:
                self.disabled = self._disabled_stack.pop() if self._disabled_stack else False
            self._replace_placeholder(None)
        return cancelled

    def undo(self, count: int = 1) -> list[Any]:
        """
        Removes the last `count` of messages from the chat log and returns them.

        Parameters
        ----------
        count : int
            The number of messages to remove, starting from the last message.

        Returns
        -------
        The messages that were removed.
        """
        if count <= 0:
            return []
        messages = self._chat_log.objects
        undone_entries = messages[-count:]
        self._chat_log.objects = messages[:-count]
        return undone_entries

    def clear(self) -> list[Any]:
        """
        Clears the chat log and returns the messages that were cleared.

        Returns
        -------
        The messages that were cleared.
        """
        cleared_entries = self._chat_log.objects
        self._chat_log.clear()
        return cleared_entries

    def _serialize_for_transformers(
        self,
        messages: list[ChatMessage],
        role_names: dict[str, str | list[str]] | None = None,
        default_role: str = "assistant",
        custom_serializer: Callable | None = None,
        **serialize_kwargs
    ) -> list[dict[str, Any]]:
        """
        Exports the chat log for use with transformers.
        """
        if role_names is None:
            role_names = {
                "user": ["user"],
                "assistant": [self.callback_user],
            }

        names_role = {}
        for role, names in role_names.items():
            # reverse the role_names dict and pd.explode list of names
            # as keys for efficient look up
            if isinstance(names, str):
                names = [names]
            for name in names:
                names_role[name.lower()] = role

        serialized_messages = []
        for message in messages:

            lowercase_name = message.user.lower()
            if lowercase_name not in names_role and not default_role:
                raise ValueError(
                    f"User {message.user!r} not found in role_names; "
                    f"got {role_names!r}."
                )

            role = names_role.get(lowercase_name, default_role)

            if custom_serializer:
                content = custom_serializer(message.object)
                if not isinstance(content, str):
                    raise ValueError(
                        f"The provided custom_serializer must return a string; "
                        f"it returned a {type(content)} type"
                    )
            else:
                content = message.serialize(**serialize_kwargs)

            serialized_messages.append({"role": role, "content": content})
        return serialized_messages

    def _run_post_hook(self, message: ChatMessage | ChatStep | None):
        """
        Runs the post hook callback, only if idle or stopped.
        """
        if self.post_hook is None:
            return

        if isinstance(message, ChatStep):
            for obj in self._chat_log.objects[::-1]:
                if obj.object is message._layout:
                    message = obj
                    break
            else:
                raise ValueError("Could not find the ChatStep layout in the chat log.")

        if iscoroutinefunction(self.post_hook):
            param.parameterized.async_executor(partial(self.post_hook, message, self))
        else:
            self.post_hook(message, self)

    def serialize(
        self,
        exclude_users: list[str] | None = None,
        filter_by: Callable | None = None,
        format: Literal["transformers"] = "transformers",
        custom_serializer: Callable | None = None,
        limit: int | None = None,
        **serialize_kwargs
    ):
        """
        Exports the chat log.

        Parameters
        ----------
        format : str
            The format to export the chat log as; currently only
            supports "transformers".
        exclude_users : list(str) | None
            A list of user (case insensitive names) to exclude from serialization.
            If not provided, defaults to ["help"]. This will be executed before `filter_by`.
        filter_by : callable
            A function to filter the chat log by.
            The function must accept and return a list of ChatMessage objects.
        custom_serializer : callable
            A custom function to format the ChatMessage's object. The function must
            accept one positional argument, the ChatMessage object, and return a string.
            If not provided, uses the serialize method on ChatMessage.
        limit : int
            The number of messages to serialize at most, starting from the last message.
        **serialize_kwargs
            Additional keyword arguments to use for the specified format.

            - format="transformers"
              role_names : dict(str, str | list(str)) | None
                  A dictionary mapping the role to the ChatMessage's user name.
                  Defaults to `{"user": ["user"], "assistant": [self.callback_user]}`
                  if not set. The keys and values are case insensitive as the strings
                  will all be lowercased. The values can be a string or a list of strings,
                  e.g. `{"user": "user", "assistant": ["executor", "langchain"]}`.
              default_role : str
                  The default role to use if the user name is not found in role_names.
                  If this is set to None, raises a ValueError if the user name is not found.

        Returns
        -------
        The chat log serialized in the specified format.
        """
        if exclude_users is None:
            exclude_users = ["help"]
        else:
            exclude_users = [user.lower() for user in exclude_users]

        objects = self._chat_log.objects
        if limit is not None:
            objects = objects[-limit:]
        messages = [
            message for message in objects
            if message.user.lower() not in exclude_users
            and message is not self._placeholder
        ]

        if filter_by is not None:
            messages = filter_by(messages)

        if format == "transformers":
            return self._serialize_for_transformers(
                messages, custom_serializer=custom_serializer, **serialize_kwargs
            )
        raise NotImplementedError(f"Format {format!r} is not supported.")

    def select(self, selector=None):
        """
        Iterates over the ChatInterface and any potential children in the
        applying the selector.

        Parameters
        ----------
        selector: type or callable or None
          The selector allows selecting a subset of Viewables by
          declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        selected = []
        if (selector is None or
            (isinstance(selector, type) and isinstance(self, selector)) or
            (callable(selector) and not isinstance(selector, type) and selector(self))):
            selected.append(self)
        return selected + self._card.select(selector)
