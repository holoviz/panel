import datetime

import pytest

from panel.layout import Row
from panel.pane.image import Image
from panel.pane.markup import HTML, Markdown
from panel.widgets.chat import (
    ChatEntry, ChatFeed, ChatReactionIcons, _FileInputMessage,
)
from panel.widgets.input import TextInput


class TestChatEntry:
    def test_layout(self):
        entry = ChatEntry(value="ABC")
        columns = entry._composite.objects
        assert len(columns) == 2

        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, HTML)
        assert avatar_pane.object == "U"

        user_pane = columns[1][0].object()
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

    def test_update_user(self):
        entry = ChatEntry(user="Andrew")
        columns = entry._composite.objects
        user_pane = columns[1][0].object()
        assert isinstance(user_pane, HTML)
        assert user_pane.object == "Andrew"

        entry.user = "August"
        user_pane = columns[1][0].object()
        assert user_pane.object == "August"

        entry.show_user = False
        user_pane = columns[1][0].object()
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


class TestChatFeed:
    @pytest.fixture
    def chat_feed(self):
        return ChatFeed()

    def test_stream_message(self, chat_feed):
        entry = chat_feed.stream("Streaming message")
        assert len(chat_feed.entries) == 1
        assert chat_feed.entries[0] is entry

    def test_stream_message_with_user_avatar(self, chat_feed):
        user = "Bob"
        avatar = "👨"
        entry = chat_feed.stream(
            "Streaming with user and avatar", user=user, avatar=avatar
        )
        assert entry.user == user
        assert entry.avatar == avatar

    def test_undo(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")
        entry3 = chat_feed.send("Message 3")

        assert len(chat_feed.entries) == 3

        undone_entries = chat_feed.undo()
        assert len(chat_feed.entries) == 2
        assert undone_entries == [entry3]

        chat_feed.undo(2)
        assert len(chat_feed.entries) == 0

    def test_clear(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")

        assert len(chat_feed.entries) == 2

        cleared_entries = chat_feed.clear()
        assert len(chat_feed.entries) == 0
        assert cleared_entries[0].value == "Message 1"
        assert cleared_entries[1].value == "Message 2"

    def test_send_with_respond(self, chat_feed):
        def callback(contents, user, instance):
            return f"Response to: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Question", respond=True)

        assert len(chat_feed.entries) == 2
        assert chat_feed.entries[1].value == "Response to: Question"

    def test_send_without_respond(self, chat_feed):
        def callback(contents, user, instance):
            return f"Response to: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Question", respond=False)

        assert len(chat_feed.entries) == 1

    def test_respond_without_callback(self, chat_feed):
        chat_feed.respond()  # Should not raise any errors

    def test_entry_updating(self, chat_feed):
        entry = chat_feed.send("Initial message")
        assert len(chat_feed.entries) == 1

        updated_entry = chat_feed.stream(" Appended message", entry=entry)
        assert len(chat_feed.entries) == 1
        assert chat_feed.entries[0] is updated_entry
        assert chat_feed.entries[0].value == "Initial message Appended message"
