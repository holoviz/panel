from __future__ import annotations

import pytest

pytest.importorskip("ipywidgets")
pytest.importorskip("playwright")

import traitlets

from bokeh.core.has_props import _default_resolver
from bokeh.model import Model

from panel.layout import Row
from panel.pane.ipywidget import Reacton
from panel.tests.util import serve_component, wait_until

try:
    import reacton
except Exception:
    reacton = None  # type: ignore
requires_reacton = pytest.mark.skipif(reacton is None, reason="requires reaction")

try:
    import anywidget
except Exception:
    anywidget = None  # type: ignore
requires_anywidget = pytest.mark.skipif(anywidget is None, reason="requires anywidget")

pytestmark = pytest.mark.ui


@pytest.fixture(scope="module", autouse=True)
def cleanup_ipywidgets():
    old_models = dict(Model.model_class_reverse_map)
    yield
    _default_resolver._known_models = old_models

@requires_reacton
def test_reacton(page):
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

    serve_component(page, reacton_app)

    wait_until(lambda: bool(runs), page)

    page.locator('button.jupyter-button').click()

    wait_until(lambda: bool(click), page)

    reacton_app[:] = []

    wait_until(lambda: bool(cleanups), page)


@requires_anywidget()
def test_anywidget(page):

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

    serve_component(page, counter)

    page.locator('.lm-Widget button').click()

    wait_until(lambda: counter.count == 1, page)

    page.locator('.lm-Widget button').click()

    wait_until(lambda: counter.count == 2, page)
