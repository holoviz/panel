import asyncio
import time

import pytest

from panel.chat.feed import ChatFeed
from panel.chat.icon import ChatReactionIcons
from panel.chat.message import DEFAULT_AVATARS, ChatMessage
from panel.chat.step import ChatStep
from panel.chat.utils import avatar_lookup
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

ChatFeed.callback_exception = "raise"  # type: ignore


@pytest.fixture
def chat_feed():
    return ChatFeed()


@pytest.mark.xdist_group("chat")
class TestChatFeed:

    def test_init_with_help_text(self):
        chat_feed = ChatFeed(help_text="Instructions")
        message = chat_feed.objects[0]
        assert message.object == "Instructions"
        assert message.user == "Help"

    def test_init_with_loading(self):
        chat_feed = ChatFeed(loading=True)
        assert chat_feed._placeholder in chat_feed._chat_log
        chat_feed.loading = False
        assert chat_feed._placeholder not in chat_feed._chat_log

    def test_update_header(self):
        chat_feed = ChatFeed(header="1")
        assert chat_feed._card.header.object == "1"
        chat_feed.header = "2"
        assert chat_feed._card.header.object == "2"
        chat_feed.header = HTML("<b>3</b>")
        assert chat_feed._card.header.object == "<b>3</b>"

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
        assert chat_feed._card.header.object == "Test"
        assert not chat_feed._card.hide_header

    async def test_send(self, chat_feed):
        message = chat_feed.send("Message", footer_objects=[HTML("Footer")])
        assert len(chat_feed.objects) == 1
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"
        assert chat_feed.objects[0].footer_objects[0].object == "Footer"

    async def test_link_chat_log_objects(self, chat_feed):
        chat_feed.send("Message")
        assert chat_feed._chat_log.objects[0] is chat_feed.objects[0]

    async def test_send_with_user_avatar(self, chat_feed):
        user = "Bob"
        avatar = "👨"
        message = chat_feed.send("Message", user=user, avatar=avatar)
        assert message.user == user
        assert message.avatar == avatar

    async def test_send_dict(self, chat_feed):
        message = chat_feed.send({"object": "Message", "user": "Bob", "avatar": "👨"})
        assert len(chat_feed.objects) == 1
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"
        assert chat_feed.objects[0].user == "Bob"
        assert chat_feed.objects[0].avatar == "👨"

    @pytest.mark.parametrize("key", ["value", "object"])
    async def test_send_dict_minimum(self, chat_feed, key):
        message = chat_feed.send({key: "Message"})
        assert len(chat_feed.objects) == 1
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"

    async def test_send_dict_without_object(self, chat_feed):
        with pytest.raises(ValueError, match="it must contain an 'object' key"):
            chat_feed.send({"user": "Bob", "avatar": "👨"})

    async def test_send_dict_with_value_and_object(self, chat_feed):
        with pytest.raises(ValueError, match="both 'value' and 'object'"):
            chat_feed.send({"value": "hey", "object": "hi", "user": "Bob", "avatar": "👨"})

    async def test_send_dict_with_user_avatar_override(self, chat_feed):
        user = "August"
        avatar = "👩"
        message = chat_feed.send(
            {"object": "Message", "user": "Bob", "avatar": "👨"},
            user=user,
            avatar=avatar,
        )
        assert len(chat_feed.objects) == 1
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"
        assert chat_feed.objects[0].user == user
        assert chat_feed.objects[0].avatar == avatar

    async def test_send_entry(self, chat_feed):
        message = ChatMessage("Message", user="Bob", avatar="👨")
        chat_feed.send(message)
        assert len(chat_feed.objects) == 1
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Message"
        assert chat_feed.objects[0].user == "Bob"
        assert chat_feed.objects[0].avatar == "👨"

    async def test_send_with_respond(self, chat_feed):
        def callback(contents, user, instance):
            return f"Response to: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Question", respond=True)

        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Response to: Question"

        chat_feed.respond()

        await async_wait_until(lambda: len(chat_feed.objects) == 3)
        assert chat_feed.objects[2].object == "Response to: Response to: Question"

    async def test_send_without_respond(self, chat_feed):
        def callback(contents, user, instance):
            return f"Response to: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Question", respond=False)

        assert len(chat_feed.objects) == 1

        chat_feed.respond()

        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Response to: Question"

    async def test_respond_without_callback(self, chat_feed):
        chat_feed.respond()  # Should not raise any errors

    async def test_stream(self, chat_feed):
        message = chat_feed.stream("Streaming message", user="Person", avatar="P", footer_objects=[HTML("Footer")])
        assert len(chat_feed.objects) == 1
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Streaming message"
        assert chat_feed.objects[0].user == "Person"
        assert chat_feed.objects[0].avatar == "P"
        assert chat_feed.objects[0].footer_objects[0].object == "Footer"

        updated_entry = chat_feed.stream(
            " Appended message", user="New Person", message=message, avatar="N", footer_objects=[HTML("New Footer")]
        )
        assert len(chat_feed.objects) == 1
        assert chat_feed.objects[0] is updated_entry
        assert chat_feed.objects[0].object == "Streaming message Appended message"
        assert chat_feed.objects[0].user == "New Person"
        assert chat_feed.objects[0].avatar == "N"
        assert chat_feed.objects[0].footer_objects[0].object == "New Footer"

        new_entry = chat_feed.stream("New message")
        assert len(chat_feed.objects) == 2
        assert chat_feed.objects[1] is new_entry
        assert chat_feed.objects[1].object == "New message"

    async def test_add_step(self, chat_feed):
        # new
        with chat_feed.add_step("Object", title="Title") as step:
            assert isinstance(step, ChatStep)
            assert step.title == "Title"
            assert step.objects[0].object == "Object"

        assert len(chat_feed) == 1
        message = chat_feed.objects[0]
        assert isinstance(message, ChatMessage)
        assert message.user == "Assistant"

        steps = message.object
        assert isinstance(steps, Column)

        assert len(steps) == 1
        assert isinstance(steps[0], ChatStep)

        # existing
        with chat_feed.add_step("New Object", title="New Title") as step:
            assert isinstance(step, ChatStep)
            assert step.title == "New Title"
            assert step.objects[0].object == "New Object"
        assert len(steps) == 2
        assert isinstance(steps[0], ChatStep)
        assert isinstance(steps[1], ChatStep)

        # actual component
        with chat_feed.add_step("Newest Object", title="Newest Title") as step:
            assert isinstance(step, ChatStep)
            assert step.title == "Newest Title"
            assert step.objects[0].object == "Newest Object"
        assert len(steps) == 3
        assert isinstance(steps[0], ChatStep)
        assert isinstance(steps[1], ChatStep)
        assert isinstance(steps[2], ChatStep)

    async def test_add_step_new_user(self, chat_feed):
        with chat_feed.add_step("Object", title="Title", user="A") as step:
            assert isinstance(step, ChatStep)
            assert step.title == "Title"
            assert step.objects[0].object == "Object"

        with chat_feed.add_step("Object 2", title="Title 2", user="B") as step:
            assert isinstance(step, ChatStep)
            assert step.title == "Title 2"
            assert step.objects[0].object == "Object 2"

        assert len(chat_feed) == 2
        message1 = chat_feed.objects[0]
        assert isinstance(message1, ChatMessage)
        assert message1.user == "A"
        steps1 = message1.object
        assert isinstance(steps1, Column)
        assert len(steps1) == 1
        assert isinstance(steps1[0], ChatStep)
        assert len(steps1[0].objects) == 1
        assert steps1[0].objects[0].object == "Object"

        message2 = chat_feed.objects[1]
        assert isinstance(message2, ChatMessage)
        assert message2.user == "B"
        steps2 = message2.object
        assert isinstance(steps2, Column)
        assert len(steps2) == 1
        assert isinstance(steps2[0], ChatStep)
        assert len(steps2[0].objects) == 1
        assert steps2[0].objects[0].object == "Object 2"

    async def test_add_step_explict_not_append(self, chat_feed):
        with chat_feed.add_step("Object", title="Title") as step:
            assert isinstance(step, ChatStep)
            assert step.title == "Title"
            assert step.objects[0].object == "Object"

        with chat_feed.add_step("Object 2", title="Title 2", append=False) as step:
            assert isinstance(step, ChatStep)
            assert step.title == "Title 2"
            assert step.objects[0].object == "Object 2"

        assert len(chat_feed) == 2
        message1 = chat_feed.objects[0]
        assert isinstance(message1, ChatMessage)
        assert message1.user == "Assistant"
        steps1 = message1.object
        assert isinstance(steps1, Column)
        assert len(steps1) == 1
        assert isinstance(steps1[0], ChatStep)
        assert len(steps1[0].objects) == 1
        assert steps1[0].objects[0].object == "Object"

        message2 = chat_feed.objects[1]
        assert isinstance(message2, ChatMessage)
        assert message2.user == "Assistant"
        steps2 = message2.object
        assert isinstance(steps2, Column)
        assert len(steps2) == 1
        assert isinstance(steps2[0], ChatStep)
        assert len(steps2[0].objects) == 1
        assert steps2[0].objects[0].object == "Object 2"

    async def test_add_step_inherits_callback_exception(self, chat_feed):
        chat_feed.callback_exception = "verbose"
        with chat_feed.add_step("Object", title="Title") as step:
            assert step.callback_exception == "verbose"
            raise ValueError("Testing")
        assert "Traceback" in step.objects[0].object

    async def test_add_step_last_messages(self, chat_feed):
        # create steps
        with chat_feed.add_step("Object 1", title="Step 1"):
            assert len(chat_feed) == 1

        # add a message in the middle
        chat_feed.send("Message 1")
        assert len(chat_feed) == 2

        # last_messages=2 should make it connect with the last steps object
        with chat_feed.add_step("Object 2", title="Step 2", last_messages=2):
            assert len(chat_feed) == 2
            message = chat_feed[0]
            steps = message.object
            assert len(steps) == 2
            assert steps[0].objects[0].object == "Object 1"
            assert steps[1].objects[0].object == "Object 2"

        # add another message
        chat_feed.send("Message 2")
        assert len(chat_feed) == 3

        # this should now not join with the last steps object because the steps is in the first message
        with chat_feed.add_step("Object 3", title="Step 3", last_messages=2):
            assert len(chat_feed) == 4
            steps = chat_feed[-1].object
            assert len(steps) == 1

    async def test_stream_with_user_avatar(self, chat_feed):
        user = "Bob"
        avatar = "👨"
        message = chat_feed.stream(
            "Streaming with user and avatar", user=user, avatar=avatar
        )
        assert message.user == user
        assert message.avatar == avatar

    async def test_stream_dict(self, chat_feed):
        message = chat_feed.stream(
            {"object": "Streaming message", "user": "Person", "avatar": "P"}
        )
        await async_wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Streaming message"
        assert chat_feed.objects[0].user == "Person"
        assert chat_feed.objects[0].avatar == "P"

    async def test_stream_dict_minimum(self, chat_feed):
        message = chat_feed.stream({"object": "Streaming message"})
        await async_wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Streaming message"

    async def test_stream_dict_without_value(self, chat_feed):
        with pytest.raises(ValueError, match="it must contain an 'object' key"):
            chat_feed.stream({"user": "Person", "avatar": "P"})

    async def test_stream_dict_with_user_avatar_override(self, chat_feed):
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

    async def test_stream_message(self, chat_feed):
        message = ChatMessage("Streaming message", user="Person", avatar="P")
        chat_feed.stream(message)
        wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0] is message
        assert chat_feed.objects[0].object == "Streaming message"
        assert chat_feed.objects[0].user == "Person"
        assert chat_feed.objects[0].avatar == "P"

    def test_stream_message_error_passed_user_avatar(self, chat_feed):
        message = ChatMessage("Streaming message", user="Person", avatar="P")
        with pytest.raises(ValueError, match="Cannot set user or avatar"):
            chat_feed.stream(message, user="Bob", avatar="👨")

    async def test_stream_replace(self, chat_feed):
        message = chat_feed.stream("Hello")
        await async_wait_until(lambda: len(chat_feed.objects) == 1)
        assert chat_feed.objects[0].object == "Hello"

        message = chat_feed.stream(" World", message=message)
        await async_wait_until(lambda: chat_feed.objects[-1].object == "Hello World")

        chat_feed.stream("Goodbye", message=message, replace=True)
        await async_wait_until(lambda: chat_feed.objects[-1].object == "Goodbye")

    @pytest.mark.parametrize("replace", [True, False])
    async def test_stream_originally_none_message(self, chat_feed, replace):
        def callback(contents, user, instance):
            for i in range(3):
                chat_feed.stream(f"{i}.", message=base_message, replace=replace)
        chat_feed.callback = callback
        base_message = ChatMessage()
        chat_feed.send(base_message, respond=True)
        await async_wait_until(lambda: chat_feed.objects[0].object == ("2." if replace else "0.1.2."))

    @pytest.mark.parametrize(
        "obj",
        [
            "Some Text",
            TextInput(value="Some Text"),
            HTML("Some Text"),
            Row(HTML("Some Text")),
        ],
    )
    async def test_stream_to_nested_entry(self, chat_feed, obj):
        message = chat_feed.send(
            Row(
                obj,
                Image("https://panel.holoviz.org/_static/logo_horizontal.png"),
            )
        )
        chat_feed.stream(" Added", message=message)
        await async_wait_until(lambda: len(chat_feed.objects) == 1)
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

    async def test_undo(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")
        entry3 = chat_feed.send("Message 3")

        await async_wait_until(lambda: len(chat_feed.objects) == 3)

        undone_entries = chat_feed.undo()
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert undone_entries == [entry3]

        chat_feed.undo(2)
        await async_wait_until(lambda: len(chat_feed.objects) == 0)

    async def test_clear(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")

        assert len(chat_feed.objects) == 2

        cleared_entries = chat_feed.clear()
        assert len(chat_feed.objects) == 0
        assert cleared_entries[0].object == "Message 1"
        assert cleared_entries[1].object == "Message 2"

    async def test_set_entries(self, chat_feed):
        chat_feed.send("Message 1")
        chat_feed.send("Message 2")

        assert len(chat_feed.objects) == 2

        chat_feed.objects = [ChatMessage("Message 3")]
        assert len(chat_feed.objects) == 1
        assert chat_feed.objects[0].object == "Message 3"

    @pytest.mark.parametrize(["key", "value"], LAYOUT_PARAMETERS.items())
    def test_layout_parameters_are_propogated_to_card(self, key, value):
        chat_feed = ChatFeed(**{key: value})
        assert getattr(chat_feed, key) == value
        assert getattr(chat_feed._card, key) == value

    async def test_width_message_offset_80(self, chat_feed):
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
    async def test_default_avatars_default(self, chat_feed, user):
        chat_feed.send("Message 1", user=user)

        assert chat_feed.objects[0].user == user
        assert chat_feed.objects[0].avatar == "⚙️"

    async def test_default_avatars_superseded_in_dict(self, chat_feed):
        chat_feed.send({"user": "System", "avatar": "👨", "value": "Message 1"})

        assert chat_feed.objects[0].user == "System"
        assert chat_feed.objects[0].avatar == "👨"

    async def test_default_avatars_superseded_by_keyword(self, chat_feed):
        chat_feed.send({"user": "System", "value": "Message 1"}, avatar="👨")

        assert chat_feed.objects[0].user == "System"
        assert chat_feed.objects[0].avatar == "👨"

    async def test_default_avatars_superseded_in_entry(self, chat_feed):
        chat_feed.send(
            ChatMessage(user="System", avatar="👨", object="Message 1")
        )

        assert chat_feed.objects[0].user == "System"
        assert chat_feed.objects[0].avatar == "👨"

    async def test_default_avatars_lookup(self, chat_feed):
        def callback(contents, user, instance):
            yield "Message back"

        chat_feed.callback = callback
        chat_feed.callback_user = "System"
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].user == "System"
        assert chat_feed.objects[1].avatar == avatar_lookup(
            "System",
            None,
            {},
            default_avatars=DEFAULT_AVATARS
        )

    async def test_default_avatars_superseded_by_callback_avatar(self, chat_feed):
        def callback(contents, user, instance):
            yield "Message back"

        chat_feed.callback = callback
        chat_feed.callback_user = "System"
        chat_feed.callback_avatar = "S"
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].user == "System"
        assert chat_feed.objects[1].avatar == "S"

    async def test_default_avatars_message_params(self, chat_feed):
        chat_feed.message_params["default_avatars"] = {"test1": "1"}
        assert chat_feed.send(value="", user="test1").avatar == "1"

        # has default
        assert chat_feed.send(value="", user="system").avatar == "⚙️"

    async def test_no_recursion_error(self, chat_feed):
        chat_feed.send("Some time ago, there was a recursion error like this")

    @pytest.mark.parametrize("callback_avatar", [None, "👨", Image("https://panel.holoviz.org/_static/logo_horizontal.png")])
    async def test_callback_avatar(self, chat_feed, callback_avatar):
        def callback(contents, user, instance):
            yield "Message back"

        chat_feed.callback_avatar = callback_avatar
        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].avatar == callback_avatar or "🤖"

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

    async def test_respond_callback_returns_none(self, chat_feed):
        def callback(contents, user, instance):
            instance.objects[0].object = "Mutated"

        chat_feed.callback = callback
        chat_feed.send("Testing!", user="User")
        await async_wait_until(lambda: len(chat_feed.objects) == 1)
        await async_wait_until(lambda: chat_feed.objects[0].object == "Mutated")

    async def test_forward_message_params(self, chat_feed):
        chat_feed = ChatFeed(reaction_icons={"like": "thumb-up"}, reactions=["like"])
        chat_feed.send("Hey!")
        chat_message = chat_feed.objects[0]
        assert chat_feed.message_params == {"reaction_icons": {"like": "thumb-up"}, "reactions": ["like"]}
        assert chat_message.object == "Hey!"
        assert chat_message.reactions == ["like"]
        assert chat_message.reaction_icons.options == {"like": "thumb-up"}

    def test_message_params_no_chat_reaction_icons_instance(self, chat_feed):
        with pytest.raises(ValueError, match="Cannot pass"):
            chat_feed.message_params = {"reaction_icons": ChatReactionIcons(
                options={"like": "thumb-up", "dislike": "thumb-down"})}

    def test_update_chat_log_params(self, chat_feed):
        chat_feed = ChatFeed(load_buffer=5, scroll_button_threshold=5, auto_scroll_limit=5)
        assert chat_feed._chat_log.load_buffer == 5
        assert chat_feed._chat_log.scroll_button_threshold == 5
        assert chat_feed._chat_log.auto_scroll_limit == 5

        chat_feed.load_buffer = 10
        chat_feed.scroll_button_threshold = 10
        chat_feed.auto_scroll_limit = 10
        assert chat_feed._chat_log.load_buffer == 10
        assert chat_feed._chat_log.scroll_button_threshold == 10
        assert chat_feed._chat_log.auto_scroll_limit == 10

    async def test_repr(self, chat_feed):
        chat_feed.send("A")
        chat_feed.send("B")
        assert repr(chat_feed) == (
            "ChatFeed(_placeholder=ChatMessage, sizing_mode='stretch_width')\n"
            "    [0] ChatMessage(object='A', user='User', reactions=[])\n"
            "    [1] ChatMessage(object='B', user='User', reactions=[])"
        )


@pytest.mark.xdist_group("chat")
class TestChatFeedPromptUser:

    async def test_prompt_user_basic(self, chat_feed):
        text_input = TextInput()

        def callback(component, feed):
            feed.send(component.value)

        async def prompt_and_submit():
            chat_feed.prompt_user(text_input, callback)
            await async_wait_until(lambda: len(chat_feed.objects) == 1)
            text_input.value = "test input"
            submit_button = chat_feed.objects[-1].object[1]
            submit_button.clicks += 1
            await async_wait_until(lambda: len(chat_feed.objects) == 2)

        await asyncio.wait_for(prompt_and_submit(), timeout=5.0)
        assert chat_feed.objects[-1].object == "test input"

    async def test_prompt_user_with_predicate(self, chat_feed):
        text_input = TextInput()

        def predicate(component):
            return len(component.value) > 5

        def callback(component, feed):
            feed.send(component.value)

        async def prompt_and_submit():
            chat_feed.prompt_user(text_input, callback, predicate=predicate)
            await async_wait_until(lambda: len(chat_feed.objects) == 1)

            text_input.value = "short"
            submit_button = chat_feed.objects[-1].object[1]
            assert submit_button.disabled

            text_input.value = "long enough"
            await async_wait_until(lambda: not submit_button.disabled)

            submit_button.clicks += 1
            await async_wait_until(lambda: len(chat_feed.objects) == 2)

        await asyncio.wait_for(prompt_and_submit(), timeout=5.0)
        assert chat_feed.objects[-1].object == "long enough"

    async def test_prompt_user_timeout(self, chat_feed):
        text_input = TextInput()

        def callback(component, feed):
            pytest.fail("Callback should not be called on timeout")

        async def prompt_and_wait():
            chat_feed.prompt_user(text_input, callback, timeout=1)
            await async_wait_until(lambda: len(chat_feed.objects) == 1)
            await async_wait_until(lambda: chat_feed.objects[-1].object[1].disabled)

        await asyncio.wait_for(prompt_and_wait(), timeout=5.0)

        submit_button = chat_feed.objects[-1].object[1]
        assert submit_button.name == "Timed out"
        assert submit_button.button_type == "light"
        assert submit_button.icon == "x"

    async def test_prompt_user_custom_button_params(self, chat_feed):
        text_input = TextInput()

        def callback(component, feed):
            feed.send(component.value)

        custom_button_params = {
            "name": "Custom Submit",
            "button_type": "success",
            "icon": "arrow-right"
        }

        async def prompt_and_check():
            chat_feed.prompt_user(text_input, callback, button_params=custom_button_params)
            await async_wait_until(lambda: len(chat_feed.objects) == 1)

        await asyncio.wait_for(prompt_and_check(), timeout=5.0)

        submit_button = chat_feed.objects[-1].object[1]
        assert submit_button.name == "Custom Submit"
        assert submit_button.button_type == "success"
        assert submit_button.icon == "arrow-right"

    async def test_prompt_user_custom_timeout_button_params(self, chat_feed):
        text_input = TextInput()

        def callback(component, feed):
            pytest.fail("Callback should not be called on timeout")

        custom_timeout_params = {
            "name": "Custom Timeout",
            "button_type": "danger",
            "icon": "alert-triangle"
        }

        async def prompt_and_wait():
            chat_feed.prompt_user(text_input, callback, timeout=1, timeout_button_params=custom_timeout_params)
            await async_wait_until(lambda: len(chat_feed.objects) == 1)
            await async_wait_until(lambda: chat_feed.objects[-1].object[1].disabled)

        await asyncio.wait_for(prompt_and_wait(), timeout=5.0)

        submit_button = chat_feed.objects[-1].object[1]
        assert submit_button.name == "Custom Timeout"
        assert submit_button.button_type == "danger"
        assert submit_button.icon == "alert-triangle"

    async def test_prompt_user_async(self, chat_feed):
        text_input = TextInput()

        async def async_callback(component, feed):
            await asyncio.sleep(0.1)
            feed.send("Callback executed")

        async def prompt_and_submit():
            chat_feed.prompt_user(text_input, async_callback)
            await async_wait_until(lambda: len(chat_feed.objects) == 1)

            submit_button = chat_feed.objects[-1].object[1]
            submit_button.clicks += 1

            await async_wait_until(lambda: len(chat_feed.objects) == 2)

        await asyncio.wait_for(prompt_and_submit(), timeout=5.0)

        assert chat_feed.objects[-1].object == "Callback executed"
        assert chat_feed.objects[-2].object.disabled == True


@pytest.mark.xdist_group("chat")
class TestChatFeedCallback:

    async def test_user_avatar(self, chat_feed):
        ChatMessage.default_avatars["bob"] = "👨"

        def echo(contents, user, instance):
            return f"{user}: {contents}"

        chat_feed.callback = echo
        chat_feed.callback_user = "Bob"
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].user == "Bob"
        assert chat_feed.objects[1].avatar == "👨"
        ChatMessage.default_avatars.pop("bob")

    async def test_return(self, chat_feed):
        def echo(contents, user, instance):
            return contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"

    @pytest.mark.parametrize("callback_user", [None, "Bob"])
    @pytest.mark.parametrize("callback_avatar", [None, "C"])
    async def test_return_chat_message(self, chat_feed, callback_user, callback_avatar):
        def echo(contents, user, instance):
            message_kwargs = {}
            if callback_user:
                message_kwargs["user"] = callback_user
            if callback_avatar:
                message_kwargs["avatar"] = callback_avatar
            return ChatMessage(object=contents, **message_kwargs)

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"
        assert chat_feed.objects[1].user == callback_avatar or "Assistant"
        assert chat_feed.objects[1].avatar == callback_avatar or "🤖"

    async def test_yield(self, chat_feed):
        def echo(contents, user, instance):
            yield contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"

    async def test_async_return(self, chat_feed):
        async def echo(contents, user, instance):
            return contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        await async_wait_until(lambda: chat_feed.objects[1].object == "Message")

    @pytest.mark.parametrize("callback_user", [None, "Bob"])
    @pytest.mark.parametrize("callback_avatar", [None, "C"])
    async def test_yield_chat_message(self, chat_feed, callback_user, callback_avatar):
        def echo(contents, user, instance):
            message_kwargs = {}
            if callback_user:
                message_kwargs["user"] = callback_user
            if callback_avatar:
                message_kwargs["avatar"] = callback_avatar
            yield ChatMessage(object=contents, **message_kwargs)

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        await async_wait_until(lambda: chat_feed.objects[1].object == "Message")
        assert chat_feed.objects[1].user == callback_avatar or "Assistant"
        assert chat_feed.objects[1].avatar == callback_avatar or "🤖"

    @pytest.mark.parametrize("callback_user", [None, "Bob"])
    @pytest.mark.parametrize("callback_avatar", [None, "C"])
    async def test_yield_chat_message_stream(self, chat_feed, callback_user, callback_avatar):
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
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        await async_wait_until(lambda: chat_feed.objects[1].object == "Message")
        assert chat_feed.objects[1].user == callback_avatar or "Assistant"
        assert chat_feed.objects[1].avatar == callback_avatar or "🤖"

    async def test_async_yield(self, chat_feed):
        async def echo(contents, user, instance):
            yield contents

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        await async_wait_until(lambda: chat_feed.objects[1].object == "Message")

    async def test_generator(self, chat_feed):
        def echo(contents, user, instance):
            message = ""
            for char in contents:
                message += char
                yield message
                assert instance.objects[-1].show_activity_dot

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        await async_wait_until(lambda: chat_feed.objects[1].object == "Message")
        await async_wait_until(lambda: not chat_feed.objects[-1].show_activity_dot)

    @pytest.mark.parametrize("key", ["value", "object"])
    async def test_generator_dict(self, chat_feed, key):
        def echo(contents, user, instance):
            message = ""
            for char in contents:
                message += char
                yield {key: message}

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        await async_wait_until(lambda: chat_feed.objects[1].object == "Message")
        assert chat_feed.objects[-1].object == "Message"

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
        await async_wait_until(lambda: chat_feed.objects[1].object == "Message")
        assert not chat_feed.objects[-1].show_activity_dot

    @pytest.mark.parametrize("key", ["value", "object"])
    async def test_async_generator_dict(self, chat_feed, key):
        async def async_gen(contents):
            for char in contents:
                yield char

        async def echo(contents, user, instance):
            message = ""
            async for char in async_gen(contents):
                message += char
                yield {key: message}

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        await async_wait_until(lambda: chat_feed.objects[1].object == "Message")
        assert chat_feed.objects[-1].object == "Message"

    async def test_placeholder_text_params(self, chat_feed):
        def echo(contents, user, instance):
            assert instance._placeholder.user == "Loading..."
            assert instance._placeholder.object == "Thinking..."
            time.sleep(1.25)
            return "hey testing"

        chat_feed.callback = echo
        chat_feed.placeholder_text = "Thinking..."
        chat_feed.placeholder_params = {"user": "Loading..."}
        chat_feed.send("Message", respond=True)

    async def test_placeholder_disabled(self, chat_feed):
        def echo(contents, user, instance):
            time.sleep(1.25)
            assert instance._placeholder not in instance._chat_log
            return "hey testing"

        chat_feed.placeholder_threshold = 0
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log

    async def test_placeholder_enabled(self, chat_feed):
        def echo(contents, user, instance):
            time.sleep(1.25)
            assert instance._placeholder in instance._chat_log
            return chat_feed.stream("hey testing")

        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log

    async def test_placeholder_threshold_under(self, chat_feed):
        async def echo(contents, user, instance):
            await asyncio.sleep(0.25)
            assert instance._placeholder not in instance._chat_log
            return "hey testing"

        chat_feed.placeholder_threshold = 5
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log

    async def test_placeholder_threshold_under_generator(self, chat_feed):
        async def echo(contents, user, instance):
            assert instance._placeholder not in instance._chat_log
            await asyncio.sleep(0.25)
            assert instance._placeholder not in instance._chat_log
            yield "hey testing"

        chat_feed.placeholder_threshold = 5
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)

    async def test_placeholder_threshold_exceed(self, chat_feed):
        async def echo(contents, user, instance):
            await asyncio.sleep(0.5)
            assert instance._placeholder in instance._chat_log
            return "hello testing"

        chat_feed.placeholder_threshold = 0.1
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log

    async def test_placeholder_threshold_exceed_generator(self, chat_feed):
        async def echo(contents, user, instance):
            await async_wait_until(lambda: instance._placeholder not in instance._chat_log)
            await asyncio.sleep(0.5)
            await async_wait_until(lambda: instance._placeholder in instance._chat_log)
            yield "hello testing"
            await async_wait_until(lambda: instance._placeholder not in instance._chat_log)

        chat_feed.placeholder_threshold = 1
        chat_feed.callback = echo
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder not in chat_feed._chat_log

    async def test_renderers_pane(self, chat_feed):
        chat_feed.renderers = [HTML]
        chat_feed.send("Hello!")
        html = chat_feed.objects[0]._object_panel
        assert isinstance(html, HTML)
        assert html.object == "Hello!"
        assert html.sizing_mode is None

    async def test_renderers_widget(self, chat_feed):
        chat_feed.renderers = [TextAreaInput]
        chat_feed.send("Hello!")
        area_input = chat_feed[0]._update_object_pane()
        area_input = chat_feed[0]._object_panel
        assert isinstance(area_input, TextAreaInput)
        assert area_input.value == "Hello!"
        assert area_input.height == 500
        assert area_input.sizing_mode is None

    async def test_renderers_custom_callable(self, chat_feed):
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

    async def test_callback_exception(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "summary"
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: "division by zero" in chat_feed.objects[-1].object)
        assert chat_feed.objects[-1].user == "Exception"

    @pytest.mark.parametrize("callback_exception", ["traceback", "verbose"])
    async def test_callback_exception_traceback(self, chat_feed, callback_exception):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = callback_exception
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: chat_feed.objects[-1].object.startswith(
            "```python\nTraceback (most recent call last):"
        ))
        assert chat_feed.objects[-1].user == "Exception"

    async def test_callback_exception_ignore(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "ignore"
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 1)

    async def test_callback_exception_raise(self, chat_feed):
        def callback(msg, user, instance):
            return 1 / 0

        chat_feed.callback = callback
        chat_feed.callback_exception = "raise"

        # We need to use asyncio.gather to properly catch the exception
        with pytest.raises(ZeroDivisionError, match="division by zero"):
            chat_feed.send("Message", respond=True)
            await chat_feed._prepare_response()

    async def test_callback_exception_callable(self, chat_feed):
        def callback(msg, user, instance):
            raise ValueError("Expected error")

        def exception_callback(exception, instance):
            instance.stream(f"The exception: {exception}")

        chat_feed.callback = callback
        chat_feed.callback_exception = exception_callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(
            lambda: len(chat_feed.objects) == 2
        )
        assert chat_feed.objects[-1].object == "The exception: Expected error"

    async def test_callback_exception_async_callable(self, chat_feed):
        async def callback(msg, user, instance):
            raise ValueError("Expected error")

        async def exception_callback(exception, instance):
            await asyncio.sleep(0.1)
            instance.stream(f"The exception: {exception}")

        chat_feed.callback = callback
        chat_feed.callback_exception = exception_callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[-1].object == "The exception: Expected error"

    def test_callback_exception_invalid_option(self, chat_feed):
        with pytest.raises(ValueError, match="Valid options are"):
            chat_feed.callback_exception = "abc"

    async def test_callback_stop_generator(self, chat_feed):
        def callback(msg, user, instance):
            yield "A"
            assert chat_feed.stop()
            time.sleep(0.5)
            yield "B"

        chat_feed.callback = callback
        try:
            chat_feed.send("Message", respond=True)
        except asyncio.CancelledError:  # tests pick up this error
            pass
        # use sleep here instead of wait for because
        # the callback is timed and I want to confirm stop works
        await asyncio.sleep(1)
        assert chat_feed.objects[-1].object == "A"

    async def test_callback_stop_async_generator(self, chat_feed):
        async def callback(msg, user, instance):
            yield "A"
            assert chat_feed.stop()
            await asyncio.sleep(0.5)
            yield "B"

        chat_feed.callback = callback
        try:
            chat_feed.send("Message", respond=True)
        except asyncio.CancelledError:  # tests pick up this error
            pass
        # use sleep here instead of wait for because
        # the callback is timed and I want to confirm stop works
        await asyncio.sleep(1)
        assert chat_feed.objects[-1].object == "A"

    async def test_callback_stop_function(self, chat_feed):
        def callback(msg, user, instance):
            assert chat_feed.stop()
            return "B"

        chat_feed.callback = callback
        try:
            chat_feed.send("Message", respond=True)
        except asyncio.CancelledError:  # tests pick up this error
            pass
        assert chat_feed.objects[-1].object == "Message"

    async def test_callback_stop_async_function(self, chat_feed):
        async def callback(msg, user, instance):
            message = instance.stream("A")
            assert chat_feed.stop()
            await asyncio.sleep(0.5)
            instance.stream("B", message=message)

        chat_feed.callback = callback
        try:
            chat_feed.send("Message", respond=True)
        except asyncio.CancelledError:
            pass
        # use sleep here instead of wait for because
        # the callback is timed and I want to confirm stop works
        await asyncio.sleep(1)
        assert chat_feed.objects[-1].object == "A"

    async def test_callback_short_time(self, chat_feed):
        def callback(contents, user, instance):
            time.sleep(1)
            message = None
            string = ""
            for c in "helloooo":
                string += c
                time.sleep(0.001)
                message = instance.stream(string, message=message, replace=True)

        feed = ChatFeed(callback=callback)
        feed.send("Message", respond=True)
        await async_wait_until(lambda: len(feed.objects) == 2)
        await async_wait_until(lambda: feed.objects[-1].object == "helloooo")
        assert chat_feed._placeholder not in chat_feed._chat_log

    async def test_callback_one_argument(self, chat_feed):
        def callback(contents):
            return contents

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "Message"

    async def test_callback_positional_argument(self, chat_feed):
        def callback(*args):
            return f"{args[1]}: {args[0]}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_mix_positional_argument(self, chat_feed):
        def callback(contents, *args):
            return f"{args[0]}: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_keyword_argument(self, chat_feed):
        def callback(**kwargs):
            assert "instance" in kwargs
            return f"{kwargs['user']}: {kwargs['contents']}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_mix_keyword_argument(self, chat_feed):
        def callback(contents, **kwargs):
            return f"{kwargs['user']}: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_mix_positional_keyword_argument(self, chat_feed):
        def callback(*args, **kwargs):
            assert not kwargs
            return f"{args[1]}: {args[0]}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_two_arguments(self, chat_feed):
        def callback(contents, user):
            return f"{user}: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_two_arguments_with_keyword(self, chat_feed):
        def callback(contents, user=None):
            return f"{user}: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_three_arguments_with_keyword(self, chat_feed):
        def callback(contents, user=None, instance=None):
            return f"{user}: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_two_arguments_yield(self, chat_feed):
        def callback(contents, user):
            yield f"{user}: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_two_arguments_async_yield(self, chat_feed):
        async def callback(contents, user):
            yield f"{user}: {contents}"

        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_as_method(self, chat_feed):
        class Test:
            def callback(self, contents, user):
                return f"{user}: {contents}"

        chat_feed.callback = Test().callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_callback_as_class_method(self, chat_feed):
        class Test:
            @classmethod
            def callback(cls, contents, user):
                return f"{user}: {contents}"

        chat_feed.callback = Test.callback
        chat_feed.send("Message", respond=True)
        await async_wait_until(lambda: len(chat_feed.objects) == 2)
        assert chat_feed.objects[1].object == "User: Message"

    async def test_persist_placeholder_while_loading(self, chat_feed):
        def callback(contents):
            assert chat_feed._placeholder in chat_feed._chat_log
            return "hey testing"

        chat_feed.loading = True
        chat_feed.callback = callback
        chat_feed.send("Message", respond=True)
        assert chat_feed._placeholder in chat_feed._chat_log


@pytest.mark.xdist_group("chat")
class TestChatFeedSerializeForTransformers:

    async def test_defaults(self):
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

    async def test_case_insensitivity(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="USER")
        chat_feed.send("I'm the assistant", user="ASSISTant")
        chat_feed.send("I'm a bot", user="boT")
        assert chat_feed.serialize() == [
            {"role": "user", "content": "I'm a user"},
            {"role": "assistant", "content": "I'm the assistant"},
            {"role": "assistant", "content": "I'm a bot"},
        ]

    async def test_default_role(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="user")
        chat_feed.send("I'm the assistant", user="assistant")
        chat_feed.send("I'm a bot", user="bot")
        assert chat_feed.serialize(default_role="system") == [
            {"role": "user", "content": "I'm a user"},
            {"role": "assistant", "content": "I'm the assistant"},
            {"role": "system", "content": "I'm a bot"},
        ]

    async def test_empty_default_role(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="user")
        chat_feed.send("I'm the assistant", user="assistant")
        chat_feed.send("I'm a bot", user="bot")
        with pytest.raises(ValueError, match="not found in role_names"):
            chat_feed.serialize(default_role="")

    async def test_role_names(self):
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

    async def test_custom_serializer(self):
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

    async def test_custom_serializer_invalid_output(self):
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

    async def test_serialize_filter_by(self, chat_feed):
        def filter_by_reactions(messages):
            return [obj for obj in messages if "favorite" in obj.reactions]

        chat_feed.send(ChatMessage("no"))
        chat_feed.send(ChatMessage("yes", reactions=["favorite"]))
        filtered = chat_feed.serialize(filter_by=filter_by_reactions)
        assert len(filtered) == 1
        assert filtered[0]["content"] == "yes"

    async def test_serialize_exclude_users_default(self):
        def say_hi(contents, user, instance):
            return f"Hi {user}!"

        chat_feed = ChatFeed(
            help_text="This chat feed will respond by saying hi!",
            callback=say_hi
        )
        chat_feed.send("Hello there!")
        await async_wait_until(lambda: chat_feed.serialize() == [
            {"role": "user", "content": "Hello there!"},
            {"role": "assistant", "content": "Hi User!"}
        ])

    async def test_serialize_exclude_users_custom(self):
        def say_hi(contents, user, instance):
            return f"Hi {user}!"

        chat_feed = ChatFeed(
            help_text="This chat feed will respond by saying hi!",
            callback=say_hi
        )
        chat_feed.send("Hello there!")
        await async_wait_until(lambda: chat_feed.serialize(exclude_users=["assistant"]) == [
            {"role": "assistant", "content": "This chat feed will respond by saying hi!"},
            {"role": "user", "content": "Hello there!"},
        ])

    async def test_serialize_exclude_placeholder(self):
        def say_hi(contents, user, instance):
            assert len(instance.serialize()) == 1
            return f"Hi {user}!"

        chat_feed = ChatFeed(
            help_text="This chat feed will respond by saying hi!",
            callback=say_hi
        )

        chat_feed.send("Hello there!")
        await async_wait_until(lambda: chat_feed.serialize() == [
            {"role": "user", "content": "Hello there!"},
            {"role": "assistant", "content": "Hi User!"}
        ])

    async def test_serialize_limit(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="user")
        chat_feed.send("I'm the assistant", user="assistant")
        chat_feed.send("I'm a bot", user="bot")
        await async_wait_until(lambda: chat_feed.serialize(limit=1) == [
            {"role": "assistant", "content": "I'm a bot"},
        ])

    async def test_serialize_class(self, chat_feed):
        class Test():

            def __repr__(self):
                return "Test()"

        chat_feed.send(Test())
        await async_wait_until(lambda: chat_feed.serialize() == [{"role": "user", "content": "Test()"}])

    async def test_serialize_kwargs(self, chat_feed):
        chat_feed.send("Hello")
        chat_feed.add_step("Hello", "World")
        await async_wait_until(lambda: chat_feed.serialize(
            prefix_with_container_label=False,
            prefix_with_viewable_label=False
        ) == [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': '((Hello))'}
        ])


@pytest.mark.xdist_group("chat")
class TestChatFeedSerializeBase:

    async def test_transformers_format(self):
        chat_feed = ChatFeed()
        chat_feed.send("I'm a user", user="user")
        chat_feed.send("I'm the assistant", user="assistant")
        chat_feed.send("I'm a bot", user="bot")
        assert chat_feed.serialize(format="transformers") == [
            {"role": "user", "content": "I'm a user"},
            {"role": "assistant", "content": "I'm the assistant"},
            {"role": "assistant", "content": "I'm a bot"},
        ]

    async def test_invalid(self):
        with pytest.raises(NotImplementedError, match="is not supported"):
            chat_feed = ChatFeed()
            chat_feed.send("I'm a user", user="user")
            chat_feed.serialize(format="atransform")


@pytest.mark.xdist_group("chat")
class TestChatFeedPostHook:

    async def test_return_string(self, chat_feed):
        def callback(contents, user, instance):
            return f"Echo: {contents}"

        def append_callback(message, instance):
            logs.append(message.object)

        logs = []
        chat_feed.callback = callback
        chat_feed.post_hook = append_callback
        chat_feed.send("Hello World!")
        await async_wait_until(lambda: chat_feed.objects[-1].object == "Echo: Hello World!")
        await async_wait_until(lambda: logs == ["Hello World!", "Echo: Hello World!"])

    async def test_yield_string(self, chat_feed):
        def callback(contents, user, instance):
            yield f"Echo: {contents}"

        def append_callback(message, instance):
            logs.append(message.object)

        logs = []
        chat_feed.callback = callback
        chat_feed.post_hook = append_callback
        chat_feed.send("Hello World!")
        await async_wait_until(lambda: chat_feed.objects[-1].object == "Echo: Hello World!")
        await async_wait_until(lambda: logs == ["Hello World!", "Echo: Hello World!"])

    async def test_generator(self, chat_feed):
        def callback(contents, user, instance):
            message = "Echo: "
            for char in contents:
                message += char
                yield message

        def append_callback(message, instance):
            logs.append(message.object)

        logs = []
        chat_feed.callback = callback
        chat_feed.post_hook = append_callback
        chat_feed.send("Hello World!")
        await async_wait_until(lambda: chat_feed.objects[-1].object == "Echo: Hello World!")
        await async_wait_until(lambda: logs == ["Hello World!", "Echo: Hello World!"])

    async def test_async_generator(self, chat_feed):
        async def callback(contents, user, instance):
            message = "Echo: "
            for char in contents:
                message += char
                yield message

        async def append_callback(message, instance):
            logs.append(message.object)

        logs = []
        chat_feed.callback = callback
        chat_feed.post_hook = append_callback
        chat_feed.send("Hello World!")
        await async_wait_until(lambda: chat_feed.objects[-1].object == "Echo: Hello World!")
        await async_wait_until(lambda: logs == ["Hello World!", "Echo: Hello World!"])

    async def test_stream(self, chat_feed):
        def callback(contents, user, instance):
            message = instance.stream("Echo: ", trigger_post_hook=True)
            for char in contents:
                message = instance.stream(char, message=message)
            instance.trigger_post_hook()

        def append_callback(message, instance):
            logs.append(message.object)

        logs = []
        chat_feed.callback = callback
        chat_feed.post_hook = append_callback
        chat_feed.send("AB")
        await async_wait_until(lambda: chat_feed.objects[-1].object == "Echo: AB")
        await async_wait_until(lambda: logs == ["AB", "Echo: ", "Echo: AB"])

    async def test_add_chat_step(self, chat_feed):
        def append_callback(message, instance):
            step = message.object[-1]
            logs.append(f"# {step.title}\n{step.objects[0].object}")

        logs = []
        chat_feed.post_hook = append_callback
        with chat_feed.add_step(title="Steps") as step:
            for c in range(2):
                step.stream(str(c))
        await async_wait_until(lambda: logs == ["# Steps\n01"])


@pytest.mark.xdist_group("chat")
class TestChatFeedEditCallback:

    @pytest.mark.parametrize("edit_callback", [None, lambda content, index, instance: ""])
    async def test_show_edit_icon_callback(self, chat_feed, edit_callback):
        chat_feed.edit_callback = edit_callback
        chat_feed.send("Hello")
        assert chat_feed[0].show_edit_icon is bool(edit_callback)

    @pytest.mark.parametrize("user", ["User", "Assistant", "Help"])
    async def test_show_edit_icon_user(self, chat_feed, user):
        chat_feed.edit_callback = lambda content, index, instance: ""
        chat_feed.send("Hello", user=user)
        if user == "User":
            assert chat_feed[0].show_edit_icon
        else:
            assert not chat_feed[0].show_edit_icon
