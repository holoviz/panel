

from inspect import isawaitable
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import (
    Any, BinaryIO, ClassVar, List, Mapping, Optional, Type, Union,
)

import param

from ..dataclass import ChatMessage
from ..io.resources import CDN_DIST
from ..layout import (
    Column, ListPanel, Row, Tabs,
)
from ..layout.card import Card
from ..pane.base import panel as _panel
from ..pane.image import PDF, Image
from ..pane.markup import HTML, DataFrame
from ..pane.media import Audio, Video
from ..reactive import ReactiveHTML
from ..viewable import Viewable
from .base import CompositeWidget, Widget
from .button import Button
from .input import TextInput


class ChatReactionIcons(ReactiveHTML):

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
        <div id="reactions" class="reactions">
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


class ChatEntry(CompositeWidget):
    value = param.ClassSelector(class_=ChatMessage, doc="The ChatMessage to display.")
    reaction_icons = param.ClassSelector(class_=ChatReactionIcons, doc="""
        The available reaction icons to click on.""")
    timestamp_format = param.String(default="%H:%M", doc="The timestamp format.")
    show_avatar = param.Boolean(default=False, doc="Whether to show the avatar.")
    show_user = param.Boolean(default=True, doc="Whether to show the name.")
    show_timestamp = param.Boolean(default=True, doc="Whether to show the timestamp.")
    css_classes = param.List(
        default=["chat-entry"],
        doc="""CSS classes to apply to the layout.""",
    )

    _avatar = param.String(doc="The rendered avatar.")

    _timestamp = param.String(doc="The rendered timestamp.")

    _composite_type: ClassVar[Type[Row]] = Row

    _stylesheets: ClassVar[List[str]] = [f"{CDN_DIST}css/chat_entry.css"]

    def __init__(self, **params):
        if isinstance(params["value"], str):
            params["value"] = ChatMessage(value=params["value"])
        self._message_container = Column(stylesheets=self._stylesheets)

        super().__init__(**params)
        right = Column(
            HTML(self.value.param.user, css_classes=["name"]),
            self._message_container,
            HTML(self._timestamp, css_classes=["timestamp"]),
            stylesheets=self._stylesheets,
        )
        self._composite[:] = [HTML(self._avatar, css_classes=["avatar", "text"]), right]

    def _get_panel_callable(self, content, mime_type, file_name=None):
        message_callable = _panel
        if mime_type == 'application/pdf':
            content = self._exit_stack.enter_context(
                BytesIO(content)
            )
            message_callable = PDF
        elif mime_type.startswith('audio/'):
            f = self._exit_stack.enter_context(
                NamedTemporaryFile(suffix=".mp3", delete=False)
            )
            f.write(content)
            f.seek(0)
            content = f.name
            message_callable = Audio
        elif mime_type.startswith('video/'):
            content = self._exit_stack.enter_context(
                BytesIO(content)
            )
            message_callable = Video
        elif mime_type.startswith('image/'):
            content = self._exit_stack.enter_context(
                BytesIO(content)
            )
            message_callable = Image
        elif mime_type.endswith("/csv"):
            import pandas as pd
            with BytesIO(content) as buf:
                content = pd.read_csv(buf)
            message_callable = DataFrame
        elif file_name is not None:
            content = f"`{file_name}`"
        return content, message_callable

    @param.depends("value.avatar", watch=True, on_init=True)
    def _render_avatar(self) -> None:
        """
        Renders the avatar as an image or text.
        """
        avatar = self.value.avatar
        if avatar.startswith("http") or Path(avatar).exists():
            self._avatar = f"<img src='{avatar}' class='avatar'>"
        else:
            self._avatar = avatar

    @param.depends("value.value", watch=True, on_init=True)
    def _render_message_content(self) -> None:
        message_content = self.value.value
        if isinstance(message_content, Viewable):
            self._message_container.objects = [message_content]

        try:
            import magic
            mime_type = magic.from_buffer(message_content, mime=True)
            message_content, message_callable = self._get_panel_callable(
                message_content, mime_type, file_name=None
            )
        except ImportError:
            message_callable = _panel

        css_classes = ["message"]
        try:
            if isinstance(message_callable, Widget):
                panel_obj = message_callable(
                    value=message_content, css_classes=css_classes)
            else:
                panel_obj = message_callable(
                    message_content, css_classes=css_classes)
        except ValueError:
            panel_obj = _panel(message_content, css_classes=css_classes)
        self._message_container.objects = [panel_obj]

    @param.depends("value.timestamp", watch=True, on_init=True)
    def _render_timestamp(self) -> None:
        """
        Formats the timestamp.
        """
        self._timestamp = self.value.timestamp.strftime(self.timestamp_format)

class ChatCard(Card):

    callback = param.Callable(doc="""
        Callback to execute when a user sends a message.
        The signature must include the previous message `value`, the previous `user` name,
        and the `chat_card` instance.""")

    placeholder = param.String(doc="""
        Placeholder to display while the callback is running.""")

    auto_scroll_limit = param.Integer(default=100, bounds=(0, None), doc="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""")

    scroll_button_threshold = param.Integer(default=50, bounds=(0, None), doc="""
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.""")

    view_latest = param.Boolean(default=True, doc="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""")

    chat_entry_params = param.Dict(default={}, doc="""
        Params to pass to ChatEntry, like `reaction_icons`, `timestamp_format`,
        `show_avatar`, `show_user`, and `show_timestamp`.""")

    _rename: ClassVar[Mapping[str, None]] = dict(
        Card._rename, **{
        'callback': None,
        'placeholder': None,
        'auto_scroll_limit': None,
        'scroll_button_threshold': None,
        'view_latest': None,
        'chat_entry_params': None,
    })

    _stylesheets: ClassVar[List[str]] = [
        f'{CDN_DIST}css/chat_card.css'
    ]

    def __init__(self, *objects: Any, **params: Any):
        params.update({
            "collapsed": False,
            "collapsible": False,
            "css_classes": ['chat-card'],
            "header_css_classes": ['chat-card-header'],
            "title_css_classes": ['chat-card-title'],
        })
        chat_log_params = {
            p: getattr(self, p)
            for p in Column.param
            if (
                p in ChatCard.param and
                p != "name" and
                getattr(self, p) is not None
            )
        }
        chat_log_params["styles"] = {"background": "transparent"}
        objects = params.pop("objects", None) or objects

        sizing_mode = chat_log_params.get("sizing_mode", "stretch_width")
        chat_log_params["sizing_mode"] = sizing_mode
        if sizing_mode is None:
            chat_log_params["sizing_mode"] = "stretch_width"
        chat_log_params["objects"] = objects
        chat_log_height = (
            chat_log_params.get("max_height") or
            chat_log_params.get("height", 450)
        )
        if "height" in sizing_mode or "both" in sizing_mode:
            chat_log_params["max_height"] = chat_log_height
        else:
            chat_log_params["height"] = chat_log_height

        self._chat_log = Column(**chat_log_params)
        super().__init__(self._chat_log, **params)

    @property
    def messages(self) -> List[ChatMessage]:
        """
        A list of the current ChatMessage values.

        Returns
        -------
        The current ChatMessage values.
        """
        return [obj.value for obj in self._chat_log.objects]

    @param.depends("title", "header", watch=True, on_init=True)
    def _hide_header(self):
        """
        Hide the header if there is no title or header.
        """
        if not self.title and not self.header:
            self.hide_header = True
        else:
            self.hide_header = False

    def _update_entry(self, placeholder_entry: ChatEntry, message: Any) -> None:
        """
        Update the placeholder entry with the response.
        """
        if isinstance(message, ChatMessage):
            message_param_values = dict(message.param.get_param_values())
            message_param_values.pop("name")
        elif isinstance(message, dict):
            message_param_values = message
        else:
            message_param_values =  {"value": message}
        placeholder_entry.value.param.update(**message_param_values)

    async def _execute_callback(self):
        """
        Execute the callback and send the response.
        """
        entry = self._chat_log[-1]
        message = entry.value
        response = self.callback(message.value, message.user, self)

        new = True
        if new:
            new = False
            placeholder_entry = ChatEntry(
                value=ChatMessage(value=self.placeholder),
                **self.chat_entry_params
            )
            self._chat_log.append(placeholder_entry)

        if hasattr(response, "__aiter__"):
            async for chunk in response:
                self._update_entry(placeholder_entry, chunk)
        elif hasattr(response, "__iter__"):
            for chunk in response:
                self._update_entry(placeholder_entry, chunk)
        elif isawaitable(self.callback):
            self._update_entry(placeholder_entry, await response)
        else:
            self._update_entry(placeholder_entry, response)

    async def send(
        self,
        message: Union[ChatMessage, dict, str],
    ) -> None:
        """
        Send a message to the Chat Card and
        execute the callback if provided.

        Parameters
        ----------
        message : Union[ChatMessage, dict, str]
            The message to send.
        """
        entry = ChatEntry(value=message, **self.chat_entry_params)
        self._chat_log.append(entry)
        if self.callback:
            await self._execute_callback()

    # async def respond(
    #     self,
    #     message: Union[ChatMessage, dict, str],
    #     user: Optional[str] = None,
    #     avatar: Optional[Union[str, BinaryIO]] = None,
    # ):
    #     """
    #     Respond to the last message.

    #     Parameters
    #     ----------
    #     message : Union[ChatMessage, dict, str]
    #         The message to send.
    #     user : str, optional
    #         The user name to use.
    #     avatar : Union[str, BinaryIO], optional
    #         The avatar to use.
    #     """
    #     if isinstance(message, str):
    #         message = {"value": message}
    #     if isinstance(message, dict):
    #         if user:
    #             message["user"] = user
    #         if avatar:
    #             message["avatar"] = avatar
    #         message = ChatMessage(**message)
    #     entry = ChatEntry(value=message, **self.chat_entry_params)
    #     self._chat_log.append(entry)

    def export(self, reactions: List[str] = None, format: Optional[str] = None) -> List[Any]:
        """
        Filters the chat log by reactions and exports them
        in the specified format.

        Parameters
        ----------
        reactions : List[str], optional
            The reactions to filter by; messages with any of the
            reactions will be exported. If None, all messages will be
            exported.
        format : str, optional
            The format to export to; The supported formats are supported:
            - "entry" (ChatEntry)
            - "message" (ChatMessage)
            - "contents" (ChatMessage.value)
            - "json" (ChatMessage.json())

        Returns
        -------
        The exported logs in the specified format.
        """
        output = []
        for entry in self._chat_log.objects:
            message = entry.object
            if reactions is not None:
                if not set(reactions).intersection(message.reactions):
                    continue
            if format == "entry":
                output.append(entry)
            elif format == "message":
                output.append(message)
            elif format == "contents":
                output.append(message.value)
            elif format == "json":
                output.append(message.json())
            else:
                raise ValueError(f"Unsupported format: {format}")
        return output

# class OpenAIChatCard(ChatCard):
#     api_key = param.String(doc="""
#         The OpenAI API key."""
#     )

#     model = param.String(default="gpt-3.5-turbo", doc="""
#         The OpenAI model to use.""")

#     temperature = param.Number(default=0.5, bounds=(0, 1), doc="""
#         The temperature to use for the OpenAI model.""")

#     max_tokens = param.Integer(default=100, bounds=(1, None), doc="""
#         The maximum number of tokens to generate.""")


class ChatInterface(CompositeWidget):
    """
    High level widget that contains the chat log and the chat input.
    """

    value = param.ClassSelector(class_=ChatCard, doc="The ChatCard widget.")

    inputs = param.List(default=[TextInput], doc="""
        Widgets to use for the input.""")

    user = param.String(default="You", doc="Name of the ChatInterface user.")

    avatar = param.ClassSelector(class_=(str, BinaryIO), doc="""
        The avatar to use for the user. Can be a single character text, an emoji,
        a URL, a file path, or a binary IO. If not set, uses the first letter
        of the name.""")

    _composite_type: ClassVar[Type[ListPanel]] = Column

    def __init__(self, **params):
        super().__init__(**params)
        if self.value is None:
            self.value = ChatCard(objects=[])

        input_layout = self._init_inputs()
        self._composite[:] = [self.value, input_layout]

    def _link_disabled_loading(self, obj: Viewable):
        """
        Link the disabled and loading attributes of the chat box to the
        given object.
        """
        for key in ["disabled", "loading"]:
            setattr(obj, key, getattr(self, key))
            self.link(obj, **{key: key})

    def _init_inputs(self) -> Union[Tabs, Row]:
        """
        Initialize the input widgets.

        Returns
        -------
        The input widgets.
        """
        self._inputs = {}
        for widget in self.inputs:
            key = widget.name or widget.__class__.__name__
            if isinstance(widget, type):  # check if instantiated
                widget = widget()
            self._inputs[key] = widget

        input_layout = Tabs()
        for name, widget in self._inputs.items():
            self._link_disabled_loading(widget)
            widget.sizing_mode = "stretch_width"
            # for longer form messages, like TextArea / Ace, don't
            # submit when clicking away; only if they manually click
            # the send button
            if isinstance(widget, TextInput):
                widget.param.watch(self._enter_input, "value")
            send_button = Button(
                name="Send",
                button_type="default",
                sizing_mode="stretch_width",
                max_width=100,
                height=35,
            )
            send_button.on_click(self._enter_input)
            self._link_disabled_loading(send_button)
            message_row = Row(widget, send_button)
            input_layout.append((name, message_row))

        if len(self._inputs) == 1:
            input_layout = input_layout[0]  # if only a single input, don't use tabs

        return input_layout

    async def _enter_input(self, _: Optional[param.parameterized.Event] = None) -> None:
        """
        Send the input when the user presses Enter.
        """
        for widget in self._inputs.values():
            if hasattr(widget, "value_input"):
                widget.value_input = ""
            value = widget.value
            if value:
                widget.value = ""
                break
        else:
            return  # no message entered across all inputs

        message = ChatMessage(
            value=value, user=self.user, avatar=self.avatar
        )
        await self.value.send(message=message)
