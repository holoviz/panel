from concurrent.futures import ThreadPoolExecutor

import pytest

from bokeh.document import Document

import panel as pn

from panel.io.document import _cleanup_doc, hold, unlocked
from panel.io.state import _state, set_curdoc, state
from panel.tests.util import serve_and_request, wait_until
from panel.widgets import IntSlider


def test_cleanup_doc_does_not_shadow_class_views():
    doc = Document()
    pane = pn.pane.Markdown("test")
    pane.get_root(doc)

    assert state._views
    views_id_before = id(_state._views)

    _cleanup_doc(doc, destroy=True)

    # The class-level dict should be mutated in place, not shadowed
    assert id(_state._views) == views_id_before
    # No instance-level shadow should be created
    assert '_views' not in state.__dict__
    # The entry should be cleaned up
    assert not state._views


def test_document_hold():
    slider = IntSlider()

    serve_and_request(slider)

    doc, model = list(slider._documents.items())[0]

    doc.hold()

    with set_curdoc(doc):
        with unlocked():
            model.value = 3

    assert doc.callbacks._held_events


@pytest.mark.xdist_group(name="server")
def test_hold_does_not_get_stuck_with_threaded_callbacks(threads):
    column = pn.FlexBox(*[pn.pane.Str('0') for _ in range(20)])
    layout = pn.Column(column)

    serve_and_request(layout)

    doc = list(layout._documents.keys())[0]

    def update_in_hold(i):
        with set_curdoc(doc):
            with hold(doc):
                for obj in column:
                    obj.object = str(i)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(update_in_hold, i) for i in range(10)]
        for f in futures:
            f.result()

    wait_until(lambda: not doc.callbacks.hold_value, timeout=5000)
