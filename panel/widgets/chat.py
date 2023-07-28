import datetime

from typing import (
    Any, BinaryIO, ClassVar, List, Mapping, Optional, Type,
)

import param

from ..io.resources import CDN_DIST
from ..layout import Card, Column, ListPanel
from ..pane.image import Image
from ..pane.markup import HTML
from ..reactive import ReactiveHTML
from . import CompositeWidget, Widget


class ChatMessage(param.Parameterized):

    value = param.Parameter(doc="""
        The message contents. Can be a string, pane, widget, layout, etc.""")

    name = param.String(default="Anonymous", doc="""
        Name of the user who sent the message.""")

    avatar = param.ClassSelector(class_=(str, BinaryIO), doc="""
        The avatar to use for the user. Can be a single character text, an emoji,
        a URL, a file path, or a binary IO. If not set, uses the first letter
        of the name.""")

    reactions = param.List(doc="""
        Reactions to associate with the message.""")

    timestamp = param.Date(
        default=datetime.datetime.utcnow(), doc="""
        Timestamp of the message. Defaults to the instantiation time.""")

    def json(self) -> dict:
        """Return the ChatMessage as JSON."""
        return {
            "value": self.value,
            "name": self.name,
            "avatar": self.avatar,
            "reactions": self.reactions,
            "timestamp": self.timestamp.isoformat(),
        }

    def __init__(self, **params):
        super().__init__(**params)
        if not self.avatar:
            self.avatar = self.name[0]


class ChatReactionIcons(ReactiveHTML):

    value = param.List(doc="The selected reactions.")

    options = param.Dict(default={"dislike": "thumb-down", "like": "thumb-up"}, doc="""
        A key-value pair of reaction values and their corresponding tabler icon names.""")

    icon_size = param.String(default="15px", doc="""
        The size of each icon.""")

    _icon_base_url = param.String("https://tabler-icons.io/static/tabler-icons/icons-png/")

    _template = """
        <div id="reactions" class="reactions">
            {% for reaction, icon_name in options.items() %}
            <img id="icon-{{ reaction }}" alt="{{ reaction }}"
                {% if reaction in value %}
                src="${_icon_base_url}{{ icon_name }}-filled.png"
                {% else %}
                src="${_icon_base_url}{{ icon_name }}.png"
                {% endif %}
                style="width: {{ icon_size }}; height: {{ icon_size }}; cursor: pointer;"
                onclick="${script('update_value')}">
            </img>
            {% endfor %}
        </div>
    """

    _scripts = {
        "update_value": """
            const reaction = event.target.alt;
            const iconName = data.options[reaction];
            if (data.value.includes(reaction)) {
                data.value = data.value.filter(r => r !== reaction);
                event.target.src = data._icon_base_url + iconName + ".png";
            } else {
                data.value = [...data.value, reaction];
                event.target.src = data._icon_base_url + iconName + "-filled.png";
            }
        """
    }


class ChatEntry(ReactiveHTML):
    object = param.ClassSelector(class_=ChatMessage, doc="The ChatMessage to display.")
    reaction_icons = param.ClassSelector(class_=ChatReactionIcons, doc="""
        The available reaction icons to click on.""")
    timestamp_format = param.String(default="%H:%M", doc="The timestamp format.")
    show_avatar = param.Boolean(default=True, doc="Whether to show the avatar.")
    show_name = param.Boolean(default=True, doc="Whether to show the name.")
    show_timestamp = param.Boolean(default=True, doc="Whether to show the timestamp.")

    _avatar = param.Parameter(doc="The rendered avatar.")

    _template = """
    <div class="chat-entry">

        <div class="left">
            {% if show_avatar %}
            <span id="avatar" class="avatar">${_avatar}</span>
            {% endif %}
        </div>

        <div class="right">
            <div class="header">
                {% if show_name %}
                <span id="name" class="name">${object.name}</span>
                {% endif %}
            </div>

            <div class="message">
                ${object.value}
            </div>

            <div class="footer">
                {% if show_timestamp %}
                <span class="timestamp">
                    {{ object.timestamp.strftime(timestamp_format) }}
                </span>
                {% endif %}
                {% if reaction_icons %}
                <span id="reactions-row" class="reactions-row">
                    ${reaction_icons}
                </span>
                {% endif %}
            </div>
        </div>
    </div>
    """

    _stylesheets: ClassVar[List[str]] = [
        f'{CDN_DIST}css/chat_entry.css'
    ]

    def __init__(self, object: ChatMessage, **params):
        super().__init__(object=object, **params)

    @param.depends('object.avatar', watch=True, on_init=True)
    def _render_avatar(self) -> None:
        avatar = self.object.avatar
        if len(avatar) == 1:
            self._avatar = HTML(avatar, css_classes=["text"])
        else:
            self._avatar = Image(avatar, width=40, height=40, css_classes=["image"])

    @param.depends('object.reactions', watch=True, on_init=True)
    def _link_reactions(self) -> None:
        if self.reaction_icons is None:
            self.reaction_icons = ChatReactionIcons()
        self.reaction_icons.link(self.object, value="reactions", bidirectional=True)

class ChatCard(Card):

    callback = param.Callable(doc="""
        Callback to execute when a user sends a message.""")

    placeholder = param.Parameter( doc="""
        Placeholder to display while the callback is running.""")

    auto_scroll_limit = param.Integer(default=100, bounds=(0, None), doc="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""")

    scroll_button_threshold = param.Integer(default=25, bounds=(0, None), doc="""
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.""")

    view_latest = param.Boolean(default=True, doc="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""")

    _rename: ClassVar[Mapping[str, None]] = dict(
        Card._rename, **{
        'callback': None,
        'placeholder': None,
        'auto_scroll_limit': None,
        'scroll_button_threshold': None,
        'view_latest': None,
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
        objects = params.pop("objects", None) or objects
        chat_log_params["objects"] = objects
        chat_log_height = (
            chat_log_params.get("max_height") or
            chat_log_params.get("height", 450)
        )
        sizing_mode = chat_log_params.get("sizing_mode", "fixed")
        if "height" in sizing_mode or "both" in sizing_mode:
            chat_log_params["max_height"] = chat_log_height
        else:
            chat_log_params["height"] = chat_log_height

        self._chat_log = Column(**chat_log_params)
        super().__init__(self._chat_log, **params)

    @param.depends("title", "header", watch=True, on_init=True)
    def _hide_header(self):
        """
        Hide the header if there is no title or header.
        """
        if not self.title and not self.header:
            self.hide_header = True
        else:
            self.hide_header = False

    @property
    def messages(self) -> List[ChatMessage]:
        """
        A list of the current ChatMessage values.

        Returns
        -------
        The current ChatMessage values.
        """
        return [obj.value for obj in self._chat_log.objects]

    def send(self, message: str) -> None:
        """
        Send a message to the chat Card.
        """
        self._chat_log.append(ChatEntry(ChatMessage(value=message)))

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


class OpenAIChatCard(ChatCard):
    api_key = param.String(doc="""
        The OpenAI API key."""
    )

    model = param.String(default="gpt-3.5-turbo", doc="""
        The OpenAI model to use.""")

    temperature = param.Number(default=0.5, bounds=(0, 1), doc="""
        The temperature to use for the OpenAI model.""")

    max_tokens = param.Integer(default=100, bounds=(1, None), doc="""
        The maximum number of tokens to generate.""")


class ChatInterface(CompositeWidget):
    """
    High level widget that contains the chat log and the chat input.
    """

    value = param.ClassSelector(class_=ChatCard, doc="""
        The ChatCard widget.""")

    input_widgets = param.List(item_type=Widget, doc="""
        Widget to use for the input.""")

    _composite_type: ClassVar[Type[ListPanel]] = Column

    def __init__(self, **params):
        super().__init__(**params)
