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
