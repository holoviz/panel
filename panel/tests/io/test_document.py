import time

import requests

from panel.io.document import unlocked
from panel.io.server import serve
from panel.io.state import set_curdoc
from panel.widgets import IntSlider


def test_document_hold(port):
    slider = IntSlider()

    serve(slider, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    doc, model = list(slider._documents.items())[0]

    doc.hold()

    with set_curdoc(doc):
        with unlocked():
            model.value = 3

    assert doc.callbacks._held_events
