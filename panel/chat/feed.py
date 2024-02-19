"""
The feed module provides a high-level API for interacting
with a list of `ChatMessage` objects through the backend methods.
"""

from __future__ import annotations

import asyncio
import traceback

from enum import Enum
from inspect import (
    isasyncgen, isasyncgenfunction, isawaitable, iscoroutinefunction,
    isgenerator, isgeneratorfunction,
)
from io import BytesIO
from typing import (
    TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Literal,
)

import param

from .._param import Margin
from ..io.resources import CDN_DIST
from ..layout import Column, ListPanel
from ..layout.card import Card
from ..layout.spacer import VSpacer
from ..pane.image import SVG
from ..widgets.button import Button
from .message import ChatMessage

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


PLACEHOLDER_SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-loader-3" width="40" height="40" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
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


class ChatFeed(ListPanel):
    """
    A widget to display a list of `ChatMessage` objects and interact with them.

    This widget provides methods to:
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

    auto_scroll_limit = param.Integer(default=200, bounds=(0, None), doc="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""",)

    callback = param.Callable(allow_refs=False, doc="""
        Callback to execute when a user sends a message or
        when `respond` is called. The signature must include
        the previous message value `contents`, the previous `user` name,
        and the component `instance`.""")

    callback_exception = param.ObjectSelector(
        default="summary", objects=["raise", "summary", "verbose", "ignore"], doc="""
        How to handle exceptions raised by the callback.
        If "raise", the exception will be raised.
        If "summary", a summary will be sent to the chat feed.
        If "verbose", the full traceback will be sent to the chat feed.
        If "ignore", the exception will be ignored.
        """)

    callback_user = param.String(default="Assistant", doc="""
        The default user name to use for the message provided by the callback.""")

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

    objects = param.List(default=[], doc="""
        The list of child objects that make up the layout.""")

    help_text = param.String(default="", doc="""
        If provided, initializes a chat message in the chat log
        using the provided help text as the message object and
        `help` as the user. This is useful for providing instructions,
        and will not be included in the `serialize` method by default.""")

    placeholder_text = param.String(default="", doc="""
        If placeholder is the default LoadingSpinner the text to display
        next to it.""")

    placeholder_threshold = param.Number(default=1, bounds=(0, None), doc="""
        Min duration in seconds of buffering before displaying the placeholder.
        If 0, the placeholder will be disabled.""")

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

    _callback_state = param.ObjectSelector(objects=list(CallbackState), doc="""
        The current state of the callback.""")

    _was_disabled = param.Boolean(default=False, doc="""
        The previous disabled state of the feed.""")

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_feed.css"]

    def __init__(self, *objects, **params):
        self._callback_future = None

        if params.get("renderers") and not isinstance(params["renderers"], list):
            params["renderers"] = [params["renderers"]]
        if params.get("width") is None and params.get("sizing_mode") is None:
            params["sizing_mode"] = "stretch_width"

        # forward message params to ChatMessage for convenience
        message_params = params.get("message_params", {})
        for param_key in params.copy():
            if param_key not in self.param and param_key in ChatMessage.param:
                message_params[param_key] = params.pop(param_key)
        params["message_params"] = message_params

        super().__init__(*objects, **params)

        if self.help_text:
            self.objects = [ChatMessage(self.help_text, user="Help"), *self.objects]

        # instantiate the card's column
        linked_params = dict(
            design=self.param.design,
            sizing_mode=self.param.sizing_mode,
            width=self.param.width,
            max_width=self.param.max_width,
            min_width=self.param.min_width,
            visible=self.param.visible
        )
        # we separate out chat log for the auto scroll feature
        self._chat_log = Column(
            *self.objects,
            auto_scroll_limit=self.auto_scroll_limit,
            scroll_button_threshold=self.scroll_button_threshold,
            css_classes=["chat-feed-log"],
            stylesheets=self._stylesheets,
            **linked_params
        )
        card_params = linked_params.copy()
        card_stylesheets = (
            self._stylesheets +
            self.param.stylesheets.rx() +
            self.param.card_params.rx().get('stylesheets', [])
        )
        card_params.update(
            margin=self.param.margin,
            align=self.param.align,
            header=self.header,
            height=self.param.height,
            hide_header=self.param.header.rx().rx.in_((None, "")),
            collapsible=False,
            css_classes=["chat-feed"] + self.param.css_classes.rx(),
            header_css_classes=["chat-feed-header"],
            max_height=self.param.max_height,
            min_height=self.param.min_height,
            title_css_classes=["chat-feed-title"],
            styles={"padding": "0px"},
            stylesheets=card_stylesheets
        )
        card_overrides = self.card_params.copy()
        card_overrides.pop('stylesheets', None)
        card_params.update(card_overrides)
        self.link(self._chat_log, objects='objects', bidirectional=True)
        # we have a card for the title
        self._card = Card(
            self._chat_log,
            VSpacer(),
            **card_params
        )

        # handle async callbacks using this trick
        self._callback_trigger = Button(visible=False)
        self._callback_trigger.on_click(self._prepare_response)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = self._card._get_model(doc, root, parent, comm)
        ref = (root or model).ref['id']
        self._models[ref] = (model, parent)
        return model

    def _update_model(
        self, events: Dict[str, param.parameterized.Event], msg: Dict[str, Any],
        root: Model, model: Model, doc: Document, comm: Comm | None
    ) -> None:
        return

    def _cleanup(self, root: Model | None = None) -> None:
        self._card._cleanup(root)
        super()._cleanup(root)

    @param.depends("card_params", watch=True)
    def _update_card_params(self):
        card_params = self.card_params.copy()
        card_params.pop('stylesheets', None)
        self._card.param.update(**card_params)

    @param.depends("placeholder_text", watch=True, on_init=True)
    def _update_placeholder(self):
        if self._placeholder is not None:
            self._placeholder.param.update(object=self.placeholder_text)
            return

        loading_avatar = SVG(
            PLACEHOLDER_SVG, sizing_mode=None, css_classes=["rotating-placeholder"]
        )
        self._placeholder = ChatMessage(
            self.placeholder_text,
            user=" ",
            show_timestamp=False,
            avatar=loading_avatar,
            reaction_icons={},
            show_copy_icon=False,
        )

    def _replace_placeholder(self, message: ChatMessage | None = None) -> None:
        """
        Replace the placeholder from the chat log with the message
        if placeholder, otherwise simply append the message.
        Replacing helps lessen the chat log jumping around.
        """
        index = None
        if self.placeholder_threshold > 0:
            try:
                index = self.index(self._placeholder)
            except ValueError:
                pass

        if index is not None:
            if message is not None:
                self[index] = message
            elif message is None:
                self.remove(self._placeholder)
        elif message is not None:
            self.append(message)

    def _build_message(
        self,
        value: dict,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
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

        message = ChatMessage(**message_params)
        return message

    def _upsert_message(
        self, value: Any, message: ChatMessage | None = None
    ) -> ChatMessage | None:
        """
        Replace the placeholder message with the response or update
        the message's value with the response.
        """
        is_stopping = self._callback_state == CallbackState.STOPPING
        is_stopped = self._callback_future is not None and self._callback_future.cancelled()
        if value is None:
            # don't add new message if the callback returns None
            return
        elif is_stopping or is_stopped:
            raise StopCallback("Callback was stopped.")

        user = self.callback_user
        avatar = None
        if isinstance(value, dict):
            user = value.get("user", user)
            avatar = value.get("avatar")

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
        return contents, message.user, self

    async def _serialize_response(self, response: Any) -> ChatMessage | None:
        """
        Serializes the response by iterating over it and
        updating the message's value.
        """
        response_message = None
        try:
            if isasyncgen(response):
                self._callback_state = CallbackState.GENERATING
                async for token in response:
                    response_message = self._upsert_message(token, response_message)
                    response_message.show_activity_dot = self.show_activity_dot
            elif isgenerator(response):
                self._callback_state = CallbackState.GENERATING
                for token in response:
                    response_message = self._upsert_message(token, response_message)
                    response_message.show_activity_dot = self.show_activity_dot
            elif isawaitable(response):
                response_message = self._upsert_message(await response, response_message)
            else:
                response_message = self._upsert_message(response, response_message)
        finally:
            if response_message:
                response_message.show_activity_dot = False
        return response_message

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
            if duration > self.placeholder_threshold or self._callback_future is None:
                self.append(self._placeholder)
                return
            await asyncio.sleep(0.1)

    async def _to_async_gen(self, sync_gen):
        done = object()

        def safe_next():
            # Converts StopIteration to a sentinel value to avoid:
            # TypeError: StopIteration interacts badly with generators and cannot be raised into a Future
            try:
                return next(sync_gen)
            except StopIteration:
                return done

        while True:
            value = await asyncio.to_thread(safe_next)
            if value is done:
                break
            yield value

    async def _handle_callback(self, message, loop: asyncio.BaseEventLoop):
        callback_args = self._gather_callback_args(message)
        if iscoroutinefunction(self.callback):
            response = await self.callback(*callback_args)
        elif isasyncgenfunction(self.callback):
            response = self.callback(*callback_args)
        else:
            if isgeneratorfunction(self.callback):
                response = self._to_async_gen(self.callback(*callback_args))
                # printing type(response) -> <class 'async_generator'>
            else:
                response = await asyncio.to_thread(self.callback, *callback_args)
        await self._serialize_response(response)

    async def _prepare_response(self, _) -> None:
        """
        Prepares the response by scheduling the placeholder and
        executing the callback.
        """
        if self.callback is None:
            return

        self._was_disabled = self.disabled
        try:
            with param.parameterized.batch_call_watchers(self):
                self.disabled = True
                self._callback_state = CallbackState.RUNNING

            message = self._chat_log[-1]
            if not isinstance(message, ChatMessage):
                return

            num_entries = len(self._chat_log)
            loop = asyncio.get_event_loop()
            future = loop.create_task(self._handle_callback(message, loop))
            self._callback_future = future
            await asyncio.gather(
                self._schedule_placeholder(future, num_entries), future,
            )
        except StopCallback:
            # callback was stopped by user
            self._callback_state = CallbackState.STOPPED
        except Exception as e:
            send_kwargs = dict(user="Exception", respond=False)
            if self.callback_exception == "summary":
                self.send(
                    f"Encountered `{e!r}`. "
                    f"Set `callback_exception='verbose'` to see the full traceback.",
                    **send_kwargs
                )
            elif self.callback_exception == "verbose":
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
            self._callback_state = CallbackState.IDLE
            self.disabled = self._was_disabled

    # Public API

    def send(
        self,
        value: ChatMessage | dict | Any,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
        respond: bool = True,
    ) -> ChatMessage | None:
        """
        Sends a value and creates a new message in the chat log.

        If `respond` is `True`, additionally executes the callback, if provided.

        Arguments
        ---------
        value : ChatMessage | dict | Any
            The message contents to send.
        user : str | None
            The user to send as; overrides the message message's user if provided.
        avatar : str | bytes | BytesIO | None
            The avatar to use; overrides the message message's avatar if provided.
        respond : bool
            Whether to execute the callback.

        Returns
        -------
        The message that was created.
        """
        if isinstance(value, ChatMessage):
            if user is not None or avatar is not None:
                raise ValueError(
                    "Cannot set user or avatar when explicitly sending "
                    "a ChatMessage. Set them directly on the ChatMessage."
                )
            message = value
        else:
            if not isinstance(value, dict):
                value = {"object": value}
            message = self._build_message(value, user=user, avatar=avatar)
        self.append(message)
        if respond:
            self.respond()
        return message

    def stream(
        self,
        value: str,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
        message: ChatMessage | None = None,
        replace: bool = False,
    ) -> ChatMessage | None:
        """
        Streams a token and updates the provided message, if provided.
        Otherwise creates a new message in the chat log, so be sure the
        returned message is passed back into the method, e.g.
        `message = chat.stream(token, message=message)`.

        This method is primarily for outputs that are not generators--
        notably LangChain. For most cases, use the send method instead.

        Arguments
        ---------
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
            if isinstance(value, (str, dict)):
                message.stream(value, replace=replace)
                if user:
                    message.user = user
                if avatar:
                    message.avatar = avatar
            else:
                message.update(value, user=user, avatar=avatar)
            return message

        if isinstance(value, ChatMessage):
            message = value
        else:
            if not isinstance(value, dict):
                value = {"object": value}
            message = self._build_message(value, user=user, avatar=avatar)
        self._replace_placeholder(message)
        return message

    def respond(self):
        """
        Executes the callback with the latest message in the chat log.
        """
        self._callback_trigger.param.trigger("clicks")

    def stop(self) -> bool:
        """
        Cancels the current callback task if possible.

        Returns
        -------
        Whether the task was successfully stopped or done.
        """
        if self._callback_future is None:
            cancelled = False
        elif self._callback_state == CallbackState.GENERATING:
            # cannot cancel generator directly as it's already "finished"
            # by the time cancel is called; instead, set the state to STOPPING
            # and let upsert_message raise StopCallback
            self._callback_state = CallbackState.STOPPING
            cancelled = True
        else:
            cancelled = self._callback_future.cancel()

        if cancelled:
            self.disabled = self._was_disabled
            self._replace_placeholder(None)
        return cancelled

    def undo(self, count: int = 1) -> List[Any]:
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
        self[:] = messages[:-count]
        return undone_entries

    def clear(self) -> List[Any]:
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
        messages: List[ChatMessage],
        role_names: Dict[str, str | List[str]] | None = None,
        default_role: str | None = "assistant",
        custom_serializer: Callable = None
    ) -> List[Dict[str, Any]]:
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
                content = str(message)

            serialized_messages.append({"role": role, "content": content})
        return serialized_messages

    def serialize(
        self,
        exclude_users: List[str] | None = None,
        filter_by: Callable | None = None,
        format: Literal["transformers"] = "transformers",
        custom_serializer: Callable | None = None,
        **serialize_kwargs
    ):
        """
        Exports the chat log.

        Arguments
        ---------
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
        messages = [
            message for message in self._chat_log.objects
            if message.user.lower() not in exclude_users
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

        Arguments
        ---------
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
