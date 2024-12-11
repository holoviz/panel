"""Test the Examples widget

The Examples widget can be used to pick Examples from a list of Examples and provide the example as
input to one or more callables.
"""
import pytest

import panel as pn

from panel.widgets import Examples
from panel.widgets.examples import Example

# value, name, thumbnail

def test_examples_init():
    examples = []
    examples = Examples(*examples)
    assert list(examples)==[]
    assert examples.__panel__()

def test_examples_init_from_list_of_examples():
    samples = [Example("example1"), Example("example2")]
    examples = Examples(*samples)
    assert list(examples)==samples
    assert examples.__panel__()

def test_examples_init_from_non_examples():
    samples = ["example1", "example2"]
    examples = Examples(*samples)
    assert list(examples)==[Example(sample) for sample in samples]
    assert examples.__panel__()

def test_can_watch():
    examples = Examples("example1", "example2")
    examples[0].param.trigger("click")
    assert examples.value == examples[0].value
    examples[1].param.trigger("click")
    assert examples.value == examples[1].value

def test_can_select():
    widget = pn.widgets.TextInput()
    examples = Examples("example1", "example2", targets=widget)
    examples[0].param.trigger("click")
    assert examples.value == examples[0].value
    examples[1].param.trigger("click")
    assert examples.value == examples[1].value

@pytest.mark.parametrize("name, expected_name, start_index, expected_index", [
    ("", "Example 1", 1, 2),          # Empty name should be updated
    ("example", "Example 1", 1, 2),   # Name "example" should be updated (case insensitive)
    ("Example", "Example 1", 1, 2),   # Name "Example" should be updated
    ("test", "test", 1, 1),           # Name "test" should not be updated
])
def test_clean_name(name, expected_name, start_index, expected_index):
    example = Example(value="", name=name)

    result_index = example._clean_name(start_index)

    # Check if the index is correctly updated
    assert result_index == expected_index
    # Check if the name is updated as expected
    assert example.name == expected_name
