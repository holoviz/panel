import time

import pytest
import traitlets

from bokeh.core.has_props import _default_resolver
from bokeh.model import Model

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.layout import Row
from panel.pane.ipywidget import Reacton

try:
    import reacton
except Exception:
    reacton = None
requires_reacton = pytest.mark.skipif(reacton is None, reason="requires reaction")

try:
    import anywidget
except Exception:
    anywidget = None
requires_anywidget = pytest.mark.skipif(anywidget is None, reason="requires anywidget")

@pytest.fixture(scope="module", autouse=True)
def cleanup_ipywidgets():
    old_models = dict(Model.model_class_reverse_map)
    yield
    _default_resolver._known_models = old_models

@requires_reacton
def test_reacton(page, port):
    import reacton
    import reacton.ipywidgets

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

        button = reacton.ipywidgets.Button(
            description=f"Clicked {clicks} times",
            on_click=my_click_handler
        )
        return button

    reacton_app = Row(
        Reacton(ButtonClick(), width=200, height=50)
    )

    serve(reacton_app, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    time.sleep(0.5)

    assert runs

    page.locator('button.jupyter-button').click()

    time.sleep(0.5)

    assert click

    reacton_app[:] = []

    time.sleep(0.5)

    assert cleanups


@requires_anywidget()
def test_anywidget(page, port):

    class CounterWidget(anywidget.AnyWidget):
        # Widget front-end JavaScript code
        _esm = """
        export function render(view) {
          let getCount = () => view.model.get("count");
          let button = document.createElement("button");
          button.innerHTML = `count is ${getCount()}`;
          button.addEventListener("click", () => {
            view.model.set("count", getCount() + 1);
            view.model.save_changes();
          });
          view.model.on("change:count", () => {
            button.innerHTML = `count is ${getCount()}`;
          });
          view.el.appendChild(button);
        }
        """
        # Stateful property that can be accessed by JavaScript & Python
        count = traitlets.Int(0).tag(sync=True)

    counter = CounterWidget()

    serve(counter, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    time.sleep(0.2)

    page.locator('.lm-Widget button').click()

    time.sleep(0.2)

    assert counter.count == 1

    page.locator('.lm-Widget button').click()

    time.sleep(0.2)

    assert counter.count == 2
