from panel.io.document import unlocked
from panel.io.state import set_curdoc
from panel.tests.util import serve_and_request
from panel.widgets import IntSlider


def test_document_hold():
    slider = IntSlider()

    serve_and_request(slider)

    doc, model = list(slider._documents.items())[0]

    doc.hold()

    with set_curdoc(doc):
        with unlocked():
            model.value = 3

    assert doc.callbacks._held_events
