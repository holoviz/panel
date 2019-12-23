from __future__ import absolute_import, division, unicode_literals

from panel.widgets import Ace


def test_ace(document, comm):
    ace = Ace(value="Hello, World", language="python")
    widget = ace.get_root(document, comm=comm)

    assert isinstance(widget, ace._widget_type)
    assert ace.value == "Hello, World"
    assert ace.language == "python"

    # Try changes
    ace._comm_change({"value": "Hi there!"})
    assert ace.value == "Hi there!"
