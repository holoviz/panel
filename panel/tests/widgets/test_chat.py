import asyncio
import datetime
import time

from unittest.mock import MagicMock

import pytest

from panel import Param, bind
from panel.layout import Column, Row, Tabs
from panel.pane.image import SVG, Image
from panel.pane.markup import HTML, Markdown
from panel.tests.util import mpl_available, mpl_figure
from panel.widgets.button import Button
from panel.widgets.chat import (
    ChatEntry, ChatFeed, ChatInterface, ChatReactionIcons, _FileInputMessage,
)
from panel.widgets.indicators import LinearGauge
from panel.widgets.input import FileInput, TextAreaInput, TextInput

LAYOUT_PARAMETERS = {
    "sizing_mode": "stretch_height",
    "height": 201,
    "max_height": 301,
    "width": 101,
    "max_width": 201,
}


class TestChatReactionIcons:
    def test_init(self):
        icons = ChatReactionIcons()
        assert icons.options == {"favorite": "heart"}

        svg = icons._svgs[0]
        assert isinstance(svg, SVG)
        assert svg.alt_text == "favorite"
        assert not svg.encode
        assert svg.margin == 0
        svg_text = svg.object
        assert 'alt="favorite"' in svg_text
        assert "icon-tabler-heart" in svg_text

        assert icons._reactions == ["favorite"]

    def test_options(self):
        icons = ChatReactionIcons(options={"favorite": "heart", "like": "thumb-up"})
        assert icons.options == {"favorite": "heart", "like": "thumb-up"}
        assert len(icons._svgs) == 2

        svg = icons._svgs[0]
        assert svg.alt_text == "favorite"

        svg = icons._svgs[1]
        assert svg.alt_text == "like"

    def test_value(self):
        icons = ChatReactionIcons(value=["favorite"])
        assert icons.value == ["favorite"]

        svg = icons._svgs[0]
        svg_text = svg.object
        assert "icon-tabler-heart-fill" in svg_text

    def test_active_icons(self):
        icons = ChatReactionIcons(
            options={"dislike": "thumb-up"},
            active_icons={"dislike": "thumb-down"},
            value=["dislike"],
        )
        assert icons.options == {"dislike": "thumb-up"}

        svg = icons._svgs[0]
        svg_text = svg.object
        assert "icon-tabler-thumb-down" in svg_text

        icons.value = []
        svg = icons._svgs[0]
        svg_text = svg.object
        assert "icon-tabler-thumb-up" in svg_text

    def test_width_height(self):
        icons = ChatReactionIcons(width=50, height=50)
        svg = icons._svgs[0]
        svg_text = svg.object
        assert 'width="50px"' in svg_text
        assert 'height="50px"' in svg_text


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

class TestChatFeed:
    @pytest.fixture
    def chat_feed(self):
        return ChatFeed()

    def test_hide_header(self, chat_feed):
        assert chat_feed.header is None

        chat_feed.header = "# Header"
        assert not chat_feed._composite.hide_header

        chat_feed.header = None
        assert chat_feed._composite.hide_header

        chat_feed.header = ""
        assert chat_feed._composite.hide_header

    def test_send(self, chat_feed):
        entry = chat_feed.send("Message")
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Message"

    def test_link_chat_log_objects(self, chat_feed):
        chat_feed.send("Message")
        assert chat_feed._chat_log.objects[0] is chat_feed.value[0]

    def test_send_with_user_avatar(self, chat_feed):
        user = "Bob"
        avatar = "👨"
        entry = chat_feed.send("Message", user=user, avatar=avatar)
        assert entry.user == user
        assert entry.avatar == avatar

    def test_send_dict(self, chat_feed):
        entry = chat_feed.send({"value": "Message", "user": "Bob", "avatar": "👨"})
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Message"
        assert chat_feed.value[0].user == "Bob"
        assert chat_feed.value[0].avatar == "👨"

    def test_send_dict_minimum(self, chat_feed):
        entry = chat_feed.send({"value": "Message"})
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Message"

    def test_send_dict_without_value(self, chat_feed):
        with pytest.raises(ValueError, match="it must contain a 'value' key"):
            chat_feed.send({"user": "Bob", "avatar": "👨"})

    def test_send_dict_with_user_avatar_override(self, chat_feed):
        user = "August"
        avatar = "👩"
        entry = chat_feed.send(
            {"value": "Message", "user": "Bob", "avatar": "👨"},
            user=user,
            avatar=avatar,
        )
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Message"
        assert chat_feed.value[0].user == user
        assert chat_feed.value[0].avatar == avatar

    def test_send_entry(self, chat_feed):
        entry = ChatEntry(value="Message", user="Bob", avatar="👨")
        chat_feed.send(entry)
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Message"
        assert chat_feed.value[0].user == "Bob"
        assert chat_feed.value[0].avatar == "👨"

    def test_send_with_respond(self, chat_feed):
        def callback(contents, user, instance):
            return f"Response to: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Question", respond=True)
        time.sleep(0.75)

        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].value == "Response to: Question"

        chat_feed.respond()
        time.sleep(0.75)

        assert len(chat_feed.value) == 3
        assert chat_feed.value[2].value == "Response to: Response to: Question"

    def test_send_without_respond(self, chat_feed):
        def callback(contents, user, instance):
            return f"Response to: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Question", respond=False)
        time.sleep(0.75)

        assert len(chat_feed.value) == 1

        chat_feed.respond()
        time.sleep(0.75)

        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].value == "Response to: Question"

    def test_respond_without_callback(self, chat_feed):
        chat_feed.respond()  # Should not raise any errors

    def test_stream(self, chat_feed):
        entry = chat_feed.stream("Streaming message", user="Person", avatar="P")
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Streaming message"
        assert chat_feed.value[0].user == "Person"
        assert chat_feed.value[0].avatar == "P"

        updated_entry = chat_feed.stream(
            " Appended message", user="New Person", entry=entry, avatar="N"
        )
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is updated_entry
        assert chat_feed.value[0].value == "Streaming message Appended message"
        assert chat_feed.value[0].user == "New Person"
        assert chat_feed.value[0].avatar == "N"

        new_entry = chat_feed.stream("New message")
        assert len(chat_feed.value) == 2
        assert chat_feed.value[1] is new_entry
        assert chat_feed.value[1].value == "New message"

    def test_stream_with_user_avatar(self, chat_feed):
        user = "Bob"
        avatar = "👨"
        entry = chat_feed.stream(
            "Streaming with user and avatar", user=user, avatar=avatar
        )
        assert entry.user == user
        assert entry.avatar == avatar

    def test_stream_dict(self, chat_feed):
        entry = chat_feed.stream(
            {"value": "Streaming message", "user": "Person", "avatar": "P"}
        )
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Streaming message"
        assert chat_feed.value[0].user == "Person"
        assert chat_feed.value[0].avatar == "P"

    def test_stream_dict_minimum(self, chat_feed):
        entry = chat_feed.stream({"value": "Streaming message"})
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Streaming message"

    def test_stream_dict_without_value(self, chat_feed):
        with pytest.raises(ValueError, match="it must contain a 'value' key"):
            chat_feed.stream({"user": "Person", "avatar": "P"})

    def test_stream_dict_with_user_avatar_override(self, chat_feed):
        user = "Bob"
        avatar = "👨"
        entry = chat_feed.stream(
            {"value": "Streaming message", "user": "Person", "avatar": "P"},
            user=user,
            avatar=avatar,
        )
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Streaming message"
        assert chat_feed.value[0].user == user
        assert chat_feed.value[0].avatar == avatar

    def test_stream_entry(self, chat_feed):
        entry = ChatEntry(value="Streaming message", user="Person", avatar="P")
        chat_feed.stream(entry)
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        assert chat_feed.value[0].value == "Streaming message"
        assert chat_feed.value[0].user == "Person"
        assert chat_feed.value[0].avatar == "P"

    @pytest.mark.parametrize(
        "obj",
        [
            "Some Text",
            TextInput(value="Some Text"),
            HTML("Some Text"),
            Row(HTML("Some Text")),
        ],
    )
    def test_stream_to_nested_entry(self, chat_feed, obj):
        entry = chat_feed.send(
            Row(
                obj,
                Image("https://panel.holoviz.org/_static/logo_horizontal.png"),
            )
        )
        chat_feed.stream(" Added", entry=entry)
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0] is entry
        entry_obj = chat_feed.value[0].value[0]
        if isinstance(entry_obj, Row):
            entry_obj = entry_obj[0]

        if hasattr(entry_obj, "object"):
            assert entry_obj.object == "Some Text Added"
        else:
            assert entry_obj.value == "Some Text Added"

    def test_undo(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")
        entry3 = chat_feed.send("Message 3")

        assert len(chat_feed.value) == 3

        undone_entries = chat_feed.undo()
        assert len(chat_feed.value) == 2
        assert undone_entries == [entry3]

        chat_feed.undo(2)
        assert len(chat_feed.value) == 0

    def test_clear(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")

        assert len(chat_feed.value) == 2

        cleared_entries = chat_feed.clear()
        assert len(chat_feed.value) == 0
        assert cleared_entries[0].value == "Message 1"
        assert cleared_entries[1].value == "Message 2"

    def test_set_entries(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")

        assert len(chat_feed.value) == 2

        chat_feed.value = [ChatEntry(value="Message 3")]
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0].value == "Message 3"

    @pytest.mark.parametrize(["key", "value"], LAYOUT_PARAMETERS.items())
    def test_layout_parameters_are_propogated_to_composite(self, key, value):
        chat_feed = ChatFeed(**{key: value})
        assert getattr(chat_feed, key) == value
        assert getattr(chat_feed._composite, key) == value

    def test_width_entry_offset_80(self, chat_feed):
        """
        Prevent horizontal scroll bars by subtracting 80px
        which is about the width of the avatar
        and reactions.
        """
        chat_feed.width = 500
        chat_feed.send("Message 1")
        assert chat_feed.value[0].width == 420

    @pytest.mark.parametrize(
        "user", ["system", "System", " System", " system ", "system-"]
    )
    def test_default_avatars_default(self, chat_feed, user):
        chat_feed.send("Message 1", user=user)

        assert chat_feed.value[0].user == user
        assert chat_feed.value[0].avatar == "⚙️"

    def test_default_avatars_superseded_in_dict(self, chat_feed):
        chat_feed.send({"user": "System", "avatar": "👨", "value": "Message 1"})

        assert chat_feed.value[0].user == "System"
        assert chat_feed.value[0].avatar == "👨"

    def test_default_avatars_superseded_by_keyword(self, chat_feed):
        chat_feed.send({"user": "System", "value": "Message 1"}, avatar="👨")

        assert chat_feed.value[0].user == "System"
        assert chat_feed.value[0].avatar == "👨"

    def test_default_avatars_superseded_in_entry(self, chat_feed):
        chat_feed.send(
            ChatEntry(**{"user": "System", "avatar": "👨", "value": "Message 1"})
        )

        assert chat_feed.value[0].user == "System"
        assert chat_feed.value[0].avatar == "👨"

    def test_default_avatars_superseded_by_callback_avatar(self, chat_feed):
        def callback(contents, user, instance):
            yield "Message back"

        chat_feed.callback = callback
        chat_feed.callback_user = "System"
        chat_feed.send("Message", respond=True)
        time.sleep(0.2)
        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].user == "System"
        assert chat_feed.value[1].avatar == ChatEntry()._avatar_lookup("System")

    def test_default_avatars_entry_params(self, chat_feed):
        chat_feed.entry_params["default_avatars"] = {"test1": "1"}
        assert chat_feed.send(value="", user="test1").avatar == "1"

        # has default
        assert chat_feed.send(value="", user="system").avatar == "⚙️"

    def test_no_recursion_error(self, chat_feed):
        chat_feed.send("Some time ago, there was a recursion error like this")
        print(chat_feed.value)

    def test_chained_response(self, chat_feed):
        async def callback(contents, user, instance):
            if user == "User":
                yield {
                    "user": "arm",
                    "avatar": "🦾",
                    "value": "Hey, leg! Did you hear the user?",
                }
                instance.respond()
            elif user == "arm":
                user_entry = instance.value[-2]
                user_contents = user_entry.value
                yield {
                    "user": "leg",
                    "avatar": "🦿",
                    "value": f'Yeah! They said "{user_contents}".',
                }

        chat_feed.callback = callback
        chat_feed.send("Testing!", user="User")
        time.sleep(0.75)
        assert chat_feed.value[1].user == "arm"
        assert chat_feed.value[1].avatar == "🦾"
        assert chat_feed.value[1].value == "Hey, leg! Did you hear the user?"
        assert chat_feed.value[2].user == "leg"
        assert chat_feed.value[2].avatar == "🦿"
        assert chat_feed.value[2].value == 'Yeah! They said "Testing!".'

    def test_respond_callback_returns_none(self, chat_feed):
        def callback(contents, user, instance):
            instance.value[0].value = "Mutated"

        chat_feed.callback = callback
        chat_feed.send("Testing!", user="User")
        time.sleep(0.75)
        assert len(chat_feed.value) == 1
        assert chat_feed.value[0].value == "Mutated"

class TestChatFeedCallback:
    @pytest.fixture
    def chat_feed(self) -> ChatFeed:
        return ChatFeed()

    def test_user_avatar(self, chat_feed):
        ChatEntry.default_avatars["bob"] = "👨"

        def echo(contents, user, instance):
            return f"{user}: {contents}"

        chat_feed.callback = echo
        chat_feed.callback_user = "Bob"
        chat_feed.send("Message", respond=True)
        time.sleep(0.75)
        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].user == "Bob"
        assert chat_feed.value[1].avatar == "👨"
        ChatEntry.default_avatars.pop("bob")

    def test_return(self, chat_feed):
        def echo(contents, user, instance):
            return contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        time.sleep(0.75)
        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].value == "Message"

    def test_yield(self, chat_feed):
        def echo(contents, user, instance):
            yield contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        time.sleep(0.75)
        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].value == "Message"

    @pytest.mark.asyncio
    async def test_async_return(self, chat_feed):
        async def echo(contents, user, instance):
            return contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await asyncio.sleep(0.25)
        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].value == "Message"

    @pytest.mark.asyncio
    async def test_async_yield(self, chat_feed):
        async def echo(contents, user, instance):
            yield contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await asyncio.sleep(0.25)
        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].value == "Message"

    @pytest.mark.asyncio
    async def test_generator(self, chat_feed):
        async def echo(contents, user, instance):
            message = ""
            for char in contents:
                message += char
                yield message

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await asyncio.sleep(0.25)
        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].value == "Message"

    @pytest.mark.asyncio
    async def test_async_generator(self, chat_feed):
        async def async_gen(contents):
            for char in contents:
                yield char

        async def echo(contents, user, instance):
            message = ""
            async for char in async_gen(contents):
                message += char
                yield message

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await asyncio.sleep(0.25)
        assert len(chat_feed.value) == 2
        assert chat_feed.value[1].value == "Message"

    def test_placeholder_disabled(self, chat_feed):
        def echo(contents, user, instance):
            time.sleep(0.25)
            yield "hey testing"

        chat_log_mock = MagicMock()
        chat_log_mock.__getitem__.return_value = ChatEntry(value="Message")
        chat_feed.placeholder_threshold = 0
        chat_feed.callback = echo
        chat_feed._chat_log = chat_log_mock
        chat_feed.send("Message", respond=True)
        # only append sent message
        assert chat_log_mock.append.call_count == 2

    def test_placeholder_enabled(self, chat_feed):
        def echo(contents, user, instance):
            time.sleep(0.25)
            yield "hey testing"

        chat_log_mock = MagicMock()
        chat_log_mock.__getitem__.return_value = ChatEntry(value="Message")
        chat_feed.callback = echo
        chat_feed._chat_log = chat_log_mock
        chat_feed.send("Message", respond=True)
        # append sent message and placeholder
        assert chat_log_mock.append.call_count == 3

    def test_placeholder_threshold_under(self, chat_feed):
        async def echo(contents, user, instance):
            await asyncio.sleep(0.25)
            return "hey testing"

        chat_feed.placeholder_threshold = 5
        chat_log_mock = MagicMock()
        chat_log_mock.__getitem__.return_value = ChatEntry(value="Message")
        chat_feed.callback = echo
        chat_feed._chat_log = chat_log_mock
        chat_feed.send("Message", respond=True)
        assert chat_log_mock.append.call_count == 2

    def test_placeholder_threshold_under_generator(self, chat_feed):
        async def echo(contents, user, instance):
            await asyncio.sleep(0.25)
            yield "hey testing"

        chat_feed.placeholder_threshold = 5
        chat_log_mock = MagicMock()
        chat_log_mock.__getitem__.return_value = ChatEntry(value="Message")
        chat_feed.callback = echo
        chat_feed._chat_log = chat_log_mock
        chat_feed.send("Message", respond=True)
        # append sent message and placeholder
        assert chat_log_mock.append.call_count == 2

    def test_placeholder_threshold_exceed(self, chat_feed):
        async def echo(contents, user, instance):
            await asyncio.sleep(0.5)
            yield "hello testing"

        chat_feed.placeholder_threshold = 0.1
        chat_log_mock = MagicMock()
        chat_log_mock.__getitem__.return_value = ChatEntry(value="Message")
        chat_feed.callback = echo
        chat_feed._chat_log = chat_log_mock
        chat_feed.send("Message", respond=True)
        # append sent message and placeholder
        assert chat_log_mock.append.call_count == 3

    def test_placeholder_threshold_exceed_generator(self, chat_feed):
        async def echo(contents, user, instance):
            await asyncio.sleep(0.5)
            yield "hello testing"

        chat_feed.placeholder_threshold = 0.1
        chat_log_mock = MagicMock()
        chat_log_mock.__getitem__.return_value = ChatEntry(value="Message")
        chat_feed.callback = echo
        chat_feed._chat_log = chat_log_mock
        chat_feed.send("Message", respond=True)
        # append sent message and placeholder
        assert chat_log_mock.append.call_count == 3

    def test_placeholder_threshold_sync(self, chat_feed):
        """
        Placeholder should always be appended if the
        callback is synchronous.
        """

        def echo(contents, user, instance):
            time.sleep(0.25)
            yield "hey testing"

        chat_feed.placeholder_threshold = 5
        chat_log_mock = MagicMock()
        chat_log_mock.__getitem__.return_value = ChatEntry(value="Message")
        chat_feed.callback = echo
        chat_feed._chat_log = chat_log_mock
        chat_feed.send("Message", respond=True)
        # append sent message and placeholder
        assert chat_log_mock.append.call_count == 3

    def test_renderers_pane(self, chat_feed):
        chat_feed.renderers = [HTML]
        chat_feed.send("Hello!")
        html = chat_feed.value[0]._value_panel
        assert isinstance(html, HTML)
        assert html.object == "Hello!"
        assert html.sizing_mode is None

    def test_renderers_widget(self, chat_feed):
        chat_feed.renderers = [TextAreaInput]
        chat_feed.send("Hello!")
        area_input = chat_feed.value[0]._render_value()
        assert isinstance(area_input, TextAreaInput)
        assert area_input.value == "Hello!"
        assert area_input.height == 500
        assert area_input.sizing_mode is None

    def test_renderers_custom_callable(self, chat_feed):
        def renderer(value):
            return Column(value, LinearGauge(value=int(value), width=100))

        chat_feed.renderers = [renderer]
        chat_feed.send(1)
        column = chat_feed.value[0]._value_panel
        assert isinstance(column, Column)
        number = column[0]
        gauge = column[1]
        assert number.object == 1
        assert number.sizing_mode is None
        assert isinstance(gauge, LinearGauge)
        assert gauge.value == 1
        assert gauge.width == 100
        assert gauge.sizing_mode == "fixed"

    def test_callback_exception(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "summary"
        chat_feed.send("Message", respond=True)
        assert chat_feed.value[-1].value == "division by zero"
        assert chat_feed.value[-1].user == "Exception"

    def test_callback_exception_traceback(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "verbose"
        chat_feed.send("Message", respond=True)
        assert chat_feed.value[-1].value.startswith(
            "```python\nTraceback (most recent call last):"
        )
        assert chat_feed.value[-1].user == "Exception"

    def test_callback_exception_ignore(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "ignore"
        chat_feed.send("Message", respond=True)
        assert len(chat_feed.value) == 1

    def test_callback_exception_raise(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "raise"
        with pytest.raises(ZeroDivisionError, match="division by zero"):
            chat_feed.send("Message", respond=True)
        assert len(chat_feed.value) == 1


class TestChatInterfaceWidgetsSizingMode:
    def test_none(self):
        chat_interface = ChatInterface()
        assert chat_interface.sizing_mode is None
        assert chat_interface._chat_log.sizing_mode is None
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_fixed(self):
        chat_interface = ChatInterface(sizing_mode="fixed")
        assert chat_interface.sizing_mode == "fixed"
        assert chat_interface._chat_log.sizing_mode == "fixed"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_stretch_both(self):
        chat_interface = ChatInterface(sizing_mode="stretch_both")
        assert chat_interface.sizing_mode == "stretch_both"
        assert chat_interface._chat_log.sizing_mode == "stretch_both"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_stretch_width(self):
        chat_interface = ChatInterface(sizing_mode="stretch_width")
        assert chat_interface.sizing_mode == "stretch_width"
        assert chat_interface._chat_log.sizing_mode == "stretch_width"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_stretch_height(self):
        chat_interface = ChatInterface(sizing_mode="stretch_height")
        assert chat_interface.sizing_mode == "stretch_height"
        assert chat_interface._chat_log.sizing_mode == "stretch_height"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_scale_both(self):
        chat_interface = ChatInterface(sizing_mode="scale_both")
        assert chat_interface.sizing_mode == "scale_both"
        assert chat_interface._chat_log.sizing_mode == "scale_both"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_scale_width(self):
        chat_interface = ChatInterface(sizing_mode="scale_width")
        assert chat_interface.sizing_mode == "scale_width"
        assert chat_interface._chat_log.sizing_mode == "scale_width"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"

    def test_scale_height(self):
        chat_interface = ChatInterface(sizing_mode="scale_height")
        assert chat_interface.sizing_mode == "scale_height"
        assert chat_interface._chat_log.sizing_mode == "scale_height"
        assert chat_interface._input_layout.sizing_mode == "stretch_width"
        assert chat_interface._input_layout[0].sizing_mode == "stretch_width"


class TestChatInterface:
    @pytest.fixture
    def chat_interface(self):
        return ChatInterface()

    def test_init(self, chat_interface):
        assert len(chat_interface._button_data) == 4
        assert len(chat_interface._widgets) == 1
        assert isinstance(chat_interface._input_layout, Row)
        assert isinstance(chat_interface._widgets["TextInput"], TextInput)

        assert chat_interface.active == -1

        # Buttons added to input layout
        inputs = chat_interface._input_layout
        for index, button_data in enumerate(chat_interface._button_data.values()):
            widget = inputs[index + 1]
            assert isinstance(widget, Button)
            assert widget.name == button_data.name.title()

    def test_init_custom_widgets(self):
        widgets = [TextInput(name="Text"), FileInput()]
        chat_interface = ChatInterface(widgets=widgets)
        assert len(chat_interface._widgets) == 2
        assert isinstance(chat_interface._input_layout, Tabs)
        assert isinstance(chat_interface._widgets["Text"], TextInput)
        assert isinstance(chat_interface._widgets["FileInput"], FileInput)
        assert chat_interface.active == 0

    def test_active_in_constructor(self):
        widgets = [TextInput(name="Text"), FileInput()]
        chat_interface = ChatInterface(widgets=widgets, active=1)
        assert chat_interface.active == 1

    def test_file_input_only(self):
        ChatInterface(widgets=[FileInput(name="CSV File", accept=".csv")])

    def test_active_widget(self, chat_interface):
        active_widget = chat_interface.active_widget
        assert isinstance(active_widget, TextInput)

    def test_active(self):
        widget = TextInput(name="input")
        chat_interface = ChatInterface(widgets=[widget])
        assert chat_interface.active == -1

    def test_active_multiple_widgets(self, chat_interface):
        widget1 = TextInput(name="input1")
        widget2 = TextInput(name="input2")
        chat_interface.widgets = [widget1, widget2]
        assert chat_interface.active == 0

        chat_interface.active = 1
        assert chat_interface.active == 1
        assert isinstance(chat_interface.active_widget, TextInput)

    def test_click_send(self, chat_interface: ChatInterface):
        chat_interface.widgets = [TextAreaInput()]
        chat_interface.active_widget.value = "Message"
        assert len(chat_interface.value) == 1
        assert chat_interface.value[0].value == "Message"

    def test_click_undo(self, chat_interface):
        chat_interface.user = "User"
        chat_interface.send("Message 1")
        chat_interface.send("Message 2")
        chat_interface.send("Message 3", user="Assistant")
        expected = chat_interface.value[-2:].copy()
        chat_interface._click_undo(None)
        assert len(chat_interface.value) == 1
        assert chat_interface.value[0].value == "Message 1"
        assert chat_interface._button_data["undo"].objects == expected

        # revert
        chat_interface._click_undo(None)
        assert len(chat_interface.value) == 3
        assert chat_interface.value[0].value == "Message 1"
        assert chat_interface.value[1].value == "Message 2"
        assert chat_interface.value[2].value == "Message 3"

    def test_click_clear(self, chat_interface):
        chat_interface.send("Message 1")
        chat_interface.send("Message 2")
        chat_interface.send("Message 3")
        expected = chat_interface.value.copy()
        chat_interface._click_clear(None)
        assert len(chat_interface.value) == 0
        assert chat_interface._button_data["clear"].objects == expected

    def test_click_rerun(self, chat_interface):
        self.count = 0

        def callback(contents, user, instance):
            self.count += 1
            return self.count

        chat_interface.callback = callback
        chat_interface.send("Message 1")
        assert chat_interface.value[1].value == 1
        chat_interface._click_rerun(None)
        assert chat_interface.value[1].value == 2

    def test_click_rerun_null(self, chat_interface):
        chat_interface._click_rerun(None)
        assert len(chat_interface.value) == 0

    def test_replace_widgets(self, chat_interface):
        assert isinstance(chat_interface._input_layout, Row)

        chat_interface.widgets = [TextAreaInput(), FileInput()]
        assert len(chat_interface._widgets) == 2
        assert isinstance(chat_interface._input_layout, Tabs)
        assert isinstance(chat_interface._widgets["TextAreaInput"], TextAreaInput)
        assert isinstance(chat_interface._widgets["FileInput"], FileInput)

    def test_reset_on_send(self, chat_interface):
        chat_interface.active_widget.value = "Hello"
        chat_interface.reset_on_send = True
        chat_interface._click_send(None)
        assert chat_interface.active_widget.value == ""

    def test_reset_on_send_text_area(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        chat_interface.active_widget.value = "Hello"
        chat_interface.reset_on_send = False
        chat_interface._click_send(None)
        assert chat_interface.active_widget.value == "Hello"

    def test_widgets_supports_list_and_widget(self, chat_interface):
        chat_interface.widgets = TextAreaInput()
        chat_interface.widgets = [TextAreaInput(), FileInput]

    def test_show_button_name_width(self, chat_interface):
        assert chat_interface.show_button_name
        assert chat_interface.width is None
        chat_interface.width = 200
        assert not chat_interface.show_button_name
