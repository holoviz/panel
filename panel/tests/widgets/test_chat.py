import datetime

import panel as pn


class TestChatEntry:
    def test_layout(self):
        entry = pn.widgets.ChatEntry(value="ABC")
        columns = entry._composite.objects
        assert len(columns) == 2

        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, pn.pane.HTML)
        assert avatar_pane.object == "U"

        user_pane = columns[1][0].object()
        assert isinstance(user_pane, pn.pane.HTML)
        assert user_pane.object == "User"

        center_row = columns[1][1]
        assert isinstance(center_row, pn.Row)

        value_pane = center_row[0].object()
        assert isinstance(value_pane, pn.pane.Markdown)
        assert value_pane.object == "ABC"

        icons = center_row[1]
        assert isinstance(icons, pn.widgets.ChatReactionIcons)

        timestamp_pane = columns[1][2].object()
        assert isinstance(timestamp_pane, pn.pane.HTML)

    def test_reactions_link(self):
        # on init
        entry = pn.widgets.ChatEntry(reactions=["favorite"])
        assert entry.reaction_icons.value == ["favorite"]

        # on change in entry
        entry.reactions = []
        assert entry.reaction_icons.value == []

        # on change in reaction_icons
        entry.reactions = ["favorite"]
        assert entry.reaction_icons.value == ["favorite"]

    def test_reaction_icons_input_dict(self):
        entry = pn.widgets.ChatEntry(reaction_icons={"favorite": "heart"})
        assert isinstance(entry.reaction_icons, pn.widgets.ChatReactionIcons)
        assert entry.reaction_icons.options == {"favorite": "heart"}

    def test_update_avatar(self):
        entry = pn.widgets.ChatEntry(avatar="A")
        columns = entry._composite.objects
        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, pn.pane.HTML)
        assert avatar_pane.object == "A"

        entry.avatar = "B"
        avatar_pane = columns[0][0].object()
        assert avatar_pane.object == "B"

        entry.avatar = "❤️"
        avatar_pane = columns[0][0].object()
        assert avatar_pane.object == "❤️"

        entry.avatar = "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"
        avatar_pane = columns[0][0].object()
        assert isinstance(avatar_pane, pn.pane.Image)
        assert (
            avatar_pane.object
            == "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"
        )

        entry.show_avatar = False
        avatar_pane = columns[0][0].object()
        assert not avatar_pane.visible

    def test_update_user(self):
        entry = pn.widgets.ChatEntry(user="Andrew")
        columns = entry._composite.objects
        user_pane = columns[1][0].object()
        assert isinstance(user_pane, pn.pane.HTML)
        assert user_pane.object == "Andrew"

        entry.user = "August"
        user_pane = columns[1][0].object()
        assert user_pane.object == "August"

        entry.show_user = False
        user_pane = columns[0][0].object()
        assert not user_pane.visible

    def test_update_value(self):
        entry = pn.widgets.ChatEntry(value="Test")
        columns = entry._composite.objects
        value_pane = columns[1][1][0].object()
        assert isinstance(value_pane, pn.pane.Markdown)
        assert value_pane.object == "Test"

        entry.value = pn.widgets.TextInput(value="Also testing...")
        value_pane = columns[1][1][0].object()
        assert isinstance(value_pane, pn.widgets.TextInput)
        assert value_pane.value == "Also testing..."

        entry.value = pn.widgets.chat._FileInputMessage(
            contents=b"I am a file",
            file_name="test.txt",
            mime_type="text/plain"
        )
        value_pane = columns[1][1][0].object()
        assert isinstance(value_pane, pn.pane.Markdown)
        assert value_pane.object == "I am a file"

    def test_update_timestamp(self):
        entry = pn.widgets.ChatEntry()
        columns = entry._composite.objects
        timestamp_pane = columns[1][2].object()
        assert isinstance(timestamp_pane, pn.pane.HTML)
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
        timestamp_pane = columns[0][0].object()
        assert not timestamp_pane.visible
