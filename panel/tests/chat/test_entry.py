import datetime

import pytest

from panel import Param, bind
from panel.chat.entry import ChatEntry, _FileInputMessage
from panel.chat.icon import ChatReactionIcons
from panel.layout import Column, Row
from panel.pane.image import SVG, Image
from panel.pane.markup import HTML, Markdown
from panel.tests.util import mpl_available, mpl_figure
from panel.widgets.button import Button
from panel.widgets.input import FileInput, TextAreaInput, TextInput


class TestChatEntry:
    def test_layout(self):
        entry = ChatEntry(value="ABC")
        columns = entry._composite.objects
        assert len(columns) == 2

        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, HTML)
        assert avatar_pane.object == "🧑"

        row = columns[1][0]
        user_pane = row[0].object()
        assert isinstance(user_pane, HTML)
        assert user_pane.object == "User"

        center_row = columns[1][1]
        assert isinstance(center_row, Row)

        value_pane = center_row[0].object()
        assert isinstance(value_pane, Markdown)
        assert value_pane.object == "ABC"

        icons = center_row[1]
        assert isinstance(icons, ChatReactionIcons)

        timestamp_pane = columns[1][2].object()
        assert isinstance(timestamp_pane, HTML)

    def test_reactions_link(self):
        # on init
        entry = ChatEntry(reactions=["favorite"])
        assert entry.reaction_icons.value == ["favorite"]

        # on change in entry
        entry.reactions = []
        assert entry.reaction_icons.value == []

        # on change in reaction_icons
        entry.reactions = ["favorite"]
        assert entry.reaction_icons.value == ["favorite"]

    def test_reaction_icons_input_dict(self):
        entry = ChatEntry(reaction_icons={"favorite": "heart"})
        assert isinstance(entry.reaction_icons, ChatReactionIcons)
        assert entry.reaction_icons.options == {"favorite": "heart"}

    def test_update_avatar(self):
        entry = ChatEntry(avatar="A")
        columns = entry._composite.objects
        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, HTML)
        assert avatar_pane.object == "A"

        entry.avatar = "B"
        avatar_pane = columns[0][0].object()
        assert avatar_pane.object == "B"

        entry.avatar = "❤️"
        avatar_pane = columns[0][0].object()
        assert avatar_pane.object == "❤️"

        entry.avatar = "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"
        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, Image)
        assert (
            avatar_pane.object
            == "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"
        )

        entry.show_avatar = False
        avatar_pane = columns[0][0].object()
        assert not avatar_pane.visible

        entry.avatar = SVG("https://tabler-icons.io/static/tabler-icons/icons/user.svg")
        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, SVG)

    def test_update_user(self):
        entry = ChatEntry(user="Andrew")
        columns = entry._composite.objects
        user_pane = columns[1][0][0].object()
        assert isinstance(user_pane, HTML)
        assert user_pane.object == "Andrew"

        entry.user = "August"
        user_pane = columns[1][0][0].object()
        assert user_pane.object == "August"

        entry.show_user = False
        user_pane = columns[1][0][0].object()
        assert not user_pane.visible

    def test_update_value(self):
        entry = ChatEntry(value="Test")
        columns = entry._composite.objects
        value_pane = columns[1][1][0].object()
        assert isinstance(value_pane, Markdown)
        assert value_pane.object == "Test"

        entry.value = TextInput(value="Also testing...")
        value_pane = columns[1][1][0].object()
        assert isinstance(value_pane, TextInput)
        assert value_pane.value == "Also testing..."

        entry.value = _FileInputMessage(
            contents=b"I am a file", file_name="test.txt", mime_type="text/plain"
        )
        value_pane = columns[1][1][0].object()
        assert isinstance(value_pane, Markdown)
        assert value_pane.object == "I am a file"

    def test_update_timestamp(self):
        entry = ChatEntry()
        columns = entry._composite.objects
        timestamp_pane = columns[1][2].object()
        assert isinstance(timestamp_pane, HTML)
        dt_str = datetime.datetime.utcnow().strftime("%H:%M")
        assert timestamp_pane.object == dt_str

        special_dt = datetime.datetime(2023, 6, 24, 15)
        entry.timestamp = special_dt
        timestamp_pane = columns[1][2].object()
        dt_str = special_dt.strftime("%H:%M")
        assert timestamp_pane.object == dt_str

        mm_dd_yyyy = "%b %d, %Y"
        entry.timestamp_format = mm_dd_yyyy
        timestamp_pane = columns[1][2].object()
        dt_str = special_dt.strftime(mm_dd_yyyy)
        assert timestamp_pane.object == dt_str

        entry.show_timestamp = False
        timestamp_pane = columns[1][2].object()
        assert not timestamp_pane.visible

    def test_does_not_turn_widget_into_str(self):
        button = Button()
        entry = ChatEntry(value=button)
        assert entry.value == button

    @mpl_available
    def test_can_display_any_python_object_that_panel_can_display(self):
        # For example matplotlib figures
        ChatEntry(value=mpl_figure())

        # For example async functions
        async def async_func():
            return "hello"

        ChatEntry(value=async_func)

        # For example async generators
        async def async_generator():
            yield "hello"
            yield "world"

        ChatEntry(value=async_generator)

    def test_can_use_pn_param_without_raising_exceptions(self):
        entry = ChatEntry()
        Param(entry)

    def test_bind_reactions(self):
        def callback(reactions):
            entry.value = " ".join(reactions)

        entry = ChatEntry(value="Hello")
        bind(callback, entry.param.reactions, watch=True)
        entry.reactions = ["favorite"]
        assert entry.value == "favorite"

    def test_show_reaction_icons(self):
        entry = ChatEntry()
        assert entry.reaction_icons.visible
        entry.show_reaction_icons = False
        assert not entry.reaction_icons.visible

    def test_default_avatars(self):
        assert isinstance(ChatEntry.default_avatars, dict)
        assert ChatEntry(user="Assistant").avatar == ChatEntry(user="assistant").avatar
        assert ChatEntry(value="Hello", user="NoDefaultUserAvatar").avatar == ""

    def test_default_avatars_depends_on_user(self):
        ChatEntry.default_avatars["test1"] = "1"
        ChatEntry.default_avatars["test2"] = "2"

        entry = ChatEntry(value="Hello", user="test1")
        assert entry.avatar == "1"

        entry.user = "test2"
        assert entry.avatar == "2"

    def test_default_avatars_can_be_updated_but_the_original_stays(self):
        assert ChatEntry(user="Assistant").avatar == "🤖"
        ChatEntry.default_avatars["assistant"] = "👨"
        assert ChatEntry(user="Assistant").avatar == "👨"

        assert ChatEntry(user="System").avatar == "⚙️"

    def test_chat_copy_icon(self):
        entry = ChatEntry(value="testing")
        assert entry.chat_copy_icon.visible
        assert entry.chat_copy_icon.value == "testing"

    @pytest.mark.parametrize("widget", [TextInput, TextAreaInput])
    def test_chat_copy_icon_text_widget(self, widget):
        entry = ChatEntry(value=widget(value="testing"))
        assert entry.chat_copy_icon.visible
        assert entry.chat_copy_icon.value == "testing"

    def test_chat_copy_icon_disabled(self):
        entry = ChatEntry(value="testing", show_copy_icon=False)
        assert not entry.chat_copy_icon.visible
        assert not entry.chat_copy_icon.value

    @pytest.mark.parametrize("component", [Column, FileInput])
    def test_chat_copy_icon_not_string(self, component):
        entry = ChatEntry(value=component())
        assert not entry.chat_copy_icon.visible
        assert not entry.chat_copy_icon.value
