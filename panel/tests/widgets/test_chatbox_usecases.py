"""Test common ChatBox use cases

The purpose is to make sure they can be implemented in a simple and performant way with a
good user experience.

Should go hand in hand with documentation
"""
import pytest

import panel as pn

from panel.widgets.chatbox import ChatBox
from panel.widgets.indicators import LoadingSpinner

RESPONSE = "I don't know"

@pytest.fixture
def messages():
    return [
        {"User": "Hello!"},
        {"Assistant": "Greetings!"},
    ]

def get_response(prompt):
    return RESPONSE

def get_multiple_responses(prompt):
    yield "planning ..."
    yield "running ..."
    yield RESPONSE

def stream_response(prompt):
    for token in ["I ", "dont' ", "know"]:
        yield token

# Todo: Todo: Support Async versions of everything

# TESTS

def test_can_provide_response():
    """The user can quickly add a new response"""
    # Given
    chat_box = ChatBox()
    prompt = "What is 2+2"
    # When: this is our recommended best practices
    answer = {"Assistant": get_response(prompt)}
    chat_box.append(answer)
    # Then
    assert chat_box.value[-1]==answer

def test_can_get_and_use_single_message(messages):
    """The user can easily get AND use a single message

    Easily use means being able to easily extract the user name and the associated prompt/ response
    """
    # Given
    chat_box = ChatBox()
    chat_box.append({"User": "Hello"})
    index = 0 # Could be any index

    # When: this is our best practice approach
    value = chat_box.value[index]
    user, value = next(iter(value.items()))

    # Then
    assert user=="User"
    assert value=="Hello"

def test_can_respond_to_primary_user_input():
    """The AI can be called and return a response when ever the user enters a new prompt"""
    # Given
    chat_box = ChatBox()

    # When: this is our best practice implementation
    def respond_to_user_input(value):
        if not value:
            return

        value = chat_box.value[-1]
        user, prompt = next(iter(value.items()))
        if user!="User":
            return

        with chat_box.respond(user="Assistant", value=None, raise_exception=False) as message:
            message.value = get_response(prompt)

    pn.bind(respond_to_user_input, value=chat_box, watch=True)

    # Then
    chat_box.append({"Assistant": "Welcome"})
    assert len(chat_box)==1

    chat_box.append({"User": "What is 2+2?"})
    assert len(chat_box)==3

    chat_box.append({"Assistant": "Anything else?"})
    assert len(chat_box)==4



def test_can_disable_chatbox_while_providing_slow_response():
    """The ChatBox can easily be disabled while a slow response is generated"""
    # Given
    chat_box = ChatBox()
    prompt = "What is 2+2?"

    # When: this is our recommended best practices
    with chat_box.respond(user="Assistant") as message:
        # Then
        assert chat_box.disabled
        # When
        message.value = get_response(prompt)
    # Then
    assert not chat_box.disabled

def test_can_provide_custom_spinner_while_providing_slow_response():
    # Given
    chat_box = ChatBox()
    prompt = "What is 2+2?"
    indicator = LoadingSpinner(value=True, height=25, color="success")

    # When
    with chat_box.respond(user="Assistant", value=indicator) as message:
        # Then
        assert message.name=="Assistant"
        assert message.value==indicator
        assert chat_box.value==[]
        assert chat_box._chat_log.objects==[message._chat_row]
        assert message._chat_row.value==[indicator]
        # When
        response = get_response(prompt)
        message.value = response
        # Then
        assert chat_box.value==[]
        assert chat_box._chat_log.objects==[message._chat_row]
        assert message._chat_row.value==[response]
    # Then
    assert chat_box.value==[{"Assistant": response}]
    assert len(chat_box._chat_log)==1

def test_can_patch_a_message():
    """We can handle a situation where the AI returns intermediate results and we want to display
    the current result"""
    # Given
    chat_box = ChatBox()
    prompt = "What is 2+2?"

    # When: this is our recommended best practices
    # When
    with chat_box.respond(user="Assistant") as message:
        for value in get_multiple_responses(prompt):
            message.value=value

    # Then
    assert chat_box.value == [{"Assistant": value}]

def test_can_append_to_a_message():
    """We can handle a situation where the AI returns multiple results and we want to display
    all of them"""
    # Given
    chat_box = ChatBox()
    prompt = "What is 2+2?"

    # When: this is our recommended best practices
    layout = pn.Column()
    value = []
    with chat_box.respond(user="Assistant", value=layout) as message:
        assert chat_box._chat_log.objects[0].value == [layout]
        for response in get_multiple_responses(prompt):
            layout.append(response)
            value.append(response)
            assert chat_box._chat_log.objects[0].value == [layout]
        message.final = value
    # Then:
    # Its important add the text message and not view
    # because we need the text value to give the AI context for the next task
    assert chat_box.value == [{"Assistant": message.final}]

def test_can_stream_tokens():
    """We can handle a situation where the AI streams the response as token"""
    # Given
    chat_box = ChatBox()
    prompt = "What is 2+2?"

    # When: this is our recommended best practices
    view = pn.pane.Markdown("")
    with chat_box.respond(user="Assistant", value=view) as message:
        for token in stream_response(prompt):
            view.object+=token
            assert chat_box._chat_log.objects[0].value == [view]
        message.final=view.object
    # Then:
    # Its important add the text message and not view
    # because we need the text value to give the AI context for the next task
    assert chat_box.value == [{"Assistant": message.final}]

def test_can_undo():
    # Given
    chat_box = ChatBox()
    # When: this is our recommended best practices
    def undo(event):
        if len(chat_box)>=2:
            chat_box.value=chat_box.value[:-2]

    undo_button = pn.widgets.Button(name="Undo", on_click=undo)

    chat_box.append({"User": "What is 2+2?"})
    chat_box.append({"Assistant": "4"})
    undo_button.param.trigger("clicks")

    # Then
    assert len(chat_box)==0

def test_can_retry():
    """We can retry a prompt"""
    # Given
    chat_box = ChatBox()
    # When: this is our recommended best practices
    def retry(event):
        if len(chat_box)>=2:
            chat_box.value=chat_box.value[:-1]

    undo_button = pn.widgets.Button(name="Retry", on_click=retry)

    chat_box.append({"User": "What is 2+2?"})
    chat_box.append({"Assistant": "4"})
    undo_button.param.trigger("clicks")

    # Then
    assert len(chat_box)==1

def test_can_clear():
    """We can clear the ChatBox"""
    # Given
    chat_box = ChatBox()
    # When: this is our recommended best practices
    def clear(event):
        if len(chat_box)>0:
            chat_box.value=[]

    undo_button = pn.widgets.Button(name="Clear", on_click=clear)

    chat_box.append({"User": "What is 2+2?"})
    chat_box.append({"Assistant": "4"})
    undo_button.param.trigger("clicks")

    # Then
    assert len(chat_box)==0

def test_can_create_chat_interface_in_one_line_of_code():
    """This is what Gradio offers

    See: https://twitter.com/Gradio/status/1681019345500078080
    """
    # Given
    def response(prompt, value):
        return get_response(prompt)
    prompt="What is 2+2?"
    message = {"User": prompt}
    answer = {"Assistant": get_response(prompt)}
    # When
    chat_box = ChatBox(response=response)
    chat_box.append(message)

    # Assert
    assert chat_box.value==[
        message, answer
    ]

def test_can_create_streaming_chat_interface_in_one_line_of_code():
    """This is what Gradio offers

    See: https://twitter.com/Gradio/status/1681019345500078080
    """
    # Given
    def response(prompt, value):
        for token in stream_response(prompt):
            yield token

    prompt="What is 2+2?"
    message = {"User": prompt}
    answer = {"Assistant": "".join(stream_response(prompt))}
    # When
    chat_box = ChatBox(response=response)
    chat_box.append(message)

    # Assert
    assert chat_box.value==[
        message, answer
    ]
