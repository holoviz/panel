import random

from textwrap import wrap
from typing import (
    AnyStr, ClassVar, Dict, List, Optional, Type,
)

import param

from panel.layout import Column, ListPanel, Row
from panel.pane.image import Image
from panel.viewable import Layoutable
from panel.widgets.base import CompositeWidget
from panel.widgets.input import StaticText, TextInput


class MessageRow(CompositeWidget):
    value = param.String(
        default="",
        doc="""The message to display""",
    )

    text_color = param.String(
        default="white",
        doc="""Font color of the chat text""",
    )

    background_color = param.String(
        default="black",
        doc="""Background color of the chat bubble""",
    )

    icon = param.String(default=None, doc="""The icon to display""")

    styles = param.Dict(
        default={},
        doc="""
            Dictionary of CSS properties and values to apply
            message to the bubble.
            """,
    )

    show_name = param.Boolean(
        default=True,
        doc="""Whether to show the name of the user""",
    )

    _composite_type: ClassVar[Type[ListPanel]] = Column

    def __init__(
        self,
        value: AnyStr,
        text_color: AnyStr,
        background: AnyStr,
        icon: AnyStr = None,
        styles: Dict[str, str] = None,
        show_name: bool = True,
        **params,
    ):
        bubble_styles = {
            "color": text_color,
            "background-color": background,
            "border-radius": "12px",
            "padding": "8px",
        }
        bubble_styles.update(styles or {})
        super().__init__(**params)

        # determine alignment
        message_layout = {
            p: getattr(self, p)
            for p in Layoutable.param
            if p not in ("name", "height", "margin", "styles")
            and getattr(self, p) is not None
        }
        # create the message icon
        icon_params = dict(
            width=37,  # finetuned so it doesn't start a new line
            height=36,  # designed to not match width
            margin=(12, 2, 12, 2),
            sizing_mode="fixed",
        )
        if icon is None:
            # if no icon is provided,
            # use the first and last letter of the name
            # and a random colored background
            icon_label = f"<strong>{self.name[0]}-{self.name[-1]}</strong>".upper()
            self._icon = StaticText(
                value=icon_label,
                styles=bubble_styles,
                **icon_params,
            )
        else:
            self._icon = Image(icon, **icon_params)

        # create the message bubble
        box_width = message_layout.get("width", 100)
        text_width = int(box_width / 2)  # make text start a new line
        wrapped_text = "\n".join(wrap(value, width=text_width))
        self._bubble = StaticText(
            value=wrapped_text,
            styles=bubble_styles,
            margin=13,
            **message_layout,
        )

        # layout objects
        horizontal_align = message_layout.get("align", "start")
        if isinstance(horizontal_align, tuple):
            horizontal_align = horizontal_align[0]
        if horizontal_align == "start":
            margin = (0, 0, -5, 60)
            objects = (self._icon, self._bubble)
        else:
            margin = (0, 60, -5, 0)
            objects = (self._bubble, self._icon)

        container_params = dict(
            align=horizontal_align,
        )
        row = Row(*objects, **container_params)
        if show_name:
            name = StaticText(
                value=self.name,
                margin=margin,
                styles={"color": "grey"},
                align=horizontal_align,
            )
            row = Column(name, row, **container_params)

        self._composite[:] = [row]


class ChatBox(CompositeWidget):
    user_messages = param.List(
        doc="""List of messages, mapping user to message,
        e.g. `[{'You': 'Welcome!'}]`""",
        item_type=Dict,
        default=[],
    )

    user_icons = param.Dict(
        doc="""Dictionary mapping name of users to their icons,
        e.g. `[{'You': 'path/to/icon.png'}]`""",
        default={},
    )

    user_colors = param.Dict(
        doc="""Dictionary mapping name of users to their colors,
        e.g. `[{'You': 'red'}]`""",
        default={},
    )

    primary_user = param.String(
        doc="""
            Name of the primary user;
            the first key found in user_messages
            will be used if unspecified
        """,
        default=None,
    )

    allow_input = param.Boolean(
        doc="""Whether to allow users to interactively enter messages.""",
        default=True,
    )

    _composite_type: ClassVar[Type[ListPanel]] = Column

    def __init__(self, user_messages: List[AnyStr] = None, **params):
        if user_messages:
            params["user_messages"] = user_messages
        if params.get("width") and params.get("height") and "sizing_mode" not in params:
            params["sizing_mode"] = None

        super().__init__(**params)

        # Set up layout
        layout = {
            p: getattr(self, p)
            for p in Layoutable.param
            if p not in ("name", "height", "margin") and getattr(self, p) is not None
        }
        chat_layout = dict(
            layout,
            sizing_mode="stretch_both",
            height=None,
            margin=0,
        )
        self._chat_log = Column(**chat_layout)
        self._input_message = TextInput(
            name="Type your message",
            placeholder="Press Enter to send",
            sizing_mode="stretch_width",
            width_policy="max",
            align="end",
        )

        # add interactivity
        self.param.watch(self._refresh_log, "user_messages")
        self.param.trigger("user_messages")
        self._input_message.param.watch(self._enter_message, "value")
        if self.allow_input:
            composite_objects = [self._chat_log, self._input_message]
        else:
            composite_objects = [self._chat_log]
        self._composite[:] = composite_objects

    def _get_name(self, dict_: Dict[str, str]) -> str:
        """
        Get the name of the user who sent the message.
        """
        return list(dict_.keys())[0]

    def _generate_dark_color(self) -> str:
        """
        Generate a random dark color in hexadecimal format.
        """
        r, g, b = random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def _instantiate_message_row(
        self, user: str, message: str, show_name: bool
    ) -> MessageRow:
        """
        Instantiate a MessageRow object.
        """
        if self.primary_user is None:
            if self.user_messages:
                self.primary_user = self._get_name(self.user_messages[0])
            else:
                self.primary_user = "You"

        # try to get input color; if not generate one and save
        if user in self.user_colors:
            background = self.user_colors[user]
        else:
            background = self._generate_dark_color()
            self.user_colors[user] = background

        # try to get input icon
        user_icon = self.user_icons.get(user, None)

        align = "start" if user != self.primary_user else "end"

        message_row = MessageRow(
            name=user,
            value=message,
            text_color="white",
            background=background,
            icon=user_icon,
            show_name=show_name,
            align=align,
        )
        return message_row

    def _refresh_log(self, event: Optional[param.parameterized.Event] = None) -> None:
        """
        Refresh the chat log for complete replacement of all messages.
        """
        user_messages = event.new

        message_rows = []
        previous_user = None
        for user_message in user_messages:
            user = self._get_name(user_message)
            message = user_message[user]
            show_name = user != previous_user
            message_row = self._instantiate_message_row(user, message, show_name)
            message_rows.append(message_row)
            previous_user = user
        self._chat_log.objects = message_rows

    def _enter_message(self, event: Optional[param.parameterized.Event] = None) -> None:
        """
        Append the message from the text input when the user presses Enter.
        """
        if event.new == "":
            return

        user = self.primary_user or "You"
        message = event.new
        self.append({user: message})
        self._input_message.value = ""

    def append(self, user_message: Dict[str, str]) -> None:
        """
        Appends a message to the chat log.

        Arguments
        ---------
        user_message (dict): Dictionary mapping user to message.
        """
        # this doesn't trigger anything because it's the same object
        # just append so it stays in sync
        self.user_messages.append(user_message)

        if self._chat_log.objects:
            previous_user = self._chat_log.objects[-1].name
        else:
            previous_user = None

        user = self._get_name(user_message)
        message = user_message[user]
        show_name = user != previous_user
        message_row = self._instantiate_message_row(user, message, show_name)
        self._chat_log.objects = [*self._chat_log.objects, message_row]

    def extend(self, user_messages: List[Dict[str, str]]) -> None:
        """
        Extends the chat log with new users' messages.

        Arguments
        ---------
        user_messages (list): List of user messages to add.
        """
        for user_message in user_messages:
            self.append(user_message)

    def clear(self) -> None:
        """
        Clears the chat log.
        """
        self.user_messages = []
