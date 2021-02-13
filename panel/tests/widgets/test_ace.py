from panel.widgets import Ace


def test_ace(document, comm):
    ace = Ace(value="Hello, World", language="python")
    widget = ace.get_root(document, comm=comm)

    assert isinstance(widget, ace._widget_type)
    assert ace.value == "Hello, World"
    assert ace.language == "python"

    # Try changes
    ace._process_events({"value": "Hi there!"})
    assert ace.value == "Hi there!"
