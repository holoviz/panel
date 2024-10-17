"""Test the ExamplePicker

The ExamplePicker can be used to pick Examples from a list of Examples and provide the example as
input to one or more callables.
"""
import pandas as pd
import pytest

import panel as pn

from panel.widgets import ExamplePicker
from panel.widgets.example_picker import Example

# value, name, thumbnail

def test_create():
    example = Example(value="example")
    assert example.value=="example"

IMAGE = ""

class ClassWithNameAttribute():
    def __init__(self, name):
        self.name = name

@pytest.mark.parametrize(["value", "expected"], [
    # Specific name
    ("some-text", "some-text"),
    (None, "None"),
    (1, "1"),
    (1.2, "1.2"),
    ("https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", "pno-cs.mp3"),
    ("https://example.com/image.png", "image.png"),
    ("image.png", "image.png"),
    (ClassWithNameAttribute("my-name"), "my-name"),
    # Not specific Name
    (pd.DataFrame(), "Example"),
    (pd.Series(), "Example"),
    ({"a": "b"}, "Example"),
])
def test_get_name(value, expected):
    assert Example._get_name(value)==expected

@pytest.mark.parametrize(["value", "expected"], [
    # Thumbnail
    ("https://example.com/image.png", "https://example.com/image.png"),
    ("image.png", "image.png"),
    # Not thumbnail
    (None, ""),
    ("some-text", ""),
    (1, ""),
    (1.2, ""),
    (pd.DataFrame(), ""),
    (pd.Series(), ""),
    ({"a": "b"}, ""),
    ("https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", ""),
])
def test_get_thumbnail(value, expected):
    assert Example._get_thumbnail(value)==expected

def test_example_as_button():
    example = Example(value="example")
    example.as_button()
    # Todo: add asserts

def test_example_as_row():
    example = Example(value="example")
    example.as_row()
    # Todo: add asserts

def test_example_picker_init_from_examples():
    examples = [Example("example1"), Example("example2")]
    example_picker = ExamplePicker(*examples)
    assert list(example_picker)==examples
    assert example_picker.__panel__()

def test_example_picker_init_from_non_examples():
    examples = ["example1", "example2"]
    example_picker = ExamplePicker(*examples)
    assert list(example_picker)==[Example(example) for example in examples]
    assert example_picker.__panel__()

def test_can_watch():
    example_picker = ExamplePicker("example1", "example2")
    example_picker[0].param.trigger("click")
    assert example_picker.value == example_picker[0].value
    example_picker[1].param.trigger("click")
    assert example_picker.value == example_picker[1].value

def test_can_bind():
    widget = pn.widgets.TextInput()
    example_picker = ExamplePicker("example1", "example2")
    example_picker.bind(widget)

def test_can_select():
    widget = pn.widgets.TextInput()
    example_picker = ExamplePicker("example1", "example2", targets=widget)
    example_picker[0].param.trigger("click")
    assert example_picker.value == example_picker[0].value
    example_picker[1].param.trigger("click")
    assert example_picker.value == example_picker[1].value

@pytest.mark.parametrize("name, expected_name, start_index, expected_index", [
    ("", "Example 1", 1, 2),          # Empty name should be updated
    # ("example", "Example 1", 1, 2),   # Name "example" should be updated (case insensitive)
    # ("Example", "Example 1", 1, 2),   # Name "Example" should be updated
    # ("test", "test", 1, 1),           # Name "test" should not be updated
])
def test_clean_name(name, expected_name, start_index, expected_index):
    example = Example(value="", name=name)

    result_index = example._clean_name(start_index)

    # Check if the index is correctly updated
    assert result_index == expected_index
    # Check if the name is updated as expected
    assert example.name == expected_name
