from __future__ import annotations

import random

from typing import (
    Any, ClassVar, Dict, List, Optional, Tuple, Type,
)

import param

from panel.layout import Column, ListPanel, Row
from panel.layout.spacer import VSpacer
from panel.pane import Markdown
from panel.pane.base import panel as _panel
from panel.pane.image import Image
from panel.viewable import Layoutable, Viewable
from panel.widgets.base import CompositeWidget
from panel.widgets.input import StaticText, TextInput


class ChatRow(CompositeWidget):
    value = param.List(
        doc="""The objects to display""",
    )

    panel_type = param.ClassSelector(
        default=None,
        class_=(Viewable,),
        doc="""
        The type of Panel object to use if an item in value is not
        already rendered as a Panel object; if None, uses the
        panel function to render a displayable Panel object
        """,
    )

    icon = param.String(
        default=None, doc="""The icon to display adjacent to the value"""
    )

    liked = param.Boolean(
        default=False, doc="""Whether a user liked the message"""
    )

    show_name = param.Boolean(
        default=True,
        doc="""Whether to show the name of the user""",
    )

    styles = param.Dict(
        default={},
        doc="""
            Dictionary of CSS properties and values to apply
            message to the bubble
            """,
    )

    _composite_type: ClassVar[Type[ListPanel]] = Column

    def __init__(
        self,
        value: List[Any],
        panel_type: Viewable = None,
        icon: str = None,
        show_name: bool = True,
        styles: Dict[str, str] = None,
        **params,
    ):
        if panel_type is None:
            panel_type = _panel

        bubble_styles = {
            "border-radius": "16px",
            "padding": "8px",
        }
        bubble_styles.update(styles or {})
        if "background" not in bubble_styles:
            bubble_styles["background"] = "black"
        super().__init__(**params)

        # create the chat icon
        icon_params = dict(
            width=60,
            height=60,
            margin=(12, 2, 12, 2),
            sizing_mode="fixed",
            align="center",
        )
        if icon is None:
            # if no icon is provided,
            # use the first and last letter of the name
            # and a random colored background
            icon_label = f"*{self.name[0:3]}*"
            self._icon = Markdown(
                object=icon_label,
                styles=bubble_styles,
                **icon_params,
            )
        else:
            self._icon = Image(icon, **icon_params)

        # create the chat bubble
        bubble_objects = [
            panel_type(obj) if not isinstance(obj, Viewable) else obj for obj in value
        ]
        self._bubble = Column(
            *bubble_objects,
            margin=12,
            styles=bubble_styles,
            width_policy="max",
        )

        # layout objects
        message_layout = {
            p: getattr(self, p)
            for p in Layoutable.param
            if p not in ("name", "height", "margin", "styles")
            and getattr(self, p) is not None
        }
        horizontal_align = message_layout.get("align", "start")
        if isinstance(horizontal_align, tuple):
            horizontal_align = horizontal_align[0]
        container_params = dict(
            align=(horizontal_align, "center"),
        )
        if horizontal_align == "start":
            margin = (0, 0, -6, 84)
            row_objects = (self._icon, self._bubble, VSpacer(min_width=400))
        else:
            margin = (0, 84, -6, 0)
            row_objects = (VSpacer(min_width=400), self._bubble, self._icon)

        row = Row(*row_objects, **container_params)
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
    value = param.List(
        doc="""List of messages, mapping user to message,
        e.g. `[{'You': 'Welcome!'}]`""",
        item_type=Dict,
        default=[],
    )

    primary_user = param.String(
        doc="""
            Name of the primary input user;
            the first key found in value
            will be used if unspecified
        """,
        default=None,
    )

    allow_input = param.Boolean(
        doc="""
            Whether to allow the primary user to interactively
            enter messages.
        """,
        default=True,
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

    _composite_type: ClassVar[Type[ListPanel]] = Column

    def __init__(self, **params):
        # set up parameters
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
            sizing_mode="stretch_both",
            height=None,
            margin=0,
            **layout,
        )
        self._chat_title = StaticText(
            value=f"{self.name}",
            styles={"font-size": "1.5em"},
            align="center",
        )
        self._chat_log = Column(scroll=True, **chat_layout)

        box_objects = [self._chat_title] if self.name else []
        box_objects.append(self._chat_log)
        if self.allow_input:
            self._input_message = TextInput(
                name="Type your message",
                placeholder="Press Enter to send",
                sizing_mode="stretch_width",
                margin=0,
            )
            self._input_message.param.watch(self._enter_message, "value")
            box_objects.extend([VSpacer(height_policy="min"), self._input_message])
        self._composite[:] = box_objects

        # add interactivity
        self.param.watch(self._refresh_log, "value")
        self.param.trigger("value")

    def _generate_bright_color(self, string: str) -> str:
        """
        Generate a random bright color in hexadecimal format.
        """
        seed = sum([ord(c) for c in string])
        random.seed(seed)

        rgb_range = (180, 230)
        r, g, b = (
            random.randint(*rgb_range),
            random.randint(*rgb_range),
            random.randint(*rgb_range),
        )
        color = "#{:02x}{:02x}{:02x}".format(r, g, b)
        return color

    @staticmethod
    def _get_name(dict_: Dict[str, str]) -> str:
        """
        Get the name of the user who sent the message.
        """
        return next(iter(dict_))

    def _separate_user_message(self, user_message: Dict[str, str]) -> Tuple[str, str]:
        """
        Separate the user and message from a dictionary.
        """
        if len(user_message) != 1:
            raise ValueError(
                f"Expected a dictionary with one key-value pair, e.g. "
                f"{{'User': 'Message'}} , but got {user_message}"
            )

        user = self._get_name(user_message)
        message = user_message[user]
        return user, message

    def _instantiate_message_row(
        self, user: str, message: str, show_name: bool
    ) -> ChatRow:
        """
        Instantiate a ChatRow object.
        """
        if self.primary_user is None:
            if self.value:
                self.primary_user = self._get_name(self.value[0])
            else:
                self.primary_user = "You"

        # try to get input color; if not generate one and save
        if user in self.user_colors:
            background = self.user_colors[user]
        else:
            background = self._generate_bright_color(string=user)
            self.user_colors[user] = background

        # try to get input icon
        user_icon = self.user_icons.get(user, None)

        align = "start" if user != self.primary_user else "end"

        message_row = ChatRow(
            name=user,
            value=[message],
            icon=user_icon,
            show_name=show_name,
            align=align,
            styles={
                "background": background,
            },
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
            user, message = self._separate_user_message(user_message)

            show_name = user != previous_user
            previous_user = user

            message_row = self._instantiate_message_row(user, message, show_name)
            message_rows.append(message_row)

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
        if not isinstance(user_message, dict):
            raise ValueError(f"Expected a dictionary, but got {user_message}")

        # this doesn't trigger anything because it's the same object
        # just append so it stays in sync
        self.value.append(user_message)
        user, message = self._separate_user_message(user_message)

        previous_user = None
        if self._chat_log.objects:
            previous_user = self._chat_log.objects[-1].name
        show_name = user != previous_user

        message_row = self._instantiate_message_row(user, message, show_name)
        self._chat_log.append(message_row)

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
        self.value = []

    def __len__(self) -> int:
        return len(self.value)
