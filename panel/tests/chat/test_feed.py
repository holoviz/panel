import asyncio
import time

from unittest.mock import MagicMock

import pytest

from panel.chat.entry import ChatEntry
from panel.chat.feed import ChatFeed
from panel.layout import Column, Row
from panel.pane.image import Image
from panel.pane.markup import HTML
from panel.widgets.indicators import LinearGauge
from panel.widgets.input import TextAreaInput, TextInput

LAYOUT_PARAMETERS = {
    "sizing_mode": "stretch_height",
    "height": 201,
    "max_height": 301,
    "width": 101,
    "max_width": 201,
}


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
