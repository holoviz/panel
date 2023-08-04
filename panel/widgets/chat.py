import asyncio
import datetime

from contextlib import ExitStack
from dataclasses import dataclass
from inspect import isawaitable
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import (
    Any, BinaryIO, ClassVar, List, Optional, Type, Union,
)

import param

from ..io.resources import CDN_DIST
from ..layout import (
    Column, ListPanel, Row, Tabs,
)
from ..layout.card import Card
from ..pane.base import panel as _panel
from ..pane.image import PDF, Image
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

    _stylesheets = [f"{CDN_DIST}css/chat_reaction_icons.css"]

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
            if (data.value.includes(reaction)) {
                data.value = data.value.filter(r => r !== reaction);
                event.target.src = data._icon_base_url + icon_name + ".svg";
            } else {
                data.value = [...data.value, reaction];
                if (reaction in data.active_icons) {
                    event.target.src = data._icon_base_url + data.active_icons[reaction] + ".svg";
                } else {
                    event.target.src = data._icon_base_url + icon_name + "-filled.svg";
                }
            }
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
    A widget to display a chat entry.

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
        Whether to show the avatar.
    show_user : bool
        Whether to show the name.
    show_timestamp : bool
        Whether to show the timestamp.
    """

    value = param.ClassSelector(class_=object, doc="""
        The message contents. Can be a string, pane, widget, layout, etc.""")

    user = param.Parameter(default="User", doc="""
        Name of the user who sent the message.""")

    avatar = param.ClassSelector(class_=(str, BinaryIO), doc="""
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

    show_avatar = param.Boolean(default=True, doc="Whether to show the avatar.")

    show_user = param.Boolean(default=True, doc="Whether to show the name.")

    show_timestamp = param.Boolean(default=True, doc="Whether to show the timestamp.")

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
        value_panel.css_classes = [
            *value_panel.css_classes, "message"
        ]

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


    """
    value = param.List(item_type=ChatEntry, doc="""
        The entries to add to the chat feed.""")

    header = param.Parameter(doc="""
        The header of the chat feed. Can be a string, pane, or widget.""")

    callback = param.Callable(doc="""
        Callback to execute when a user sends a message.
        The signature must include the previous message value `contents`, the previous `user` name,
        and the `chat_feed` instance.""")

    placeholder = param.Parameter(doc="""
        Placeholder to display while the callback is running.
        If not set, defaults to a LoadingSpinner.""")

    placeholder_text = param.String(default="Loading...", doc="""
        If placeholder is the default LoadingSpinner,
        the text to display next to it.""")

    placeholder_threshold = param.Number(default=0.28, bounds=(0, None), doc="""
        Min duration in seconds to display the placeholder. If 0, the placeholder
        will be disabled.""")

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

    _disabled = param.Boolean(default=False, doc="""
        Whether the chat feed is disabled.""")

    _previous_user = param.String(default="", doc="""
        The previous user name.""")

    _stylesheets: ClassVar[List[str]] = [
        f"{CDN_DIST}css/chat_feed.css"
    ]

    _composite_type: ClassVar[Type[ListPanel]] = Card

    def __init__(self, **params: Any):
        super().__init__(**params)

        # instantiate the card
        card_params = {
            "header": self.header,
            "hide_header": self.header is None,
            "collapsed": False,
            "collapsible": False,
            "css_classes": ["chat-card"],
            "header_css_classes": ["chat-card-header"],
            "title_css_classes": ["chat-card-title"],
        }
        card_params.update(**self.card_params)
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
        chat_log_params["styles"] = {"background": "transparent"}
        chat_log_params = self._configure_log_sizing(chat_log_params)
        self._chat_log = Column(**chat_log_params)
        self._composite[:] = [self._chat_log]

        # handle async callbacks using this trick
        self._respond_trigger = Button(visible=False)
        self._respond_trigger.on_click(self._execute_callback)

        if self.placeholder is None:
            self.placeholder = LoadingSpinner(
                name=self.placeholder_text,
                value=True,
                width=40,
                height=40,
                margin=25
            )

    def _configure_log_sizing(self, chat_log_params):
        sizing_mode = chat_log_params.get("sizing_mode", "stretch_width")
        chat_log_params["sizing_mode"] = sizing_mode
        if sizing_mode is None:
            chat_log_params["sizing_mode"] = "stretch_width"
        chat_log_params["objects"] = self.value
        chat_log_height = (
            chat_log_params.get("max_height") or
            chat_log_params.get("height", 450)
        )
        if "height" in sizing_mode or "both" in sizing_mode:
            chat_log_params["max_height"] = chat_log_height
        else:
            chat_log_params["height"] = chat_log_height
        chat_log_params["margin"] = 0
        return chat_log_params

    @param.depends("header", watch=True)
    def _hide_header(self):
        """
        Hide the header if there is no title or header.
        """
        self._composite.hide_header = self.header is None

    def _replace_placeholder(self, entry: Optional[ChatEntry] = None):
        """
        Replace the placeholder from the chat log with the entry
        if placeholder, otherwise simply append the entry.
        Replacing helps lessen the chat log jumping around.
        """
        index = None
        if self.placeholder_threshold > 0:
            try:
                index = list(self._chat_log).index(self.placeholder)
            except ValueError:
                pass

        if index is not None:
            if entry is None:
                self._chat_log.remove(self.placeholder)
            else:
                self._chat_log[index] = entry
        elif entry is not None:
            self._chat_log.append(entry)

    def _update_entry(self, message: Any, entry: ChatEntry) -> bool:
        """
        Update the placeholder entry with the response.
        """
        if isinstance(message, dict):
            message_param_values = message
        else:
            message_param_values =  {"value": message}

        if entry is None:
            entry = ChatEntry(**message_param_values, **self.entry_params)
            self._replace_placeholder(entry)
        else:
            entry.param.update(**message_param_values)
        return entry

    def _extract_contents(self, entry):
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

    async def _serialize_response(self, response):
        response_entry = None
        if hasattr(response, "__aiter__"):
            async for chunk in response:
                response_entry = self._update_entry(chunk, response_entry)
        elif hasattr(response, "__iter__"):
            for chunk in response:
                response_entry = self._update_entry(chunk, response_entry)
        elif isawaitable(self.callback):
            response_entry = self._update_entry(await response, response_entry)
        else:
            response_entry = self._update_entry(response, response_entry)
        return response_entry

    async def _submit_callback(self, entry: ChatEntry):
        contents = self._extract_contents(entry)
        response = self.callback(contents, entry.user, self)
        response_entry = await self._serialize_response(response)
        return response_entry

    async def _append_placeholder(self, task: asyncio.Task, num_entries: int):
        if self.placeholder_threshold == 0:
            return

        start = asyncio.get_event_loop().time()
        while not task.done() and num_entries == len(self._chat_log):
            duration = asyncio.get_event_loop().time() - start
            if duration > self.placeholder_threshold:
                self._chat_log.append(self.placeholder)
                break
            elif duration > 60:
                # in case something went horribly wrong
                break
            await asyncio.sleep(0.05)

    async def _execute_callback(self, _):
        """
        Execute the callback and send the response.
        """
        if self.callback is None:
            return

        try:
            entry = self._chat_log[-1]
            if not isinstance(entry, ChatEntry):
                return
            elif entry.user == self._previous_user:
                return

            self._disabled = True
            num_entries = len(self._chat_log)
            task = asyncio.create_task(self._submit_callback(entry))
            await self._append_placeholder(task, num_entries)
            await task
            response_entry = task.result()
            if entry.user != response_entry.user:
                self._previous_user = response_entry.user
                self._respond_trigger.param.trigger("clicks")
        finally:
            self._replace_placeholder(None)
            self._disabled = False

    def send(
        self,
        message: Union[ChatEntry, dict, str],
        respond: bool = True,
    ) -> None:
        """
        Send a message and creates a new entry in the chat log.
        If respond, additionally executes the callback, if provided.

        Parameters
        ----------
        message : Union[ChatEntry, dict, str]
            The message to send.
        respond : bool
            Whether to execute the callback.

        Returns
        -------
        The entry that was created.
        """
        if isinstance(message, str):
            message = {"value": message}

        if isinstance(message, dict):
            entry = ChatEntry(**message, **self.entry_params)
        else:
            entry = message

        self._chat_log.append(entry)
        if respond:
            self._respond_trigger.param.trigger("clicks")
        return entry

    def undo(self, count: Optional[int] = 1) -> List[Any]:
        """
        Remove the last `count` of entries from
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

    @property
    def entries(self) -> List[ChatEntry]:
        """
        Returns the entries in the chat log.
        """
        return self._chat_log.objects

    @entries.setter
    def entries(self, entries: List[ChatEntry]) -> None:
        """
        Sets the entries in the chat log.
        """
        self._chat_log.objects = entries


class ChatInterface(CompositeWidget):
    """
    High level widget that contains the chat log and the chat input.
    """

    value = param.ClassSelector(class_=ChatFeed, doc="The ChatFeed widget.")

    widgets = param.List(default=[TextInput], doc="""
        Widgets to use for the input.""")

    user = param.String(default="You", doc="Name of the ChatInterface user.")

    avatar = param.ClassSelector(class_=(str, BinaryIO), doc="""
        The avatar to use for the user. Can be a single character text, an emoji,
        or anything supported by `pn.pane.Image`. If not set, uses the
        first character of the name.""")

    show_rerun = param.Boolean(default=False, doc="""
        Whether to show the rerun button.""")

    show_undo = param.Boolean(default=True, doc="""
        Whether to show the undo button.""")

    show_clear = param.Boolean(default=True, doc="""
        Whether to show the clear button.""")

    _button_data = param.Dict(default={}, doc="""
        Metadata and data related to the buttons.""")

    _composite_type: ClassVar[Type[ListPanel]] = Column

    def __init__(self, **params):
        super().__init__(**params)
        if self.value is None:
            self.value = ChatFeed(objects=[])

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
        self._input_layout = self._init_widgets()
        self._composite[:] = [self.value, self._input_layout]

        self.link(self.value, disabled="_disabled", bidirectional=True)


    def _toggle_disabled(func):
        def wrapper(self, *args, **kwargs):
            self.disabled = True
            try:
                func(self, *args, **kwargs)
            finally:
                self.disabled = False
        return wrapper

    def _link_disabled_loading(self, obj: Viewable):
        """
        Link the disabled and loading attributes of the chat box to the
        given object.
        """
        for attr in ["disabled", "loading"]:
            setattr(obj, attr, getattr(self, attr))
            self.link(obj, **{attr: attr})

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

        input_layout = Tabs()
        for name, widget in self._widgets.items():
            widget.sizing_mode = "stretch_width"
            # for longer form messages, like TextArea / Ace, don't
            # submit when clicking away; only if they manually click
            # the send button
            if isinstance(widget, TextInput):
                widget.param.watch(self._click_send, "value")

            buttons = []
            for button_data in self._button_data.values():
                button = Button(
                    icon=button_data.icon, sizing_mode=None, margin=5
                )
                self._link_disabled_loading(button)
                action = button_data.name
                button.on_click(getattr(self, f"_click_{action}"))
                buttons.append(button)
                button_data.buttons.append(button)

            message_row = Row(widget, *buttons)
            input_layout.append((name, message_row))

        # if only a single input, don't use tabs
        if len(self._widgets) == 1:
            input_layout = input_layout[0]

        return input_layout

    async def _click_send(self, _: Optional[param.parameterized.Event] = None) -> None:
        """
        Send the input when the user presses Enter.
        """
        # wait until the chat feed's callback is done executing
        if self.disabled:
            return

        for widget in self._widgets.values():
            if hasattr(widget, "value_input"):
                widget.value_input = ""
            value = widget.value
            if value:
                if isinstance(widget, FileInput):
                    value = _FileInputMessage(
                        contents=value,
                        mime_type=widget.mime_type,
                        file_name=widget.filename,
                    )
                widget.value = ""
                break
        else:
            return  # no message entered across all widgets

        self._reset_button_data()
        message = ChatEntry(
            value=value, user=self.user, avatar=self.avatar
        )
        self.value.send(message=message)

    def _get_last_user_entry_index(self) -> int:
        """
        Get the index of the last user entry.
        """
        entries = self.value.entries[::-1]
        for index, entry in enumerate(entries, 1):
            if entry.user == self.user:
                return index
        return 0

    def _toggle_revert(self, button_data, active):
        for button in button_data.buttons:
            if active and button_data.objects:
                button.button_type = "success"
                button.name = "🔙"
            else:
                button.button_type = "default"
                button.name = ""

    def _reset_button_data(self):
        for button_data in self._button_data.values():
            button_data.objects.clear()
            self._toggle_revert(button_data, False)

    def _click_rerun(self, _):
        """
        Upon clicking the rerun button, rerun the last user entry,
        which can trigger the callback again.
        """
        count = self._get_last_user_entry_index()
        entries = self.value.undo(count)
        if not entries:
            return

        # select the current input tab
        tab = self._input_layout[self._input_layout.active]
        widget = tab.objects[0]
        widget.value = entries[0].value

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
            undo_data.objects = self.value.undo(count)
            self._toggle_revert(undo_data, True)
        else:
            self.value.entries = [*self.value.entries, *undo_objects.copy()]
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
            clear_data.objects = self.value.clear()
            self._toggle_revert(clear_data, True)
        else:
            self.value.entries = clear_objects.copy()
            self._reset_button_data()
