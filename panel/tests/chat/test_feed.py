import asyncio
import time

import pytest

from panel.chat.feed import ChatFeed
from panel.chat.message import ChatMessage
from panel.layout import Column, Row
from panel.pane.image import Image
from panel.pane.markup import HTML
from panel.tests.util import async_wait_until, wait_until
from panel.widgets.indicators import LinearGauge
from panel.widgets.input import TextAreaInput, TextInput

LAYOUT_PARAMETERS = {
    "sizing_mode": "stretch_height",
    "height": 201,
    "max_height": 301,
    "width": 101,
    "max_width": 201,
}


@pytest.fixture
def chat_feed():
    return ChatFeed()


@pytest.mark.xdist_group("chat")
class TestChatFeed:

    def test_hide_header(self, chat_feed):
        assert chat_feed.header is None

        chat_feed.header = "# Header"
        assert not chat_feed._card.hide_header

        chat_feed.header = None
        assert chat_feed._card.hide_header

        chat_feed.header = ""
        assert chat_feed._card.hide_header

    def test_card_params(self, chat_feed):
        chat_feed.card_params = {
            "header_background": "red",
            "header": "Test",
            "hide_header": False
        }
        assert chat_feed._card.header_background == "red"
        assert chat_feed._card.header == "Test"
        assert not chat_feed._card.hide_header

    def test_send(self, chat_feed):
        message = chat_feed.send("Message")
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"

    def test_link_chat_log_objects(self, chat_feed):
        chat_feed.send("Message")
        assert chat_feed._chat_log.objects[0] is chat_feed.objects[0]

    def test_send_with_user_avatar(self, chat_feed):
        user = "Bob"
        avatar = "👨"
        message = chat_feed.send("Message", user=user, avatar=avatar)
        assert message.user == user
        assert message.avatar == avatar

    def test_send_dict(self, chat_feed):
        message = chat_feed.send({"object": "Message", "user": "Bob", "avatar": "👨"})
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"
        assert chat_feed.objects[0].user == "Bob"
        assert chat_feed.objects[0].avatar == "👨"

    @pytest.mark.parametrize("key", ["value", "object"])
    def test_send_dict_minimum(self, chat_feed, key):
        message = chat_feed.send({key: "Message"})
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"

    def test_send_dict_without_object(self, chat_feed):
        with pytest.raises(ValueError, match="it must contain an 'object' key"):
            chat_feed.send({"user": "Bob", "avatar": "👨"})

    def test_send_dict_with_value_and_object(self, chat_feed):
        with pytest.raises(ValueError, match="both 'value' and 'object'"):
            chat_feed.send({"value": "hey", "object": "hi", "user": "Bob", "avatar": "👨"})

    def test_send_dict_with_user_avatar_override(self, chat_feed):
        user = "August"
        avatar = "👩"
        message = chat_feed.send(
            {"object": "Message", "user": "Bob", "avatar": "👨"},
            user=user,
            avatar=avatar,
        )
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"
        assert chat_feed.objects[0].user == user
        assert chat_feed.objects[0].avatar == avatar

    def test_send_entry(self, chat_feed):
        message = ChatMessage("Message", user="Bob", avatar="👨")
        chat_feed.send(message)
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"
        assert chat_feed.objects[0].user == "Bob"
        assert chat_feed.objects[0].avatar == "👨"

    def test_send_with_respond(self, chat_feed):
        def callback(contents, user, instance):
            return f"Response to: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Question", respond=True)

        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Response to: Question"

        chat_feed.respond()

        wait_until(lambda: len(chat_feed.objects) == 3)
        assert chat_feed.objects[2].object == "Response to: Response to: Question"

    def test_send_without_respond(self, chat_feed):
        def callback(contents, user, instance):
            return f"Response to: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Question", respond=False)

        wait_until(lambda: len(chat_feed.objects) == 1)

        chat_feed.respond()

        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Response to: Question"

    def test_respond_without_callback(self, chat_feed):
        chat_feed.respond()  # Should not raise any errors

    def test_stream(self, chat_feed):
        message = chat_feed.stream("Streaming message", user="Person", avatar="P")
        assert len(chat_feed.objects) == 1
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Streaming message"
        assert chat_feed.objects[0].user == "Person"
        assert chat_feed.objects[0].avatar == "P"

        updated_entry = chat_feed.stream(
            " Appended message", user="New Person", message=message, avatar="N"
        )
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is updated_entry
        assert chat_feed.objects[0].object == "Streaming message Appended message"
        assert chat_feed.objects[0].user == "New Person"
        assert chat_feed.objects[0].avatar == "N"

        new_entry = chat_feed.stream("New message")
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1] is new_entry
        assert chat_feed.objects[1].object == "New message"

    def test_stream_with_user_avatar(self, chat_feed):
        user = "Bob"
        avatar = "👨"
        message = chat_feed.stream(
            "Streaming with user and avatar", user=user, avatar=avatar
        )
        assert message.user == user
        assert message.avatar == avatar

    def test_stream_dict(self, chat_feed):
        message = chat_feed.stream(
            {"object": "Streaming message", "user": "Person", "avatar": "P"}
        )
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Streaming message"
        assert chat_feed.objects[0].user == "Person"
        assert chat_feed.objects[0].avatar == "P"

    def test_stream_dict_minimum(self, chat_feed):
        message = chat_feed.stream({"object": "Streaming message"})
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Streaming message"

    def test_stream_dict_without_value(self, chat_feed):
        with pytest.raises(ValueError, match="it must contain an 'object' key"):
            chat_feed.stream({"user": "Person", "avatar": "P"})

    def test_stream_dict_with_user_avatar_override(self, chat_feed):
        user = "Bob"
        avatar = "👨"
        message = chat_feed.stream(
            {"object": "Streaming message", "user": "Person", "avatar": "P"},
            user=user,
            avatar=avatar,
        )
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Streaming message"
        assert chat_feed.objects[0].user == user
        assert chat_feed.objects[0].avatar == avatar

    def test_stream_entry(self, chat_feed):
        message = ChatMessage("Streaming message", user="Person", avatar="P")
        chat_feed.stream(message)
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Streaming message"
        assert chat_feed.objects[0].user == "Person"
        assert chat_feed.objects[0].avatar == "P"

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
        message = chat_feed.send(
            Row(
                obj,
                Image("https://panel.holoviz.org/_static/logo_horizontal.png"),
            )
        )
        chat_feed.stream(" Added", message=message)
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        message_obj = chat_feed.objects[0].object[0]
        if isinstance(message_obj, Row):
            message_obj = message_obj[0]

        if hasattr(message_obj, "object"):
            assert message_obj.object == "Some Text Added"
        elif hasattr(message_obj, "value"):
            assert message_obj.value == "Some Text Added"
        else:
            assert message_obj.objects == "Some Text Added"

    def test_undo(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")
        entry3 = chat_feed.send("Message 3")

        wait_until(lambda: len(chat_feed.objects) == 3)

        undone_entries = chat_feed.undo()
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert undone_entries == [entry3]

        chat_feed.undo(2)
        wait_until(lambda: len(chat_feed.objects) == 0)

    def test_clear(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")

        wait_until(lambda: len(chat_feed.objects) == 2)

        cleared_entries = chat_feed.clear()
        wait_until(lambda: len(chat_feed.objects) == 0)
        assert cleared_entries[0].object == "Message 1"
        assert cleared_entries[1].object == "Message 2"

    def test_set_entries(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")

        wait_until(lambda: len(chat_feed.objects) == 2)

        chat_feed.objects = [ChatMessage("Message 3")]
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0].object == "Message 3"

    @pytest.mark.parametrize(["key", "value"], LAYOUT_PARAMETERS.items())
    def test_layout_parameters_are_propogated_to_card(self, key, value):
        chat_feed = ChatFeed(**{key: value})
        assert getattr(chat_feed, key) == value
        assert getattr(chat_feed._card, key) == value

    def test_width_message_offset_80(self, chat_feed):
        """
        Prevent horizontal scroll bars by subtracting 80px
        which is about the width of the avatar
        and reactions.
        """
        chat_feed.width = 500
        chat_feed.send("Message 1")
        assert chat_feed.objects[0].width == 420

    @pytest.mark.parametrize(
        "user", ["system", "System", " System", " system ", "system-"]
    )
    def test_default_avatars_default(self, chat_feed, user):
        chat_feed.send("Message 1", user=user)

        assert chat_feed.objects[0].user == user
        assert chat_feed.objects[0].avatar == "⚙️"

    def test_default_avatars_superseded_in_dict(self, chat_feed):
        chat_feed.send({"user": "System", "avatar": "👨", "value": "Message 1"})

        assert chat_feed.objects[0].user == "System"
        assert chat_feed.objects[0].avatar == "👨"

    def test_default_avatars_superseded_by_keyword(self, chat_feed):
        chat_feed.send({"user": "System", "value": "Message 1"}, avatar="👨")

        assert chat_feed.objects[0].user == "System"
        assert chat_feed.objects[0].avatar == "👨"

    def test_default_avatars_superseded_in_entry(self, chat_feed):
        chat_feed.send(
            ChatMessage(user="System", avatar="👨", object="Message 1")
        )

        assert chat_feed.objects[0].user == "System"
        assert chat_feed.objects[0].avatar == "👨"

    def test_default_avatars_superseded_by_callback_avatar(self, chat_feed):
        def callback(contents, user, instance):
            yield "Message back"

        chat_feed.callback = callback
        chat_feed.callback_user = "System"
        chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].user == "System"
        assert chat_feed.objects[1].avatar == ChatMessage()._avatar_lookup("System")

    def test_default_avatars_message_params(self, chat_feed):
        chat_feed.message_params["default_avatars"] = {"test1": "1"}
        assert chat_feed.send(value="", user="test1").avatar == "1"

        # has default
        assert chat_feed.send(value="", user="system").avatar == "⚙️"

    def test_no_recursion_error(self, chat_feed):
        chat_feed.send("Some time ago, there was a recursion error like this")

    @pytest.mark.asyncio
    async def test_chained_response(self, chat_feed):
        async def callback(contents, user, instance):
            if user == "User":
                yield {
                    "user": "arm",
                    "avatar": "🦾",
                    "value": "Hey, leg! Did you hear the user?",
                }
                instance.respond()
            elif user == "arm":
                for user_entry in instance.objects:
                    if user_entry.user == "User":
                        break
                user_contents = user_entry.object
                yield {
                    "user": "leg",
                    "avatar": "🦿",
                    "value": f'Yeah! They said "{user_contents}".',
                }

        chat_feed.callback = callback
        chat_feed.send("Testing!", user="User")
        await async_wait_until(lambda: len(chat_feed.objects) == 3)
        assert chat_feed.objects[1].user == "arm"
        assert chat_feed.objects[1].avatar == "🦾"
        assert chat_feed.objects[1].object == "Hey, leg! Did you hear the user?"
        assert chat_feed.objects[2].user == "leg"
        assert chat_feed.objects[2].avatar == "🦿"
        assert chat_feed.objects[2].object == 'Yeah! They said "Testing!".'

    def test_respond_callback_returns_none(self, chat_feed):
        def callback(contents, user, instance):
            instance.objects[0].object = "Mutated"

        chat_feed.callback = callback
        chat_feed.send("Testing!", user="User")
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0].object == "Mutated"

    def test_forward_message_params(self, chat_feed):
        chat_feed = ChatFeed(reaction_icons={"like": "thumb-up"}, reactions=["like"])
        chat_feed.send("Hey!")
        chat_message = chat_feed.objects[0]
        assert chat_feed.message_params == {"reaction_icons": {"like": "thumb-up"}, "reactions": ["like"]}
        assert chat_message.object == "Hey!"
        assert chat_message.reactions == ["like"]
        assert chat_message.reaction_icons.options == {"like": "thumb-up"}


@pytest.mark.xdist_group("chat")
class TestChatFeedCallback:

    def test_user_avatar(self, chat_feed):
        ChatMessage.default_avatars["bob"] = "👨"

        def echo(contents, user, instance):
            return f"{user}: {contents}"

        chat_feed.callback = echo
        chat_feed.callback_user = "Bob"
        chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].user == "Bob"
        assert chat_feed.objects[1].avatar == "👨"
        ChatMessage.default_avatars.pop("bob")

    def test_return(self, chat_feed):
        def echo(contents, user, instance):
            return contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"

    @pytest.mark.parametrize("callback_user", [None, "Bob"])
    @pytest.mark.parametrize("callback_avatar", [None, "C"])
    def test_return_chat_message(self, chat_feed, callback_user, callback_avatar):
        def echo(contents, user, instance):
            message_kwargs = {}
            if callback_user:
                message_kwargs["user"] = callback_user
            if callback_avatar:
                message_kwargs["avatar"] = callback_avatar
            return ChatMessage(object=contents, **message_kwargs)

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"
        assert chat_feed.objects[1].user == callback_avatar or "Assistant"
        assert chat_feed.objects[1].avatar == callback_avatar or "🤖"

    def test_yield(self, chat_feed):
        def echo(contents, user, instance):
            yield contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"

    @pytest.mark.asyncio
    async def test_async_return(self, chat_feed):
        async def echo(contents, user, instance):
            return contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"

    @pytest.mark.parametrize("callback_user", [None, "Bob"])
    @pytest.mark.parametrize("callback_avatar", [None, "C"])
    def test_yield_chat_message(self, chat_feed, callback_user, callback_avatar):
        def echo(contents, user, instance):
            message_kwargs = {}
            if callback_user:
                message_kwargs["user"] = callback_user
            if callback_avatar:
                message_kwargs["avatar"] = callback_avatar
            yield ChatMessage(object=contents, **message_kwargs)

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"
        assert chat_feed.objects[1].user == callback_avatar or "Assistant"
        assert chat_feed.objects[1].avatar == callback_avatar or "🤖"

    @pytest.mark.parametrize("callback_user", [None, "Bob"])
    @pytest.mark.parametrize("callback_avatar", [None, "C"])
    def test_yield_chat_message_stream(self, chat_feed, callback_user, callback_avatar):
        def echo(contents, user, instance):
            message_kwargs = {}
            if callback_user:
                message_kwargs["user"] = callback_user
            if callback_avatar:
                message_kwargs["avatar"] = callback_avatar
            message = ""
            for char in contents:
                message += char
                yield ChatMessage(object=message, **message_kwargs)

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"
        assert chat_feed.objects[1].user == callback_avatar or "Assistant"
        assert chat_feed.objects[1].avatar == callback_avatar or "🤖"

    @pytest.mark.asyncio
    async def test_async_yield(self, chat_feed):
        async def echo(contents, user, instance):
            yield contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert len(chat_feed.objects) == 2
        assert chat_feed.objects[1].object == "Message"

    @pytest.mark.asyncio
    def test_generator(self, chat_feed):
        async def echo(contents, user, instance):
            message = ""
            for char in contents:
                message += char
                yield message
                assert instance.objects[-1].show_activity_dot

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 2)
        assert len(chat_feed.objects) == 2
        assert chat_feed.objects[1].object == "Message"
        assert not chat_feed.objects[-1].show_activity_dot

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
                assert instance.objects[-1].show_activity_dot

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"
        assert not chat_feed.objects[-1].show_activity_dot

    def test_placeholder_disabled(self, chat_feed):
        def echo(contents, user, instance):
            time.sleep(1.25)
            assert instance._placeholder not in instance._chat_log
            return "hey testing"

        chat_feed.placeholder_threshold = 0
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log

    def test_placeholder_enabled(self, chat_feed):
        def echo(contents, user, instance):
            time.sleep(1.25)
            assert instance._placeholder in instance._chat_log
            return chat_feed.stream("hey testing")

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log
        # append sent message and placeholder

    def test_placeholder_threshold_under(self, chat_feed):
        async def echo(contents, user, instance):
            await asyncio.sleep(0.25)
            assert instance._placeholder not in instance._chat_log
            return "hey testing"

        chat_feed.placeholder_threshold = 5
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log

    def test_placeholder_threshold_under_generator(self, chat_feed):
        async def echo(contents, user, instance):
            assert instance._placeholder not in instance._chat_log
            await asyncio.sleep(0.25)
            assert instance._placeholder not in instance._chat_log
            yield "hey testing"

        chat_feed.placeholder_threshold = 5
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)

    def test_placeholder_threshold_exceed(self, chat_feed):
        async def echo(contents, user, instance):
            await asyncio.sleep(0.5)
            assert instance._placeholder in instance._chat_log
            return "hello testing"

        chat_feed.placeholder_threshold = 0.1
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log

    def test_placeholder_threshold_exceed_generator(self, chat_feed):
        async def echo(contents, user, instance):
            assert instance._placeholder not in instance._chat_log
            await asyncio.sleep(0.5)
            assert instance._placeholder in instance._chat_log
            yield "hello testing"
            assert instance._placeholder not in instance._chat_log

        chat_feed.placeholder_threshold = 0.2
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log

    def test_renderers_pane(self, chat_feed):
        chat_feed.renderers = [HTML]
        chat_feed.send("Hello!")
        html = chat_feed.objects[0]._object_panel
        assert isinstance(html, HTML)
        assert html.object == "Hello!"
        assert html.sizing_mode is None

    def test_renderers_widget(self, chat_feed):
        chat_feed.renderers = [TextAreaInput]
        chat_feed.send("Hello!")
        area_input = chat_feed[0]._update_object_pane()
        area_input = chat_feed[0]._object_panel
        assert isinstance(area_input, TextAreaInput)
        assert area_input.value == "Hello!"
        assert area_input.height == 500
        assert area_input.sizing_mode is None

    def test_renderers_custom_callable(self, chat_feed):
        def renderer(value):
            return Column(value, LinearGauge(value=int(value), width=100))

        chat_feed.renderers = [renderer]
        chat_feed.send(1)
        column = chat_feed.objects[0]._object_panel
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
        assert "division by zero" in chat_feed.objects[-1].object
        assert chat_feed.objects[-1].user == "Exception"

    def test_callback_exception_traceback(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "verbose"
        chat_feed.send("Message", respond=True)
        assert chat_feed.objects[-1].object.startswith(
            "```python\nTraceback (most recent call last):"
        )
        assert chat_feed.objects[-1].user == "Exception"

    def test_callback_exception_ignore(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "ignore"
        chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 1)

    def test_callback_exception_raise(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "raise"
        with pytest.raises(ZeroDivisionError, match="division by zero"):
            chat_feed.send("Message", respond=True)
        wait_until(lambda: len(chat_feed.objects) == 1)

    def test_callback_stop_async_generator(self, chat_feed):
        async def callback(msg, user, instance):
            yield "A"
            assert chat_feed.stop()
            await asyncio.sleep(0.5)
            yield "B"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        # use sleep here instead of wait for because
        # the callback is timed and I want to confirm stop works
        time.sleep(1)
        assert chat_feed.objects[-1].object == "A"

    def test_callback_stop_async_function(self, chat_feed):
        async def callback(msg, user, instance):
            message = instance.stream("A")
            assert chat_feed.stop()
            await asyncio.sleep(0.5)
            instance.stream("B", message=message)

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        # use sleep here instead of wait for because
        # the callback is timed and I want to confirm stop works
        time.sleep(1)
        assert chat_feed.objects[-1].object == "A"

    def test_callback_stop_sync_function(self, chat_feed):
        def callback(msg, user, instance):
            message = instance.stream("A")
            assert chat_feed.stop()
            time.sleep(0.5)
            instance.stream("B", message=message)  # should not reach this point

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        # use sleep here instead of wait for because
        # the callback is timed and I want to confirm stop works
        time.sleep(1)
        assert chat_feed.objects[-1].object == "A"


@pytest.mark.xdist_group("chat")
class TestChatFeedSerializeForTransformers:

    def test_defaults(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="user")
        chat_feed.send("I'm the assistant", user="assistant")
        chat_feed.send("I'm a bot", user="bot")
        assert chat_feed.serialize() == [
            {"role": "user", "content": "I'm a user"},
            {"role": "assistant", "content": "I'm the assistant"},
            {"role": "assistant", "content": "I'm a bot"},
        ]

    def test_empty(self):
        chat_feed = ChatFeed()
        assert chat_feed.serialize() == []

    def test_case_insensitivity(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="USER")
        chat_feed.send("I'm the assistant", user="ASSISTant")
        chat_feed.send("I'm a bot", user="boT")
        assert chat_feed.serialize() == [
            {"role": "user", "content": "I'm a user"},
            {"role": "assistant", "content": "I'm the assistant"},
            {"role": "assistant", "content": "I'm a bot"},
        ]

    def test_default_role(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="user")
        chat_feed.send("I'm the assistant", user="assistant")
        chat_feed.send("I'm a bot", user="bot")
        assert chat_feed.serialize(default_role="system") == [
            {"role": "user", "content": "I'm a user"},
            {"role": "assistant", "content": "I'm the assistant"},
            {"role": "system", "content": "I'm a bot"},
        ]

    def test_empty_default_role(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="user")
        chat_feed.send("I'm the assistant", user="assistant")
        chat_feed.send("I'm a bot", user="bot")
        with pytest.raises(ValueError, match="not found in role_names"):
            chat_feed.serialize(default_role="")

    def test_role_names(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm the user", user="Andrew")
        chat_feed.send("I'm another user", user="August")
        chat_feed.send("I'm the assistant", user="Bot")
        role_names = {"user": ["Andrew", "August"], "assistant": "Bot"}
        assert chat_feed.serialize(role_names=role_names) == [
            {"role": "user", "content": "I'm the user"},
            {"role": "user", "content": "I'm another user"},
            {"role": "assistant", "content": "I'm the assistant"},
        ]

    def test_custom_serializer(self):
        def custom_serializer(obj):
            if isinstance(obj, str):
                return "new string"
            else:
                return "0"

        chat_feed = ChatFeed()
        chat_feed.send("I'm the user", user="user")
        chat_feed.send(3, user="assistant")
        assert chat_feed.serialize(custom_serializer=custom_serializer) == [
            {"role": "user", "content": "new string"},
            {"role": "assistant", "content": "0"},
        ]

    def test_custom_serializer_invalid_output(self):
        def custom_serializer(obj):
            if isinstance(obj, str):
                return "new string"
            else:
                return 0

        chat_feed = ChatFeed()
        chat_feed.send("I'm the user", user="user")
        chat_feed.send(3, user="assistant")
        with pytest.raises(ValueError, match="must return a string"):
            chat_feed.serialize(custom_serializer=custom_serializer)

    def test_serialize_filter_by(self, chat_feed):
        def filter_by_reactions(messages):
            return [obj for obj in messages if "favorite" in obj.reactions]

        chat_feed.send(ChatMessage("no"))
        chat_feed.send(ChatMessage("yes", reactions=["favorite"]))
        filtered = chat_feed.serialize(filter_by=filter_by_reactions)
        assert len(filtered) == 1
        assert filtered[0]["content"] == "yes"


@pytest.mark.xdist_group("chat")
class TestChatFeedSerializeBase:

    def test_transformers_format(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="user")
        chat_feed.send("I'm the assistant", user="assistant")
        chat_feed.send("I'm a bot", user="bot")
        assert chat_feed.serialize(format="transformers") == [
            {"role": "user", "content": "I'm a user"},
            {"role": "assistant", "content": "I'm the assistant"},
            {"role": "assistant", "content": "I'm a bot"},
        ]

    def test_invalid(self):
        with pytest.raises(NotImplementedError, match="is not supported"):
            chat_feed = ChatFeed()
            chat_feed.send("I'm a user", user="user")
            chat_feed.serialize(format="atransform")
