from unittest.mock import patch

import pytest

from panel import config
from panel.widgets import CodeEditor


def test_ace(document, comm):
    editor = CodeEditor(value="Hello, World", language="python")
    widget = editor.get_root(document, comm=comm)

    assert isinstance(widget, editor._widget_type)
    assert editor.value == "Hello, World"
    assert editor.language == "python"

    # Try changes
    editor._process_events({"value": "Hi there!"})
    assert editor.value == "Hi there!"


def test_ace_keyboard_accessible_and_soft_wrap(document, comm):
    editor = CodeEditor(value="x", keyboard_accessible=True, soft_wrap=True)
    model = editor.get_root(document, comm=comm)
    assert model.keyboard_accessible and model.soft_wrap

    editor.param.update(keyboard_accessible=False, soft_wrap=False)
    assert not model.keyboard_accessible and not model.soft_wrap


def test_ace_input(document, comm):
    editor = CodeEditor(value="", language="python")
    editor.value = "Hello World!"
    assert editor.value == "Hello World!"
    assert editor.value_input == "Hello World!"

    editor.value = ""
    assert editor.value == ""
    assert editor.value_input == ""

def test_code_editor_theme():
    assert CodeEditor(value="My theme is appropriate").theme == CodeEditor.param.theme.default
    assert CodeEditor(value="My theme is appropriate", theme="dracula").theme == "dracula"

    with patch('panel.config._config.theme', new_callable=lambda: "default"):
        assert CodeEditor(value="My theme is appropriate").theme == CodeEditor.param.theme.default

    with patch('panel.config._config.theme', new_callable=lambda: "dark"):
        assert CodeEditor(value="My theme is appropriate").theme == CodeEditor.THEME_CONFIGURATION[config.theme]

    with patch('panel.config._config.theme', new_callable=lambda: "dark"):
        assert CodeEditor(value="My theme is appropriate", theme="chrome").theme == "chrome"


def test_ace_markers(document, comm):
    markers = [{"start_row": 0, "end_row": 1, "gutter_class": "changed"}]
    editor = CodeEditor(value="a\nb\nc", markers=markers)
    model = editor.get_root(document, comm=comm)
    assert model.markers == markers

    editor.markers = [{"start_row": 2, "class": "only"}]
    assert model.markers == [{"start_row": 2, "class": "only"}]

    editor.markers = []
    assert model.markers == []


@pytest.mark.parametrize("marker", [
    {"end_row": 1},
    {"start_row": "1"},
    {"start_row": -1},
    {"start_row": True},
    {"start_row": 0, "end_row": False},
    {"start_row": 2, "end_row": 1},
    {"start_row": 0, "type": "block"},
])
def test_ace_markers_invalid(marker):
    with pytest.raises(ValueError):
        CodeEditor(markers=[marker])


def test_ace_markers_invalid_not_stored():
    markers = [{"start_row": 1}]
    editor = CodeEditor(markers=markers)
    with pytest.raises(ValueError):
        editor.markers = [{"start_row": -1}]
    assert editor.markers == markers
