from __future__ import annotations

from typing import (
    Any, ClassVar, Dict, List, Optional, Tuple, Type, Union,
)

import param

from .._param import Margin
from ..layout import (
    Column, ListPanel, Row, Tabs,
)
from ..pane.base import PaneBase, panel as _panel
from ..pane.image import Image
from ..pane.markup import Markdown
from ..viewable import Layoutable, Viewable
from .base import CompositeWidget
from .button import Button, Toggle
from .input import StaticText, TextInput


class ChatRow(CompositeWidget):
    """
    The ChatRow widget allows displaying a message adjacent to an icon and name.

    :Example:

    >>> ChatRow(name="You", value="Welcome!", show_name=True, align="start")
    """

    value = param.List(doc="""The objects to display""")

    align_name = param.Selector(default="start", objects=["start", "end"], doc="""
        Whether to show the name at the start or end of the row""")

    default_message_callable = param.Callable(default=None, doc="""
        The type of Panel object or callable to use if an item in value is not
        already rendered as a Panel object; if None, uses the
        pn.panel function to render a displayable Panel object.
        If the item is not serializable, will fall back to pn.panel.""")

    icon = param.String(default=None, doc="""
        The icon to display adjacent to the value""")

    liked = param.Boolean(default=False, doc="""
        Whether a user liked the message""")

    margin = Margin(default=0, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    show_name = param.Boolean(default=True, doc="""
        Whether to show the name of the user""")

    show_like = param.Boolean(default=True, doc="""
        Whether to show the like button""")

    styles = param.Dict(default={}, doc="""
        Dictionary of CSS properties and values to apply
        message to the bubble.""")

    _composite_type: ClassVar[Type[ListPanel]] = Column

    def __init__(
        self,
        value: List[Any],
        icon: str = None,
        show_name: bool = True,
        show_like: bool = True,
        styles: Dict[str, str] = None,
        **params,
    ):
        bubble_styles = {
            "overflow-x": "auto",
            "overflow-y": "auto",
            "box-shadow": "rgba(0, 0, 0, 0.15) 1.95px 1.95px 2.6px;",
            "padding": "0.5em",
        }
        if styles:
            bubble_styles.update(styles)
        icon_styles = dict((styles or {}))
        icon_styles.pop("background", None)
        icon_styles.pop("color", None)
        icon_styles.update(
            {
                "border-radius": "50%",
                "font-weight": "bold",
                "font-size": "1.2em",
                "text-align": "center",
            }
        )
        if "background" not in bubble_styles:
            bubble_styles["background"] = "black"
        self._bubble_styles = bubble_styles
        super().__init__(value=value, icon=icon, **params)

        # create the chat icon
        icon_params = dict(width=48, height=48, align="center")
        if icon:
            self._icon = Image(icon, **icon_params)
        else:
            self._icon = None

        # create the chat bubble
        self._bubble = Column(
            *[self._serialize_obj(obj) for obj in self.value],
            align="center",
            margin=8,
            styles=bubble_styles,
        )

        # create heart icon next to chat
        self._like = Toggle(
            name="♡", width=30, height=30, align="end", visible=show_like
        )
        self._like.link(self, value="liked", bidirectional=True)
        self._like.param.watch(self._update_like, "value")

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

        if icon:
            row_objects = (self._icon, self._bubble, self._like)
        else:
            row_objects = (self._bubble, self._like)
        if horizontal_align == "end":
            row_objects = row_objects[::-1]

        container_params = dict(
            sizing_mode="fixed",
            align=(horizontal_align, "center"),
        )
        row = Row(*row_objects, **container_params)
        if show_name:
            if horizontal_align == "end":
                name_margin = (-15, 15, -15, 0)
            else:
                name_margin = (-15, 0, -15, 15)
            self._name = Markdown(
                object=self.name,
                margin=name_margin,
                align=(horizontal_align, "start"),
                styles={"font-size": "0.88em", "color": "grey"},
                sizing_mode="fixed",
            )
            if self.align_name == "start":
                row = Column(self._name, row, **container_params)
            else:
                row = Column(row, self._name, **container_params)
        else:
            self._name = None

        self._composite[:] = [row]

    def _serialize_obj(
        self, obj: Any
    ) -> Viewable:
        """
        Convert an object to a Panel object.
        """
        if isinstance(obj, Viewable):
            return obj

        stylesheets = ["p { margin-block-start: 0.2em; margin-block-end: 0.2em;}"]
        text_styles = {"color": self._bubble_styles.get("color")}
        try:
            if self.default_message_callable is None or issubclass(
                self.default_message_callable, PaneBase
            ):
                panel_obj = (self.default_message_callable or _panel)(
                    obj, stylesheets=stylesheets, styles=text_styles
                )
            else:
                panel_obj = self.default_message_callable(value=obj)
        except ValueError:
            panel_obj = _panel(obj, stylesheets=stylesheets, styles=text_styles)

        if panel_obj.sizing_mode is None:
            panel_obj.sizing_mode = "stretch_width"

        if "overflow-wrap" not in panel_obj.styles:
            panel_obj.styles.update({"overflow-wrap": "break-word"})
        return panel_obj

    def _update_like(self, event: param.parameterized.Event):
        """
        Update the like button when the user clicks it.
        """
        self.liked = event.new
        if self.liked:
            event.obj.name = "❤️"
        else:
            event.obj.name = "♡"


class ChatBox(CompositeWidget):
    """
    The ChatBox widget displays a conversation between multiple users
    composed of users' icons, names, messages, and likes.

    Reference: https://panel.holoviz.org/reference/widgets/ChatBox.html

    :Example:

    >>> ChatBox(value=[{"You": "Hello!"}, {"Bot": ["How may I help?", "I'm a bot."]}])
    """

    value = param.List(default=[], item_type=Dict, doc="""
        List of messages as dicts, mapping user to message(s),
        e.g. `[{'You': ['Welcome!', 'Good bye!']}]` The message(s) can be
        any Python object that can be rendered by Panel.""")

    primary_name = param.String(default=None, doc="""Name of the primary user (the one who inputs messages);
        the first key found in value will be used if unspecified.""")

    allow_input = param.Boolean(default=True, doc="""
        Whether to allow the primary user to interactively enter messages.""")

    allow_likes = param.Boolean(default=False, doc="""
        Whether to allow the primary user to interactively like messages.""")

    ascending = param.Boolean(default=False, doc="""
        Whether to display messages in ascending time order.  If true,
        the latest messages and message_input_widgets will be at the
        bottom of the chat box. Otherwise, they will be at the top.""")

    default_message_callable = param.Callable(default=None, doc="""
        The type of Panel object to use for items in value if they are
        not already rendered as a Panel object; if None, uses the
        pn.panel function to render a displayable Panel object.
        If the item is not serializable, will fall back to pn.panel.
        """)

    message_icons = param.Dict(default={}, doc="""
        Dictionary mapping name of messages to their icons,
        e.g. `[{'You': 'path/to/icon.png'}]`""")

    message_colors = param.Dict(default={}, doc="""
        Dictionary mapping name of messages to their colors, e.g.
        `[{'You': 'red'}]`""")

    message_hue = param.Integer(default=None, bounds=(0, 360), doc="""
        Base hue of the message bubbles if message_colors is not specified for a user.""")

    message_input_widgets = param.List(default=[TextInput], doc="""
        List of widgets to use for message input. Multiple widgets will
        be nested under tabs.""")

    show_names = param.Boolean(default=True, doc="""
        Whether to show chat participant's names below the message.""")

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
            if p not in ("name", "styles", "margin") and getattr(self, p) is not None
        }
        chat_layout = layout.copy()
        chat_layout.update(
            styles={
                "overflow-y": "auto",
                "overflow-x": "auto",
                "flex-direction": "column" if self.ascending else "column-reverse",
            },
        )
        self._chat_title = StaticText(
            value=f"{self.name}",
            styles={"font-size": "1.5em"},
            align="center",
        )
        self._chat_log = Column(**chat_layout)
        self._scroll_button = Button(
            name="Scroll to latest",
            align="center",
            sizing_mode="fixed",
            width=115,
            height=35,
            margin=0,
        )
        self._add_scroll_callback(self._scroll_button, "clicks")
        self._current_hue = self.message_hue
        if self._current_hue:
            self._default_colors = self._generate_default_hsl(self._current_hue)
        else:
            self._default_colors = []

        box_objects = [self._chat_title] if self.name else []
        box_objects.append(self._chat_log)
        if self.ascending:
            box_objects.insert(0, self._scroll_button)
        else:
            box_objects.append(self._scroll_button)

        if self.allow_input:
            self._attach_input(box_objects, layout)
        else:
            self._message_inputs = {}
            self._send_button = None
        self._composite[:] = box_objects

        # add interactivity
        self.param.watch(self._refresh_log, "value")

        # populate with initial value
        self.param.trigger("value")

    def _generate_default_hsl(self, hue: int | None, increment: int = 0) -> List[str]:
        hue += increment
        if hue > 360:
            hue -= 360
        self._current_hue = hue

        return [
            (f"hsl({hue}, 45%, 50%)", "white"),
            (f"hsl({hue}, 30%, 55%)", "white"),
            (f"hsl({hue}, 15%, 60%)", "white"),
        ]

    def _add_scroll_callback(self, obj: Viewable, what: str):
        code = """
            const outerColumn = document.querySelector(".bk-Column")
            const column = outerColumn.shadowRoot.querySelector(".bk-Column")
        """
        if self.ascending:
            code += "\ncolumn.scrollTop = column.scrollHeight"
        else:
            code += "\ncolumn.scrollTop = -column.scrollHeight"

        obj.jscallback(
            args={"chat_log": self._chat_log},
            **{what: code},
        )

    def _link_disabled_loading(self, obj: Viewable):
        """
        Link the disabled and loading attributes of the chat box to the
        given object.
        """
        for key in ["disabled", "loading"]:
            setattr(obj, key, getattr(self, key))
            self.link(obj, **{key: key})

    def _attach_input(self, box_objects: List, layout: Dict[str, str]) -> None:
        """
        Attach the input widgets to the chat box.
        """
        self._message_inputs = {}
        for message_input_widget in self.message_input_widgets:
            key = message_input_widget.name or message_input_widget.__class__.__name__
            if isinstance(message_input_widget, type):  # check if instantiated
                message_input_widget = message_input_widget()
            self._message_inputs[key] = message_input_widget

        self._send_button = Button(
            name="Send",
            button_type="default",
            sizing_mode="stretch_width",
            max_width=100,
            height=35,
        )
        self._send_button.on_click(self._enter_message)

        row_layout = layout.copy()
        row_layout.pop("width", None)
        row_layout.pop("height", None)
        row_layout["sizing_mode"] = "stretch_width"

        input_items = Tabs()
        for message_input_name, message_input in self._message_inputs.items():
            self._link_disabled_loading(message_input)
            message_input.sizing_mode = "stretch_width"
            # for longer form messages, like TextArea / Ace, don't
            # submit when clicking away; only if they manually click
            # the send button
            if isinstance(message_input, TextInput):
                message_input.param.watch(self._enter_message, "value")
                self._add_scroll_callback(message_input, "value")
            send_button = self._send_button.clone()
            self._link_disabled_loading(send_button)
            message_row = Row(message_input, send_button, **row_layout)
            input_items.append((message_input_name, message_row))

        if len(self._message_inputs) == 1:
            input_items = input_items[0]  # if only a single input, don't use tabs

        if self.ascending:
            box_objects.append(input_items)
        else:
            box_objects.insert(0, input_items)

    @staticmethod
    def _get_name(dict_: Dict[str, str]) -> str:
        """
        Get the name of the user who sent the message.
        """
        return next(iter(dict_))

    def _separate_user_message(
        self, user_message: Dict[str, Union[List[Any], Any]]
    ) -> Tuple[str, str]:
        """
        Separate the user and message from a dictionary.
        """
        if len(user_message) == 1:
            user = self._get_name(user_message)
            message_contents = user_message[user]
        elif "role" in user_message and "content" in user_message:
            user = user_message["role"]
            message_contents = user_message["content"]
        else:
            raise ValueError(
                f"Expected a dictionary with one key-value pair, e.g. "
                f"{{'User': 'Message'}} or two key-value pairs with "
                f"'role' and 'content' as keys, e.g. "
                f"{{'role': 'User', 'content': 'Message'}}, "
                f"but got {user_message}"
            )
        return user, message_contents

    def _instantiate_message_row(
        self,
        user: str,
        message_contents: Union[Any, List[Any]],
        show_name: bool,
    ) -> ChatRow:
        """
        Instantiate a ChatRow object.
        """
        if self.primary_name is None:
            if self.value:
                self.primary_name = self._get_name(self.value[0])
            else:
                self.primary_name = "You"

        # try to get input color; if not generate one and save
        if user in self.message_colors:
            colors = self.message_colors[user]
            background, color = (
                colors if isinstance(colors, tuple) else (colors, "black")
            )
        elif self.message_hue:
            if len(self._default_colors) == 0:
                self._default_colors = self._generate_default_hsl(
                    self._current_hue, increment=88
                )
            background, color = self._default_colors.pop()
            self.message_colors[user] = (background, color)
        else:
            if user == self.primary_name:
                background, color = ("rgb(99, 139, 226)", "white")
            else:
                background, color = ("rgb(235, 235, 235)", "black")
            self.message_colors[user] = (background, color)

        # try to get input icon
        message_icon = self.message_icons.get(user, None)

        is_other_user = user != self.primary_name
        align = "start" if is_other_user else "end"
        if not isinstance(message_contents, list):
            message_contents = [message_contents]
        message_row = ChatRow(
            name=user,
            value=message_contents,
            icon=message_icon,
            show_name=show_name,
            show_like=self.allow_likes,
            align=align,
            align_name="start" if self.ascending else "end",
            default_message_callable=self.default_message_callable,
            styles={
                "background": background,
                "color": color,
                "border-radius": "1em",
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
        for i, user_message in enumerate(user_messages):
            user, message_contents = self._separate_user_message(user_message)

            # only show name if it's a new user and only if show_names is True
            show_name = user != previous_user if self.show_names else False
            previous_user = user

            message_row = self._instantiate_message_row(
                user, message_contents, show_name
            )

            # try to rebuild liked status
            if len(self._chat_log.objects) > i:
                original_message_row = self._chat_log.objects[i]
                if original_message_row.value == message_row.value:
                    message_row.liked = original_message_row.liked
            message_rows.append(message_row)

        self._chat_log.objects = message_rows

    def _enter_message(self, _: Optional[param.parameterized.Event] = None) -> None:
        """
        Append the message from the text input when the user presses Enter.
        """
        for message_input in self._message_inputs.values():
            # first set value_input to "" or else it triggers twice in notebook
            # strangely, it doesn't occur when served on the browser
            if hasattr(message_input, "value_input"):
                message_input.value_input = ""
            message = message_input.value
            if message:
                break
        else:
            return  # no message entered across all inputs

        user = self.primary_name or "You"
        self.append({user: message})

    @property
    def rows(self) -> List[ChatRow]:
        """
        Returns a list of ChatRow objects.
        """
        return self._chat_log.objects

    def append(self, user_message: Dict[str, Union[List[Any], Any]]) -> None:
        """
        Appends a message to the chat log.

        Arguments
        ---------
        user_message (dict): Dictionary mapping user to message.
        """
        if not isinstance(user_message, dict):
            raise ValueError(f"Expected a dictionary, but got {user_message}")
        self.value.append(user_message)
        self.param.trigger("value")

    def extend(self, user_messages: List[Dict[str, Union[List[Any], Any]]]) -> None:
        """
        Extends the chat log with new users' messages.

        Arguments
        ---------
        user_messages (list): List of user messages to add.
        """
        self.value.extend(user_messages)
        self.param.trigger("value")

    def insert(self, index: int, user_message: Dict[str, Union[List[Any], Any]]) -> None:
        """
        Inserts a message into the chat log at the given index.

        Arguments
        ---------
        index (int): Index to insert the message at.
        user_message (dict): Dictionary mapping user to message.
        """
        self.value.insert(index, user_message)
        self.param.trigger("value")

    def pop(self, index: int = -1) -> Dict[str, Union[List[Any], Any]]:
        """
        Pops the last message from the chat log.

        Arguments
        ---------
        index (int): Index of the message to pop; defaults to the last message.

        Returns
        -------
        user_message (dict): Dictionary mapping user to message.
        """
        value = self.value.pop(index)
        self.param.trigger("value")
        return value

    def replace(self, index: int, user_message: Dict[str, Union[List[Any], Any]]):
        """
        Replaces a message in the chat log at the given index.

        Arguments
        ---------
        index (int): Index to replace the message at.
        user_message (dict): Dictionary mapping user to message.
        """
        self.value[index] = user_message
        self.param.trigger("value")

    def clear(self) -> None:
        """
        Clears the chat log.
        """
        self.value = []

    def __len__(self) -> int:
        return len(self.value)
