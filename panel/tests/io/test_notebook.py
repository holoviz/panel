from panel.io.notebook import ipywidget
from panel.pane import Str

from ..util import jb_available


@jb_available
def test_ipywidget(document):
    pane = Str('A')
    widget = ipywidget(pane, doc=document)

    assert widget._view_count == 0
    assert len(pane._models) == 1

    init_id = list(pane._models)[0]

    widget._view_count = 1

    assert widget._view_count == 1
    assert init_id in pane._models

    widget._view_count = 0

    assert len(pane._models) == 0

    widget._view_count = 1

    assert len(pane._models) == 1
    prev_id = list(pane._models)[0]

    widget.notify_change({'new': 1, 'old': 1, 'name': '_view_count',
                          'type': 'change', 'model': widget})
    assert prev_id in pane._models
    assert len(pane._models) == 1

    widget._view_count = 2

    assert prev_id in pane._models
    assert len(pane._models) == 1
