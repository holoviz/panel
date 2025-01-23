"""
The interface module provides an even higher-level API for interacting
with a list of `ChatMessage` objects compared to the `ChatFeed`
through a frontend input UI.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from io import BytesIO
from typing import Any, ClassVar

import param

from ..io.resources import CDN_DIST
from ..layout import Row, Tabs
from ..layout.base import ListLike, NamedListLike
from ..pane.image import ImageBase
from ..viewable import Viewable
from ..widgets.base import WidgetBase
from ..widgets.button import Button
from ..widgets.input import FileInput, TextInput
from .feed import CallbackState, ChatFeed
from .input import ChatAreaInput
from .message import ChatMessage, _FileInputMessage


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
    callback : Callable
        The callback to execute when the button is clicked.
    js_on_click : dict | str | None
        The JavaScript `code` and `args` to execute when the button is clicked.
    """

    index: int
    name: str
    icon: str
    objects: list
    buttons: list
    callback: Callable
    js_on_click: dict | str | None = None


class ChatInterface(ChatFeed):
    """
    High level widget that contains the chat log and the chat input.

    Reference: https://panel.holoviz.org/reference/chat/ChatInterface.html

    :Example:

    >>> async def repeat_contents(contents, user, instance):
    >>>     yield contents

    >>> chat_interface = ChatInterface(
    ...    callback=repeat_contents, widgets=[TextInput(), FileInput()]
    ... )
    """

    auto_send_types = param.List(doc="""
        The widget types to automatically send when the user presses enter
        or clicks away from the widget. If not provided, defaults to
        `[TextInput]`.""")

    avatar = param.ClassSelector(class_=(str, BytesIO, bytes, ImageBase), doc="""
        The avatar to use for the user. Can be a single character text, an emoji,
        or anything supported by `pn.pane.Image`. If not set, uses the
        first character of the name.""")

    reset_on_send = param.Boolean(default=True, doc="""
        Whether to reset the widget's value after sending a message;
        has no effect for `TextInput`.""")

    show_send = param.Boolean(default=True, doc="""
        Whether to show the send button.""")

    show_stop = param.Boolean(default=True, doc="""
        Whether to show the stop button temporarily replacing the send button during
        callback; has no effect if `callback` is not async.""")

    show_rerun = param.Boolean(default=True, doc="""
        Whether to show the rerun button.""")

    show_undo = param.Boolean(default=True, doc="""
        Whether to show the undo button.""")

    show_clear = param.Boolean(default=True, doc="""
        Whether to show the clear button.""")

    show_button_name = param.Boolean(default=None, doc="""
        Whether to show the button name.""")

    show_button_tooltips = param.Boolean(default=False, doc="""
        Whether to show the button tooltips.""")

    user = param.String(default="User", doc="""
        Name of the ChatInterface user.""")

    widgets = param.ClassSelector(class_=(WidgetBase, list), allow_refs=False, doc="""
        Widgets to use for the input. If not provided, defaults to
        `[TextInput]`.""")

    button_properties = param.Dict(default={}, doc="""
        Allows addition of functionality or customization of buttons
        by supplying a mapping from the button name to a dictionary
        containing the `icon`, `callback`, `post_callback`, and/or `js_on_click` keys.

        If the button names correspond to default buttons
        (send, rerun, undo, clear), the default icon can be
        updated and if a `callback` key value pair is provided,
        the specified callback functionality runs before the existing one.

        For button names that don't match existing ones,
        new buttons are created and must include a
        `callback`, `post_callback`, and/or `js_on_click` key.

        The provided callbacks should have a signature that accepts
        two positional arguments: instance (the ChatInterface instance)
        and event (the button click event).

        The `js_on_click` key should be a str or dict. If str,
        provide the JavaScript code; else if dict, it must have a
        `code` key, containing the JavaScript code
        to execute when the button is clicked, and optionally an `args` key,
        containing dictionary of arguments to pass to the JavaScript
        code.
        """)

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

    _buttons = param.Dict(default={}, doc="""
        The rendered buttons.""")

    _stylesheets: ClassVar[list[str]] = [f"{CDN_DIST}css/chat_interface.css"]

    def __init__(self, *objects, **params):
        widgets = params.get("widgets")
        if widgets is None:
            params["widgets"] = [ChatAreaInput(placeholder="Send a message")]
        elif not isinstance(widgets, list):
            params["widgets"] = [widgets]
        active = params.pop("active", None)
        super().__init__(*objects, **params)

        self._input_container = Row(
            css_classes=["chat-interface-input-container"],
            stylesheets=self._stylesheets,
        )
        self._update_input_width()
        self._init_widgets()
        if active is not None:
            self.active = active
        self._card.param.update(
            objects=self._card.objects + [self._input_container],
            css_classes=["chat-interface"],
        )

    def _link_disabled_loading(self, obj: Viewable):
        """
        Link the disabled and loading attributes of the chat box to the
        given object.
        """
        mapping: dict[str, Any] = {"disabled": "disabled", "loading": "loading"}
        values = {p: getattr(self, p) for p in mapping}
        self.param.update(values)
        self.link(obj, **mapping)

    @param.depends("width", watch=True)
    def _update_input_width(self):
        """
        Update the input width.
        """
        if self.show_button_name is None:
            self.show_button_name = self.width is None or self.width >= 400

    @param.depends("widgets", "button_properties", watch=True)
    def _init_widgets(self):
        """
        Initialize the input widgets.

        Returns
        -------
        The input widgets.
        """
        default_button_properties = {
            "send": {"icon": "send", "_default_callback": self._click_send},
            "stop": {"icon": "player-stop", "_default_callback": self._click_stop},
            "rerun": {"icon": "repeat", "_default_callback": self._click_rerun},
            "undo": {"icon": "arrow-back", "_default_callback": self._click_undo},
            "clear": {"icon": "trash", "_default_callback": self._click_clear},
        }
        self._allow_revert = len(self.button_properties) == 0

        button_properties = {**default_button_properties, **self.button_properties}
        for index, (name, properties) in enumerate(button_properties.items()):
            name = name.lower()
            callback = properties.get("callback")
            post_callback = properties.get("post_callback")
            js_on_click = properties.get("js_on_click")
            default_properties = default_button_properties.get(name) or {}
            if default_properties:
                default_callback = default_properties["_default_callback"]
                callback = (
                    self._wrap_callbacks(
                        callback=callback,
                        post_callback=post_callback,
                        name=name,
                    )(default_callback)
                    if callback is not None or post_callback is not None else default_callback
                )
            elif callback is not None and post_callback is not None:
                callback = self._wrap_callbacks(post_callback=post_callback)(callback)
            elif callback is None and post_callback is not None:
                callback = post_callback
            elif callback is None and post_callback is None and not js_on_click:
                raise ValueError(f"A 'callback' key is required for the {name!r} button")
            icon = properties.get("icon") or default_properties.get("icon")
            self._button_data[name] = _ChatButtonData(
                index=index,
                name=name,
                icon=icon,
                objects=[],
                buttons=[],
                callback=callback,
                js_on_click=js_on_click,
            )

        widgets = self.widgets
        if isinstance(self.widgets, WidgetBase):
            widgets = [self.widgets]

        self._widgets = {}
        new_widgets = []
        for widget in widgets:
            key = widget.name or widget.__class__.__name__
            if isinstance(widget, type):  # check if instantiated
                widget = widget()
            if self._widgets.get(key) is not widget:
                self._widgets[key] = widget
                new_widgets.append(widget)

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
            # note, explicitly not isinstance because
            # TextAreaInput will trigger auto send!
            auto_send = (
                isinstance(widget, tuple(self.auto_send_types)) or
                type(widget) in (TextInput, ChatAreaInput)
            )
            if auto_send and widget in new_widgets:
                callback = partial(self._button_data["send"].callback, self)
                widget.param.watch(callback, "value")
            widget.param.update(
                sizing_mode="stretch_width",
                css_classes=["chat-interface-input-widget"]
            )
            if isinstance(widget, ChatAreaInput):
                self.link(widget, disabled="disabled_enter")

            self._buttons = {}
            for button_data in self._button_data.values():
                action = button_data.name
                try:
                    visible = self.param[f'show_{action}'] if action != "stop" else False
                except KeyError:
                    visible = True
                show_name_expr = self.param.show_button_name.rx()
                show_tooltip_expr = self.param.show_button_tooltips.rx()
                button = Button(
                    name=show_name_expr.rx.where(button_data.name.title(), ""),
                    description=show_tooltip_expr.rx.where(f"Click to {button_data.name.lower()}", None),
                    icon=button_data.icon,
                    sizing_mode="stretch_width",
                    max_width=show_name_expr.rx.where(90, 45),
                    max_height=50,
                    margin=(0, 5, 0, 0),
                    align="center",
                    visible=visible
                )
                if action != "stop":
                    self._link_disabled_loading(button)
                if button_data.callback:
                    callback = partial(button_data.callback, self)
                    button.on_click(callback)
                if button_data.js_on_click:
                    js_on_click = button_data.js_on_click
                    if isinstance(js_on_click, dict):
                        if "code" not in js_on_click:
                            raise ValueError(
                                f"A 'code' key is required for the {action!r} button's "
                                "'js_on_click' key"
                            )
                        button.js_on_click(
                            args=js_on_click.get("args", {}),
                            code=js_on_click["code"],
                        )
                    elif isinstance(js_on_click, str):
                        button.js_on_click(code=js_on_click)
                self._buttons[action] = button
                button_data.buttons.append(button)

            message_row = Row(
                widget,
                *list(self._buttons.values()),
                sizing_mode="stretch_width",
                css_classes=["chat-interface-input-row"],
                stylesheets=self._stylesheets,
                align="start",
            )
            input_layout.append((name, message_row))

        # if only a single input, don't use tabs
        if len(self._widgets) == 1:
            input_layout = input_layout[0]

        self._input_container.objects = [input_layout]
        self._input_layout = input_layout

    def _wrap_callbacks(
        self,
        callback: Callable | None = None,
        post_callback: Callable | None = None,
        name: str = ""
    ):
        """
        Wrap the callback and post callback around the default callback.
        """
        def decorate(default_callback: Callable):
            def wrapper(self, event: param.parameterized.Event):
                if name == "send" and not self.active_widget.value:
                    # don't trigger if no message to prevent duplication
                    return

                if callback is not None:
                    try:
                        self.disabled = True
                        callback(self, event)
                    finally:
                        self.disabled = False

                default_callback(self, event)

                if post_callback is not None:
                    try:
                        self.disabled = True
                        post_callback(self, event)
                    finally:
                        self.disabled = False
            return wrapper
        return decorate

    def _click_send(
        self,
        event: param.parameterized.Event | None = None,
        instance: ChatInterface | None = None
    ) -> None:
        """
        Send the input when the user presses Enter.
        """
        # wait until the chat feed's callback is done executing
        # before allowing another input
        if self.disabled:
            return

        active_widget = self.active_widget
        # value_input for ChatAreaInput because value is unsynced until "Enter",
        # value for TextInput and others
        value = active_widget.value
        if not value and hasattr(active_widget, "value_input"):
            value = active_widget.value_input

        if value:
            if isinstance(active_widget, FileInput):
                value = _FileInputMessage(
                    contents=value,
                    mime_type=active_widget.mime_type,
                    file_name=active_widget.filename,
                )
            if isinstance(value, TextInput) or self.reset_on_send:
                updates = {"value": ""}
                if hasattr(active_widget, "value_input"):
                    updates["value_input"] = ""
                try:
                    with param.discard_events(self):
                        active_widget.param.update(updates)
                except ValueError:
                    pass
        else:
            return  # no message entered
        self._reset_button_data()
        self.send(value=value, user=self.user, avatar=self.avatar, respond=True)

    def _click_stop(
        self,
        event: param.parameterized.Event | None = None,
        instance: ChatInterface | None = None
    ) -> bool:
        """
        Cancel the callback when the user presses the Stop button.
        """
        return self.stop()

    def _get_last_user_entry_index(self) -> int:
        """
        Get the index of the last user message.
        """
        messages = self.objects[::-1]
        for index, message in enumerate(messages, 1):
            if message.user == self.user:
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
                    "width": 90,
                }
            else:
                button_update = {
                    "button_type": "default",
                    "name": button_data.name.title() if self.show_button_name else "",
                    "width": 90 if self.show_button_name else 45,
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

    def _click_rerun(
        self,
        event: param.parameterized.Event | None = None,
        instance: ChatInterface | None = None
    ) -> None:
        """
        Upon clicking the rerun button, rerun the last user message,
        which can trigger the callback again.
        """
        count = self._get_last_user_entry_index()
        messages = self.undo(count)
        if not messages:
            return
        self.send(value=messages[0], respond=True)

    def _click_undo(
        self,
        event: param.parameterized.Event | None = None,
        instance: ChatInterface | None = None
    ) -> None:
        """
        Upon clicking the undo button, undo (remove) messages
        up to the last user message. If the button is clicked
        again without performing any other actions, revert the undo.
        """
        undo_data = self._button_data["undo"]
        undo_objects = undo_data.objects
        if not undo_objects:
            self._reset_button_data()
            count = self._get_last_user_entry_index()
            undo_data.objects = self.undo(count)
            if self._allow_revert:
                self._toggle_revert(undo_data, True)
            else:
                undo_data.objects = []
        else:
            self.extend(undo_objects)
            self._reset_button_data()

    def _click_clear(
        self,
        event: param.parameterized.Event | None = None,
        instance: ChatInterface | None = None
    ) -> None:
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
            if self._allow_revert:
                self._toggle_revert(clear_data, True)
            else:
                clear_data.objects = []
        else:
            self[:] = clear_objects.copy()
            self._reset_button_data()

    @property
    def active_widget(self) -> WidgetBase:
        """
        The currently active widget.

        Returns
        -------
        The active widget.
        """
        if isinstance(self._input_layout, Tabs):
            current_tab = self._input_layout[self.active]
            if isinstance(current_tab, (ListLike, NamedListLike)):
                return current_tab.objects[0]
            else:
                return current_tab  # type: ignore
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

        Parameters
        ----------
        index : int
            The active index to set.
        """
        if isinstance(self._input_layout, Tabs):
            self._input_layout.active = index

    def _serialize_for_transformers(
        self,
        messages: list[ChatMessage],
        role_names: dict[str, str | list[str]] | None = None,
        default_role: str = "assistant",
        custom_serializer: Callable[[ChatMessage], Any] | None = None,
        **serialize_kwargs
    ) -> list[dict[str, Any]]:
        """
        Exports the chat log for use with transformers.

        Parameters
        ----------
        messages : list(ChatMessage)
            A list of ChatMessage objects to serialize.
        role_names : dict(str, str | list(str)) | None
            A dictionary mapping the role to the ChatMessage's user name.
            Defaults to `{"user": [self.user], "assistant": [self.callback_user]}`
            if not set. The keys and values are case insensitive as the strings
            will all be lowercased. The values can be a string or a list of strings,
            e.g. `{"user": "user", "assistant": ["executor", "langchain"]}`.
        default_role : str
            The default role to use if the user name is not found in role_names.
            If this is set to None, raises a ValueError if the user name is not found.
        custom_serializer : callable
            A custom function to format the ChatMessage's object. The function must
            accept one positional argument, the ChatMessage object, and return a string.
            If not provided, uses the serialize method on ChatMessage.
        serialize_kwargs : dict
            Additional keyword arguments to pass to the serializer.

        Returns
        -------
        A list of dictionaries with a role and content keys.
        """
        if role_names is None:
            role_names = {
                "user": [self.user],
                "assistant": [self.callback_user],
            }
        return super()._serialize_for_transformers(
            messages, role_names, default_role, custom_serializer, **serialize_kwargs
        )

    @param.depends("_callback_state", watch=True)
    async def _update_input_disabled(self):
        busy_states = (CallbackState.RUNNING, CallbackState.GENERATING)
        if not self.show_stop or self._callback_state not in busy_states or self._callback_future is None:
            with param.parameterized.batch_call_watchers(self):
                self._buttons["send"].visible = True
                self._buttons["stop"].visible = False
        else:
            with param.parameterized.batch_call_watchers(self):
                self._buttons["send"].visible = False
                self._buttons["stop"].visible = True

    async def _cleanup_response(self):
        """
        Events to always execute after the callback is done.
        """
        await super()._cleanup_response()
        await self._update_input_disabled()

    def send(
        self,
        value: ChatMessage | dict | Any,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
        respond: bool = True,
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
            Will default to the user parameter.
        avatar : str | bytes | BytesIO | None
            The avatar to use; overrides the message message's avatar if provided.
            Will default to the avatar parameter.
        respond : bool
            Whether to execute the callback.
        message_params : dict
            Additional parameters to pass to the ChatMessage.

        Returns
        -------
        The message that was created.
        """
        if not isinstance(value, ChatMessage):
            if user is None:
                user = self.user
            if avatar is None:
                avatar = self.avatar
        message_params["show_edit_icon"] = message_params.get(
            "show_edit_icon", user == self.user and self.edit_callback is not None)
        return super().send(value, user=user, avatar=avatar, respond=respond, **message_params)

    def stream(
        self,
        value: str | dict | ChatMessage,
        user: str | None = None,
        avatar: str | bytes | BytesIO | None = None,
        message: ChatMessage | None = None,
        replace: bool = False,
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
            Will default to the user parameter.
        avatar : str | bytes | BytesIO | None
            The avatar to use; overrides the message's avatar if provided.
            Will default to the avatar parameter.
        message : ChatMessage | None
            The message to update.
        replace : bool
            Whether to replace the existing text when streaming a string or dict.
        message_params : dict
            Additional parameters to pass to the ChatMessage.

        Returns
        -------
        The message that was updated.
        """
        if not isinstance(value, ChatMessage) and not message:
            # ChatMessage cannot set user or avatar when explicitly streaming
            # so only set to the default when not a ChatMessage
            user = user or self.user
            avatar = avatar or self.avatar
        message_params["show_edit_icon"] = message_params.get("show_edit_icon", user == self.user and self.edit_callback is not None)
        return super().stream(value, user=user, avatar=avatar, message=message, replace=replace, **message_params)
