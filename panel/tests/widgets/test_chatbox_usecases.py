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
    for token in RESPONSE.split():
        yield token

# Todo: Todo: Support Async versions of everything

# TESTS

def test_can_provide_response():
    """The user can quickly add a new response"""
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
    # Give
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
    chat_box = ChatBox()
    prompt = "What is 2+2?"

    # When: this is our recommended best practices
    with chat_box.respond(user="Assistant") as message:
        # Then
        assert chat_box.disabled
        # When
        response = get_response(prompt)
        message.value = response
    # Then
    assert not chat_box.disabled

def test_can_provide_custom_spinner_while_providing_slow_response():
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
        for response in get_multiple_responses(prompt):
            message.value=response

    # Then
    assert chat_box.value == [{"Assistant": response}]

def test_can_append_to_a_message():
    """We can handle a situation where the AI returns multiple results and we want to display
    all of them"""
    # Given
    chat_box = ChatBox()
    prompt = "What is 2+2?"

    # When: this is our recommended best practices
    # Todo: Fix issue that value change is triggered before final value delivered
    layout = pn.Column()
    with chat_box.respond(user="Assistant", value=layout):
        assert chat_box._chat_log.objects[0].value == [layout]
        for response in get_multiple_responses(prompt):
            layout.append(response)
            assert chat_box._chat_log.objects[0].value == [layout]
    # Then
    assert chat_box.value == [{"Assistant": layout}]

def test_can_stream_tokens():
    """We can handle a situation where the AI streams the response as token"""
    # Given
    chat_box = ChatBox()
    prompt = "What is 2+2?"

    # When: this is our recommended best practices
    # Todo: Fix issue that value change is triggered before final value delivered
    text = ""
    layout = pn.Column(text)
    with chat_box.respond(user="Assistant", value=layout):
        for token in stream_response(prompt):
            text+=token
            layout[0]=text
            assert chat_box._chat_log.objects[0].value == [layout]
    # Then
    assert chat_box.value == [{"Assistant": layout}]
    assert layout[0].object==text
