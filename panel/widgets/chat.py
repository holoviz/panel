
from typing import (
    Any, BinaryIO, ClassVar, List, Mapping, Optional, Type, Union,
)

import param

from param.parameterized import iscoroutinefunction

from ..dataclass import ChatMessage
from ..io.resources import CDN_DIST
from ..layout import (
    Column, ListPanel, Row, Tabs,
)
from ..layout.card import Card
from ..pane.chat_entry import ChatEntry
from ..viewable import Viewable
from .base import CompositeWidget
from .button import Button
from .input import TextInput


class ChatCard(Card):

    callback = param.Callable(doc="""
        Callback to execute when a user sends a message.
        The signature must include the previous message `value`, the previous `user` name,
        and the `chat_card` instance.""")

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

    async def send(
            self,
            message: Union[ChatMessage, dict, str],
        ) -> None:
        """
        Send a message to the chat Card.

        Parameters
        ----------
        message : Union[ChatMessage, dict, str]
            The message to send.
        """
        entry = ChatEntry(message, **self.chat_entry_params)
        self._chat_log.append(entry)
        await self._respond()

    async def _stream_response(self, response):
        new = True
        async for chunk in response:
            if new:
                new = False
                placeholder_entry = ChatEntry("", **self.chat_entry_params)
                self._chat_log.append(placeholder_entry)
            self._chat_log[-1] = ChatEntry(chunk, **self.chat_entry_params)

    async def _respond(self):
        if self.callback:
            message = self._chat_log[-1].object
            response = self.callback(message.value, message.user, self)
            if hasattr(response, "__aiter__"):
                await self._stream_response(response)
            elif iscoroutinefunction(self.callback):
                self._chat_log[-1] = await response
            else:
                self._chat_log[-1] = response

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
