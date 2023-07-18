"""Test common ChatBox use cases

The purpose is to make sure they can be implemented in a simple and performant way with a
good user experience.

Should go hand in hand with documentation
"""
import pytest

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
    yield "response ..."

def stream_response(prompt):
    for token in RESPONSE.split():
        yield token

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

def test_can_get_single_message(messages):
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



def test_can_disable_chatbox_while_providing_slow_response():
    """The ChatBox can easily be disabled while a slow response is generated"""
    chat_box = ChatBox()
    prompt = "What is 2+2?"

    # When: this is our recommended best practices
    org_value = chat_box.disabled
    try:
        chat_box.disabled=True
        answer = {"Assistant": get_response(prompt)}
    except Exception as ex:
        answer = {"Assistant": str(ex)}
    finally:
        chat_box.append(answer)
        chat_box.disabled=org_value

    # Then
    assert chat_box.disabled==False


def test_can_provide_spinner_while_providing_slow_response():
    chat_box = ChatBox()
    prompt = "What is 2+2?"

    # When: this is our recommended best practices
    message = {"Assistant": LoadingSpinner(value=True, height=25, color="success")}
    chat_box.append(message)
    try:
        response = get_response(prompt)
    except Exception as ex:
        response = str(ex)
    finally:
        message["Assistant"]=response
        chat_box.param.trigger("value")

    # Then
    assert chat_box.disabled==False
