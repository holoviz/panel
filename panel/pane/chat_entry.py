
from typing import ClassVar, List, Union

import param

from ..dataclass import ChatMessage
from ..io.resources import CDN_DIST
from ..pane.image import Image
from ..pane.markup import HTML
from ..reactive import ReactiveHTML


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


class ChatEntry(ReactiveHTML):
    object = param.ClassSelector(class_=ChatMessage, doc="The ChatMessage to display.")
    reaction_icons = param.ClassSelector(class_=ChatReactionIcons, doc="""
        The available reaction icons to click on.""")
    timestamp_format = param.String(default="%H:%M", doc="The timestamp format.")
    show_avatar = param.Boolean(default=True, doc="Whether to show the avatar.")
    show_user = param.Boolean(default=True, doc="Whether to show the name.")
    show_timestamp = param.Boolean(default=True, doc="Whether to show the timestamp.")

    _avatar_pane = param.Parameter(doc="The rendered avatar pane.")

    _template = """
    <div class="chat-entry">

        <div class="left">
            {% if show_avatar %}
            <span id="avatar" class="avatar">${_avatar_pane}</span>
            {% endif %}
        </div>

        <div class="right">
            <div class="header">
                {% if show_user %}
                <span id="name" class="name">${object.user}</span>
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

    def __init__(self, object: Union[ChatMessage, dict, str], **params):
        object = self._serialize_message(object)
        if params.get("reaction_icons") is None:
            params["reaction_icons"] = ChatReactionIcons()
        elif isinstance(params["reaction_icons"], dict):
            params["reaction_icons"] = ChatReactionIcons(options=params["reaction_icons"])
        super().__init__(object=object, **params)
        self.reaction_icons.link(self.object, value="reactions", bidirectional=True)

    def _serialize_message(
            self,
            message: Union[ChatMessage, dict, str],
        ) -> ChatMessage:
        """
        Create a ChatMessage from the given message.
        """
        if isinstance(message, str):
            message = ChatMessage(value=message)
        elif isinstance(message, dict):
            if "value" not in message:
                raise ValueError("Message must contain a 'value' key.")
            message = ChatMessage(**message)
        return message

    @param.depends('object.avatar', watch=True, on_init=True)
    def _render_avatar(self) -> None:
        """
        Render the avatar pane as some HTML text or Image pane.
        """
        avatar = self.object.avatar
        if len(avatar) == 1:
            self._avatar_pane = HTML(avatar, css_classes=["text"])
        else:
            self._avatar_pane = Image(avatar, width=40, height=40, css_classes=["image"])
