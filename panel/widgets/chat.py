import datetime

from typing import BinaryIO, ClassVar, Type

import param

from panel.layout import Column, ListPanel
from panel.reactive import ReactiveHTML
from panel.widgets import CompositeWidget, Widget


class ChatMessage(param.Parameterized):
    value = param.Parameter(
        doc="""
        The message contents. Can be a string, pane, widget, layout, etc."""
    )

    name = param.String(doc="Name of the user who sent the message.")

    icon = param.ClassSelector(
        class_=(str, BinaryIO),
        doc="""
        The icon to use for the user. Can be a URL, a file path, or a binary IO.""",
    )

    liked = param.Boolean(
        default=False,
        doc="""
        Whether the message is favorited.""",
    )

    timestamp = param.Date(
        default=datetime.datetime.utcnow(),
        doc="""
        Timestamp of the message. Defaults to the instantiation time.""",
    )

    @property
    def json(self) -> dict:
        """
        Return the ChatMessage as JSON. For panes,
        extract the pane's underlying `object`.
        For widgets, extract the widget's `value`.
        For layouts, extract the layout's `objects`
        and recursively extract the children's
        `object` or `value`.
        e.g.
        ```
        {
            "value": "Hello, world!",
            "name": "User",
            "icon": "https://...",
            "liked": False,
            "timestamp": "2021-01-01T00:00:00.000Z",
        }
        ```
        """


class ChatEntry(ReactiveHTML):  # Pane?

    object = param.ClassSelector(class_=ChatMessage, doc="The ChatMessage to display.")

    show_name = param.Boolean(default=False, doc="Whether to show the name.")

    show_icon = param.Boolean(default=False, doc="Whether to show the icon.")

    show_liked = param.Boolean(default=False, doc="Whether to show the liked button.")

    show_timestamp = param.Boolean(default=False, doc="Whether to show the timestamp.")

    # reactive html will handle name, icon, and like updates
    _template = """
    """

    def __init__(self, object, **params):
        super().__init__(object=object, **params)


class ChatBlock(Column):  # Layout?
    value = param.List(doc="The list of ChatEntry values.", item_type=ChatEntry)

    callback = param.Callable(
        doc="""
        Callback to execute when a user sends a message."""
    )

    placeholder = param.Parameter(
        doc="""
        Placeholder to display while the callback is running."""
    )

    response_user = param.String(
        default="Assistant",
        doc="""
        The default name of the user who responds to another user.
        If the response callback returns a ChatMessage with a name,
        that name will be used instead.""",
    )

    response_icon = param.ClassSelector(
        class_=(str, BinaryIO),
        doc="""
        The default icon to use for the user who responds to the primary user.
        Can be a URL, a file path, or a binary IO.""",
    )

    @property
    def messages(self):
        """
        Return the list of ChatMessage values.
        """
        ...

    def send(self, message: str):
        """
        Send a message to the chat log.
        """
        ...

    def export(self, format: str = "json"):
        """
        Exports the chat log into a format that can be
        used in other applications.
        """
        ...


class OpenAIChatBlock(ChatBlock):
    api_key = param.String(
        doc="""
        The OpenAI API key."""
    )

    model = param.String(
        default="gpt-3.5-turbo",
        doc="""
        The OpenAI model to use.""",
    )

    temperature = param.Number(
        default=0.5,
        bounds=(0, 1),
        doc="""
        The temperature to use for the OpenAI model.""",
    )

    max_tokens = param.Integer(
        default=100,
        bounds=(1, None),
        doc="""
        The maximum number of tokens to generate.""",
    )


class ChatInterface(CompositeWidget):
    """
    High level widget that contains the chat log and the chat input.
    """

    value = param.ClassSelector(
        class_=ChatBlock,
        doc="""
        The ChatBlock widget.""",
    )

    input_widget = param.ClassSelector(
        class_=Widget,
        doc="""
        Widget to use for the input.""",
    )

    _composite_type: ClassVar[Type[ListPanel]] = Column

    def __init__(self, **params):
        super().__init__(**params)
