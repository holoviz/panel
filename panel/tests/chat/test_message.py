import datetime

import pytest

from panel import Param, bind
from panel.chat.icon import ChatReactionIcons
from panel.chat.message import ChatMessage, _FileInputMessage
from panel.layout import Column, Row
from panel.pane.image import SVG, Image
from panel.pane.markup import HTML, Markdown
from panel.tests.util import mpl_available, mpl_figure
from panel.widgets.button import Button
from panel.widgets.input import FileInput, TextAreaInput, TextInput


class TestChatMessage:

    def test_layout(self):
        message = ChatMessage(object="ABC")
        columns = message._composite.objects
        assert len(columns) == 2

        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, HTML)
        assert avatar_pane.object == "🧑"

        row = columns[1][0]
        user_pane = row[0]
        assert isinstance(user_pane, HTML)
        assert user_pane.object == "User"

        center_row = columns[1][1]
        assert isinstance(center_row, Row)

        object_pane = center_row[0].object()
        assert isinstance(object_pane, Markdown)
        assert object_pane.object == "ABC"

        icons = center_row[1]
        assert isinstance(icons, ChatReactionIcons)

        timestamp_pane = columns[1][2]
        assert isinstance(timestamp_pane, HTML)

    def test_reactions_link(self):
        # on init
        message = ChatMessage(reactions=["favorite"])
        assert message.reaction_icons.value == ["favorite"]

        # on change in message
        message.reactions = []
        assert message.reaction_icons.value == []

        # on change in reaction_icons
        message.reactions = ["favorite"]
        assert message.reaction_icons.value == ["favorite"]

    def test_reaction_icons_input_dict(self):
        message = ChatMessage(reaction_icons={"favorite": "heart"})
        assert isinstance(message.reaction_icons, ChatReactionIcons)
        assert message.reaction_icons.options == {"favorite": "heart"}

    def test_update_avatar(self):
        message = ChatMessage(avatar="A")
        columns = message._composite.objects
        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, HTML)
        assert avatar_pane.object == "A"

        message.avatar = "B"
        avatar_pane = columns[0][0].object()
        assert avatar_pane.object == "B"

        message.avatar = "❤️"
        avatar_pane = columns[0][0].object()
        assert avatar_pane.object == "❤️"

        message.avatar = "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"
        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, Image)
        assert (
            avatar_pane.object
            == "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"
        )

        message.show_avatar = False
        avatar_pane = columns[0][0].object()
        assert not avatar_pane.visible

        message.avatar = SVG("https://tabler-icons.io/static/tabler-icons/icons/user.svg")
        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, SVG)

    def test_update_user(self):
        message = ChatMessage(user="Andrew")
        columns = message._composite.objects
        user_pane = columns[1][0][0]
        assert isinstance(user_pane, HTML)
        assert user_pane.object == "Andrew"

        message.user = "August"
        user_pane = columns[1][0][0]
        assert user_pane.object == "August"

        message.show_user = False
        user_pane = columns[1][0][0]
        assert not user_pane.visible

    def test_update_object(self):
        message = ChatMessage(object="Test")
        columns = message._composite.objects
        object_pane = columns[1][1][0].object()
        assert isinstance(object_pane, Markdown)
        assert object_pane.object == "Test"

        message.object = TextInput(value="Also testing...")
        object_pane = columns[1][1][0].object()
        assert isinstance(object_pane, TextInput)
        assert object_pane.value == "Also testing..."

        message.object = _FileInputMessage(
            contents=b"I am a file", file_name="test.txt", mime_type="text/plain"
        )
        object_pane = columns[1][1][0].object()
        assert isinstance(object_pane, Markdown)
        assert object_pane.object == "I am a file"

    def test_update_timestamp(self):
        message = ChatMessage()
        columns = message._composite.objects
        timestamp_pane = columns[1][2]
        assert isinstance(timestamp_pane, HTML)
        dt_str = datetime.datetime.utcnow().strftime("%H:%M")
        assert timestamp_pane.object == dt_str

        special_dt = datetime.datetime(2023, 6, 24, 15)
        message.timestamp = special_dt
        timestamp_pane = columns[1][2]
        dt_str = special_dt.strftime("%H:%M")
        assert timestamp_pane.object == dt_str

        mm_dd_yyyy = "%b %d, %Y"
        message.timestamp_format = mm_dd_yyyy
        timestamp_pane = columns[1][2]
        dt_str = special_dt.strftime(mm_dd_yyyy)
        assert timestamp_pane.object == dt_str

        message.show_timestamp = False
        timestamp_pane = columns[1][2]
        assert not timestamp_pane.visible

    def test_does_not_turn_widget_into_str(self):
        button = Button()
        message = ChatMessage(object=button)
        assert message.object == button

    @mpl_available
    def test_can_display_any_python_object_that_panel_can_display(self):
        # For example matplotlib figures
        ChatMessage(object=mpl_figure())

        # For example async functions
        async def async_func():
            return "hello"

        ChatMessage(object=async_func)

        # For example async generators
        async def async_generator():
            yield "hello"
            yield "world"

        ChatMessage(object=async_generator)

    def test_can_use_pn_param_without_raising_exceptions(self):
        message = ChatMessage()
        Param(message)

    def test_bind_reactions(self):
        def callback(reactions):
            message.object = " ".join(reactions)

        message = ChatMessage(object="Hello")
        bind(callback, message.param.reactions, watch=True)
        message.reactions = ["favorite"]
        assert message.object == "favorite"

    def test_show_reaction_icons(self):
        message = ChatMessage()
        assert message.reaction_icons.visible
        message.show_reaction_icons = False
        assert not message.reaction_icons.visible

    def test_default_avatars(self):
        assert isinstance(ChatMessage.default_avatars, dict)
        assert ChatMessage(user="Assistant").avatar == ChatMessage(user="assistant").avatar
        assert ChatMessage(object="Hello", user="NoDefaultUserAvatar").avatar == ""

    def test_default_avatars_depends_on_user(self):
        ChatMessage.default_avatars["test1"] = "1"
        ChatMessage.default_avatars["test2"] = "2"

        message = ChatMessage(object="Hello", user="test1")
        assert message.avatar == "1"

        message.user = "test2"
        assert message.avatar == "2"

    def test_default_avatars_can_be_updated_but_the_original_stays(self):
        assert ChatMessage(user="Assistant").avatar == "🤖"
        ChatMessage.default_avatars["assistant"] = "👨"
        assert ChatMessage(user="Assistant").avatar == "👨"

        assert ChatMessage(user="System").avatar == "⚙️"

    def test_chat_copy_icon(self):
        message = ChatMessage(object="testing")
        assert message.chat_copy_icon.visible
        assert message.chat_copy_icon.value == "testing"

    @pytest.mark.parametrize("widget", [TextInput, TextAreaInput])
    def test_chat_copy_icon_text_widget(self, widget):
        message = ChatMessage(object=widget(value="testing"))
        assert message.chat_copy_icon.visible
        assert message.chat_copy_icon.value == "testing"

    def test_chat_copy_icon_disabled(self):
        message = ChatMessage(object="testing", show_copy_icon=False)
        assert not message.chat_copy_icon.visible
        assert not message.chat_copy_icon.value

    @pytest.mark.parametrize("component", [Column, FileInput])
    def test_chat_copy_icon_not_string(self, component):
        message = ChatMessage(object=component())
        assert not message.chat_copy_icon.visible
        assert not message.chat_copy_icon.value
