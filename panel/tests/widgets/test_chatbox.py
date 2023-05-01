from panel.pane import JPG
from panel.widgets import TextInput
from panel.widgets.chatbox import ChatBox, ChatRow

JPG_FILE = "https://assets.holoviz.org/panel/samples/jpg_sample.jpg"


def test_chat_box(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box.value == value
    assert len(chat_box) == 2


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


def test_chat_box_append(document, comm):
    chat_box = ChatBox()
    chat_box.append({"user1": "Hello"})
    chat_box.append({"user2": "Hi"})
    assert chat_box.value == [{"user1": "Hello"}, {"user2": "Hi"}]
    assert len(chat_box) == 2
    assert len(chat_box._chat_log.objects) == 2


def test_chat_box_extend(document, comm):
    chat_box = ChatBox()
    chat_box.extend([{"user1": "Hello"}, {"user2": "Hi"}])
    assert chat_box.value == [{"user1": "Hello"}, {"user2": "Hi"}]
    assert len(chat_box) == 2


def test_chat_box_allow_input(document, comm):
    chat_box = ChatBox(allow_input=True)
    assert chat_box.allow_input == True
    assert isinstance(chat_box._composite[-1], TextInput)
    # column, vspacer, text input
    assert len(chat_box._composite) == 3


def test_chat_box_not_allow_input(document, comm):
    chat_box = ChatBox(allow_input=False)
    assert chat_box.allow_input == False
    assert not isinstance(chat_box._composite[-1], TextInput)
    # column, vspacer, text input
    assert len(chat_box._composite) == 1


def test_chat_box_primary_user(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy(), primary_user="Panel User")
    assert chat_box.primary_user == "Panel User"
    assert chat_box.value == value

    chat_box._input_message.value = "Hello!"
    assert chat_box.value == value + [{"Panel User": "Hello!"}]


def test_chat_box_inferred_primary_user(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy())
    assert chat_box.primary_user == "user1"
    assert chat_box.value == value

    chat_box._input_message.value = "Hello!"
    assert chat_box.value == value + [{"user1": "Hello!"}]


def test_chat_box_user_colors(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy(), user_colors={"user1": "red"})
    assert chat_box.user_colors["user1"] == "red"
    # random generated colors are hexcodes
    assert chat_box.user_colors["user2"].startswith("#")


def test_chat_box_user_icons(document, comm):
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy(), user_icons={"user1": JPG_FILE})
    assert chat_box.user_icons["user1"] == JPG_FILE
    assert "user2" not in chat_box.user_icons


def test_chat_box_show_name(document, comm):
    # name should only show on the first message
    value = [
        {"user1": "Hello"},
        {"user2": "Hi"},
        {"user2": "Hi"},
    ]
    chat_box = ChatBox(value=value.copy())
    # Log -> ChatRow -> Column -> StaticText == name
    assert chat_box._chat_log[0]._composite[0][0].value == "user1"
    assert chat_box._chat_log[1]._composite[0][0].value == "user2"
    # no name shown
    assert not isinstance(chat_box._chat_log[1]._composite[0][0], TextInput)


def test_chat_row(document, comm):
    chat_row = ChatRow(
        value=["Hello"], name="user1", styles={"background": "black"}, show_name=True
    )

    name = chat_row._name
    assert name.value == "user1"
    assert name.align == "start"

    icon = chat_row._icon
    assert icon.object == "*U-1*"
    assert icon.align == "center"
    assert icon.styles["background"] == "black"

    bubble = chat_row._bubble
    assert bubble[0].object == "Hello"
    assert icon.styles["background"] == "black"


def test_chat_row_image_message(document, comm):
    chat_row = ChatRow(value=[JPG_FILE])
    assert isinstance(chat_row._bubble[0], JPG)


def test_chat_row_update_like(document, comm):
    chat_row = ChatRow(
        value=["Hello"], name="user1"
    )

    assert not chat_row.liked
    assert not chat_row._like.value
    assert chat_row._like.name == "♡"
    chat_row._like.value = True
    assert chat_row.liked
    assert chat_row._like.value
    assert chat_row._like.name == "❤️"


def test_chat_row_default_panel(document, comm):
    chat_row = ChatRow(
        value=["Hello", TextInput(value="Input")],
        default_panel=TextInput
    )

    for obj in chat_row._bubble:
        assert isinstance(obj, TextInput)


def test_message_align_end(document, comm):
    chat_row = ChatRow(
        value=["Hello"], name="user1", align="end"
    )
    assert chat_row._name.align == "end"


def test_message_not_show_name(document, comm):
    chat_row = ChatRow(
        value=["Hello"], name="user1", show_name=False
    )
    assert chat_row._name is None


def test_message_not_show_like(document, comm):
    chat_row = ChatRow(
        value=["Hello"], name="user1", show_like=False
    )
    assert chat_row._like is None
