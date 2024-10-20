"""Test the `Example`

The `Example` can be used like a Button to provide the example `value` to a target or a list of targets.
"""
from pathlib import Path

import pandas as pd
import pytest

import panel as pn

from panel.widgets import Example

EXAMPLE_IMAGE = (Path(__file__).parent.parent/"assets"/"example-image.png").absolute()

# value, name, thumbnail

def test_create():
    example = Example(value="example")
    assert example.value=="example"
    layout = example._get_layout()
    assert isinstance(layout, pn.widgets.Button)
    assert layout.name==example.name

def test_create_row_layout():
    example = Example(value=1, layout=pn.Row)
    layout = example._get_layout()
    assert isinstance(layout, pn.Row)
    assert isinstance(layout[0], pn.widgets.Button)
    assert layout[0].name=="1"


IMAGE = ""

class ClassWithNameAttribute():
    def __init__(self, name):
        self.name = name

object_with_name_attribute = ClassWithNameAttribute("my-name")
empty_dataframe = pd.DataFrame()
empty_series = pd.Series()

TEST_EXAMPLES = [
    ("https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", Example("https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", "pno-cs.mp3", "")),
    ("https://example.com/image.png", Example("https://example.com/image.png", "image.png", "https://example.com/image.png")),
    ("image.png", Example("image.png", "image.png", "image.png")),
    ("some-text", Example("some-text", "some-text", "")),
    ({"a": "b"}, Example({"a": "b"}, "Example", "")),
    (["a", "b"], Example(["a", "b"], "Example", "")),
    (1, Example(1, "1", "")),
    (1.2, Example(1.2, "1.2", "")),
    (empty_dataframe, Example(empty_dataframe, "Example", "")),
    (empty_series, Example(empty_series, "Example", "")),
    (None, Example(None, "None", "")),
    (object_with_name_attribute, Example(object_with_name_attribute, "my-name", "")),
]

def test_instantiation_with_no_value():
    with pytest.raises(TypeError):
        Example()

@pytest.mark.parametrize(["value", "expected"], TEST_EXAMPLES)
def test_instantiation_from_value(value, expected):
    example = Example(value)
    assert example==expected
    assert example.to_dict()
    assert repr(example)
    example.layout=None
    assert example.__panel__()
    assert isinstance(example._get_layout(), pn.widgets.Button)
    example.layout=pn.Row
    assert example.__panel__()
    assert isinstance(example._get_layout(), pn.Row)


def test_can_set_single_target():
    widget = pn.widgets.TextInput()
    example = Example("example1", "example2", targets=widget)
    example.param.trigger("click")
    assert widget.value == example.value

def test_can_set_multiple_targets():
    widget1 = pn.widgets.TextInput()
    widget2 = pn.widgets.TextInput()
    targets = [widget1, widget2]
    example = Example(("a", "b"), targets=targets)
    example.param.trigger("click")
    assert widget1.value == example.value[0]
    assert widget2.value == example.value[1]


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

def test_can_layout_as_button():
    example = Example("example", layout=None)
    assert isinstance(example._get_layout(), pn.widgets.Button)

def test_can_layout_as_row():
    example = Example("example", layout=pn.Row)
    assert isinstance(example._get_layout(), pn.Row)

def test_button_kwargs():
    example = Example("example", button_kwargs=dict(width=101), layout=None)
    assert example._button.width==101

@pytest.mark.parametrize("value", [str(EXAMPLE_IMAGE), EXAMPLE_IMAGE])
def test_local_image_as_value(value):
    example = Example(value)
    assert example.value==value
    assert example.name=="example-image.png"
    assert example.thumbnail.startswith("data:image/png;base64,")

@pytest.mark.parametrize("thumbnail", [str(EXAMPLE_IMAGE), EXAMPLE_IMAGE])
def test_local_image_as_thumbnail(thumbnail):
    example = Example("some-value", thumbnail=thumbnail)
    assert example.value=="some-value"
    assert example.name=="some-value"
    assert example.thumbnail.startswith("data:image/png;base64,")

@pytest.mark.parametrize("value", ["http://panel.holoviz.org/_static/logo_horizontal_light_theme.png", "https://panel.holoviz.org/_static/logo_horizontal_light_theme.png"])
def test_url_image_as_value(value):
    example = Example(value)
    assert example.value==value
    assert example.name=="logo_horizontal_light_theme.png"
    assert example.thumbnail==value

@pytest.mark.parametrize("thumbnail", ["http://panel.holoviz.org/_static/logo_horizontal_light_theme.png", "https://panel.holoviz.org/_static/logo_horizontal_light_theme.png"])
def test_url_image_as_thumbnail(thumbnail):
    example = Example("some-value", thumbnail=thumbnail)
    assert example.value=="some-value"
    assert example.name=="some-value"
    assert example.thumbnail==thumbnail

def test_special_image():
    example = Example("Hello World", thumbnail="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSLZf31OpU0zqzpDS-IwNBp7lF1eejh9YJHHA&s")
    assert example.name=="Hello World"
    assert example.value=="Hello World"
    assert example.thumbnail=="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSLZf31OpU0zqzpDS-IwNBp7lF1eejh9YJHHA&s"
