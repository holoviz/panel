import pytest

from panel.depends import bind
from panel.layout import Column
from panel.pane import JPG
from panel.widgets import FileInput, TextInput
from panel.widgets.chatbox import ChatBox, ChatRow

JPG_FILE = "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"


def test_chat_box(document, comm):
    value = [
        {"user1": "Hello"},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box.value == value
    assert len(chat_box) == 1
    rows = chat_box.rows
    assert all(isinstance(row, ChatRow) for row in rows)
    assert len(rows) == 1
    assert rows[0].value == ["Hello"]
    assert rows[0]._bubble[0].object == "Hello"


def test_chat_box_role_content_format(document, comm):
    value = [
        {"role": "user1", "content": "Hello"},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box.value == value
    assert len(chat_box) == 1
    rows = chat_box.rows
    assert all(isinstance(row, ChatRow) for row in rows)
    assert len(rows) == 1
    assert rows[0].value == ["Hello"]
    assert rows[0]._bubble[0].object == "Hello"


def test_chat_box_invalid_format(document, comm):
    value = [
        {"a_user": "user1", "message": "Hello"},
    ]
    with pytest.raises(ValueError, match="Expected a dictionary with one key-value"):
        ChatBox(value=value.copy())


def test_chat_box_list(document, comm):
    value = [
        {"user2": ["Hi", "Greetings", "Salutations"]},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box.value == value
    assert len(chat_box) == 1
    rows = chat_box.rows
    assert all(isinstance(row, ChatRow) for row in rows)
    assert len(rows) == 1
    assert rows[0].value == ["Hi", "Greetings", "Salutations"]
    assert rows[0]._bubble[0].object == "Hi"
    assert rows[0]._bubble[1].object == "Greetings"
    assert rows[0]._bubble[2].object == "Salutations"


def test_chat_box_chat_log_overflow(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box._chat_log.styles == {
        "flex-direction": "column-reverse",
        "overflow-x": "auto",
        "overflow-y": "auto",
    }


def test_chat_box_input_widgets(document, comm):
    chat_box = ChatBox(
        message_input_widgets=[FileInput(name="Communicate with files!")]
    )
    assert chat_box._send_button
    message_input = chat_box._message_inputs["Communicate with files!"]
    assert isinstance(message_input, FileInput)
    assert message_input.name == "Communicate with files!"
    assert message_input.sizing_mode == "stretch_width"


def test_chat_box_empty(document, comm):
    chat_box = ChatBox()
    assert chat_box.value == []
    assert len(chat_box) == 0


def test_chat_box_refresh(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box.value == value
    assert len(chat_box) == 2

    chat_box.value = [
        {"user1": "Greetings"},
    ]
    assert chat_box.value == [{"user1": "Greetings"}]
    assert len(chat_box) == 1
    assert len(chat_box._chat_log.objects) == 1


def test_chat_box_clear(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box.value == value
    assert len(chat_box) == 2
    chat_box.clear()
    assert chat_box.value == []
    assert len(chat_box) == 0


def test_chat_box_disabled(document, comm):
    chat_box = ChatBox(disabled=True)
    # message input
    assert chat_box._composite[0][0].disabled
    # send button
    assert chat_box._composite[0][1].disabled

    chat_box.disabled = False
    # message input
    assert not chat_box._composite[0][0].disabled
    # send button
    assert not chat_box._composite[0][1].disabled


def test_chat_box_loading(document, comm):
    chat_box = ChatBox(loading=True)
    # message input
    assert chat_box._composite[0][0].loading
    # send button
    assert chat_box._composite[0][1].loading

    chat_box.loading = False
    # message input
    assert not chat_box._composite[0][0].loading
    # send button
    assert not chat_box._composite[0][1].loading


def test_chat_box_append(document, comm):
    chat_box = ChatBox()
    chat_box.append({"user1": "Hello"})
    chat_box.append({"user2": "Hi"})
    assert chat_box.value == [{"user1": "Hello"}, {"user2": "Hi"}]
    assert len(chat_box) == 2
    assert len(chat_box._chat_log.objects) == 2


def test_chat_box_append_bind(document, comm):
    def update(history):
        return history

    chat_box = ChatBox()
    result = bind(update, history=chat_box)
    col = Column(chat_box, result)
    chat_box.append({"user1": "Hello"})
    chat_box.append({"user2": "Hi"})
    assert col[-1].object() == [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]


def test_chat_box_extend(document, comm):
    chat_box = ChatBox()
    chat_box.extend([{"user1": "Hello"}, {"user2": "Hi"}])
    assert chat_box.value == [{"user1": "Hello"}, {"user2": "Hi"}]
    assert len(chat_box) == 2


def test_insert(document, comm):
    chat_box = ChatBox()
    message = {"user": "Hello"}
    chat_box.insert(0, message)
    assert chat_box.value == [message]
    assert len(chat_box) == 1

    # Inserting at an index greater than the current length
    chat_box.insert(2, {"user": "Hi"})
    assert chat_box.value == [message, {"user": "Hi"}]
    assert len(chat_box) == 2


def test_pop(document, comm):
    chat_box = ChatBox()
    message1 = {"user": "Hello"}
    message2 = {"user": "Hi"}
    message3 = {"user": "Hey"}
    chat_box.extend([message1, message2, message3])

    # Pop the last message
    popped_message = chat_box.pop()
    assert popped_message == message3
    assert chat_box.value == [message1, message2]
    assert len(chat_box) == 2

    # Pop a specific index
    popped_message = chat_box.pop(0)
    assert popped_message == message1
    assert chat_box.value == [message2]
    assert len(chat_box) == 1


def test_replace(document, comm):
    chat_box = ChatBox()
    message1 = {"user": "Hello"}
    message2 = {"user": "Hi"}
    chat_box.extend([message1, message2])

    # Replace a message at a specific index
    new_message = {"user": "Hey"}
    chat_box.replace(1, new_message)
    assert chat_box.value == [message1, new_message]
    assert len(chat_box) == 2


def test_chat_box_allow_input(document, comm):
    chat_box = ChatBox(allow_input=True)
    assert chat_box.allow_input == True
    assert isinstance(chat_box._message_inputs["TextInput"], TextInput)
    # column, text input, button
    assert len(chat_box._composite) == 3


def test_chat_box_not_allow_input(document, comm):
    chat_box = ChatBox(allow_input=False)
    assert chat_box.allow_input == False
    assert chat_box._message_inputs == {}
    assert chat_box._send_button is None
    # column, button
    assert len(chat_box._composite) == 2


def test_chat_box_primary_name(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy(), primary_name="Panel User")
    assert chat_box.primary_name == "Panel User"
    assert chat_box.value == value

    chat_box._message_inputs["TextInput"].value = "Hello!"
    assert chat_box.value == value + [{"Panel User": "Hello!"}]


def test_chat_box_inferred_primary_name(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box.primary_name == "user1"
    assert chat_box.value == value

    chat_box._message_inputs["TextInput"].value = "Hello!"
    assert chat_box.value == value + [{"user1": "Hello!"}]


def test_chat_box_message_colors(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy(), message_colors={"user1": "red"})
    assert chat_box.message_colors["user1"] == "red"
    # random generated colors are hexcodes
    assert chat_box.message_colors["user2"] == ("rgb(235, 235, 235)", "black")


def test_chat_box_message_colors_with_hue(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(
        value=value.copy(), message_colors={"user1": "red"}, message_hue=210
    )
    assert chat_box.message_colors["user1"] == "red"
    # random generated colors are hexcodes
    assert chat_box.message_colors["user2"][0].startswith("hsl")


def test_chat_box_generate_color(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
        {"user3": "Hi"},
        {"user4": "Hi"},
        {"user5": "Hi"},
    ]
    chat_box = ChatBox(
        value=value.copy(), message_colors={"user1": "red"}, message_hue=290
    )
    assert chat_box.message_colors["user1"] == "red"
    assert chat_box.message_colors["user2"][0] == "hsl(290, 15%, 60%)"
    assert chat_box.message_colors["user3"][0] == "hsl(290, 30%, 55%)"
    assert chat_box.message_colors["user4"][0] == "hsl(290, 45%, 50%)"
    assert chat_box.message_colors["user5"][0] == "hsl(18, 15%, 60%)"


def test_chat_box_user_icons(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy(), message_icons={"user1": JPG_FILE})
    assert chat_box.message_icons["user1"] == JPG_FILE
    assert "user2" not in chat_box.message_icons


def test_chat_box_show_name(document, comm):
    # name should only show on the first message
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box.rows[0]._name.object == "user1"
    assert chat_box.rows[1]._name.object == "user2"
    # no name shown for consecutive messages from the same user
    assert chat_box.rows[2]._name is None


def test_chat_box_show_names(document, comm):
    # name should only show on the first message
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy(), show_names=False)
    assert chat_box.rows[0]._name is None
    assert chat_box.rows[1]._name is None
    # no name shown for consecutive messages from the same user
    assert chat_box.rows[2]._name is None


def test_chat_box_allow_likes(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy(), allow_likes=False)
    assert not chat_box.rows[0]._like.visible


def test_chat_box_keeps_likes(document, comm):
    """
    Like disappears after appending a new message
    https://github.com/holoviz/panel/issues/5050
    """
    chat_box = ChatBox(
        name="Chat",
        value=[{"You": "Hello!"}, {"Bot": ["How may I help?", "I'm a bot."]}],
        allow_likes=True,
    )

    chat_box.rows[0].liked = True
    chat_box.rows[1].liked = True
    chat_box.append({"You": "Do I still like your message?"})
    assert chat_box.rows[1].liked

    # it shouldn't keep the likes if the message is changed
    chat_box.value = [
        {"You": "Hello!"},
        {"Bot": "No longer do I do..."},
        {"You": "Do I still like your message?"},
    ]
    assert chat_box.rows[0].liked
    assert not chat_box.rows[1].liked
    assert not chat_box.rows[1].liked


def test_chat_box_replace_value(document, comm):
    """
    Ensure replacing it with new messages works
    """
    chat_box = ChatBox(
        name="Chat",
        value=[{"You": "Hello!"}, {"Bot": ["How may I help?", "I'm a bot."]}],
        allow_likes=True,
    )
    chat_box.rows[1].liked = True

    chat_box.append({"You": "Do I still like your message?"})
    assert chat_box.rows[1].liked

    chat_box.value = [{"You": "Hey!"}, {"Bot": "Bye"}]
    assert not chat_box.rows[1].liked
    assert chat_box.rows[0].value == ["Hey!"]
    assert chat_box.rows[1].value == ["Bye"]
    assert chat_box.value == [{"You": "Hey!"}, {"Bot": "Bye"}]


def test_chat_row(document, comm):
    chat_row = ChatRow(
        value=["Hello"], name="user1", styles={"background": "black"}, show_name=True
    )

    name = chat_row._name
    assert name.object == "user1"
    assert name.align == ("start", "start")

    assert chat_row._icon is None

    bubble = chat_row._bubble
    assert bubble[0].object == "Hello"


def test_chat_row_image_message(document, comm):
    chat_row = ChatRow(value=[JPG_FILE])
    assert isinstance(chat_row._bubble[0], JPG)


def test_chat_row_update_like(document, comm):
    chat_row = ChatRow(value=["Hello"], name="user1")

    assert not chat_row.liked
    assert not chat_row._like.value
    assert chat_row._like.name == "♡"

    # now like it!
    chat_row._like.value = True
    assert chat_row.liked
    assert chat_row._like.value
    assert chat_row._like.name == "❤️"

    # now unlike it :( using the public property
    chat_row.liked = False
    assert not chat_row.liked
    assert not chat_row._like.value
    assert chat_row._like.name == "♡"


def test_chat_row_hide_like(document, comm):
    chat_row = ChatRow(value=["Hello"], name="user1", show_like=False)
    assert not chat_row._like.visible


def test_chat_row_default_message_callable(document, comm):
    chat_row = ChatRow(
        value=["Hello", TextInput(value="Input")], default_message_callable=TextInput
    )

    for obj in chat_row._bubble:
        assert isinstance(obj, TextInput)


def test_chat_row_align_end(document, comm):
    chat_row = ChatRow(value=["Hello"], name="user1", align="end")
    assert chat_row._name.align == ("end", "start")


def test_chat_row_not_show_name(document, comm):
    chat_row = ChatRow(value=["Hello"], name="user1", show_name=False)
    assert chat_row._name is None


def test_chat_row_bubble_obj_sizing_mode_default(document, comm):
    chat_row = ChatRow(value=["Hello"], name="user1", show_name=False)
    assert chat_row._bubble[0].sizing_mode == "stretch_width"


def test_chat_row_bubble_obj_sizing_mode_set(document, comm):
    widget = TextInput(sizing_mode="fixed", width=300, height=100)
    chat_row = ChatRow(value=[widget], name="user1", show_name=False)
    assert chat_row._bubble[0].sizing_mode == "fixed"
