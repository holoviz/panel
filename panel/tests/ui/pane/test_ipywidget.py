import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.layout import Row
from panel.pane.ipywidget import Reacton


def test_reacton(page, port):
    import reacton.ipywidgets as w

    import reacton

    runs, cleanups, click = [], [], []

    @reacton.component
    def ButtonClick():
        # first render, this return 0, after that, the last argument
        # of set_clicks
        clicks, set_clicks = reacton.use_state(0)

        def test_effect():
            runs.append(button)
            def cleanup():
                cleanups.append(button)
            return cleanup
        reacton.use_effect(test_effect, [])

        def my_click_handler():
            # trigger a new render with a new value for clicks
            click.append(clicks+1)
            set_clicks(clicks+1)

        button = w.Button(description=f"Clicked {clicks} times",
                          on_click=my_click_handler)
        return button

    reacton_app = Row(
        Reacton(ButtonClick(), width=200, height=50)
    )

    serve(reacton_app, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    time.sleep(0.5)

    assert runs

    page.locator('button.jupyter-button').click()

    time.sleep(0.5)

    assert click

    reacton_app[:] = []

    time.sleep(0.5)

    assert cleanups
