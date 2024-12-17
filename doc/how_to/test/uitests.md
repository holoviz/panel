# Test UI rendering

This guide addresses how to test the UI with Pytest and Playwright.

---

Testing is key to developing robust and performant applications. Particularly when you build complex UIs you will want to ensure that it behaves as expected. Unit tests will allow you test that the logic on the backend behaves correctly, but it is also useful to test that the UI is rendered correctly and responds appropriately.

For testing the UI we recommend the framework [Playwright](https://playwright.dev/). Panel itself is tested with this framework.

Before you get started ensure you have installed the required dependencies:

```bash
pip install panel pytest pytest-playwright
```

and ensure `playwright` sets up the browsers it will use to display the applications:

```bash
playwright install
```

## Create the app

Let's create a simple data app for testing. The app sleeps 0.5 seconds (default) when loaded and when the button is clicked.

![app.py](https://assets.holoviz.org/panel/gifs/pytest.gif)

Create the file `app.py` and add the code below (don't worry about the contents of the app for now):

:::{card} app.py

```{code-block} python

import time

import panel as pn
import param

class App(pn.viewable.Viewer):
    run = param.Event(doc="Runs for click_delay seconds when clicked")
    runs = param.Integer(doc="The number of runs")
    status = param.String(default="No runs yet")

    load_delay = param.Number(default=0.5)
    run_delay = param.Number(default=0.5)

    def __init__(self, **params):
        super().__init__(**params)

        result = self._load()
        self._time = time.time()


        self._status_pane = pn.pane.Markdown(self.status, height=40, align="start", margin=(0,5,10,5))
        self._result_pane = pn.Column(result)
        self._view = pn.Column(
            pn.Row(pn.widgets.Button.from_param(self.param.run, sizing_mode="fixed"), self._status_pane),
            self._result_pane
        )

    def __panel__(self):
        return self._view

    def _start_run(self):
        self.status = f"Running ..."
        self._time = time.time()

    def _stop_run(self):
        now = time.time()
        duration = round(now-self._time,3)
        self._time = now
        self.runs+=1
        self.status=f"Finished run {self.runs} in {duration}sec"

    @param.depends("run", watch=True)
    def _run_with_status_update(self):
        self._start_run()
        self._result_pane[:] = [self._run()]
        self._stop_run()

    @param.depends("status", watch=True)
    def _update_status_pane(self):
        self._status_pane.object = self.status

    def _load(self):
        time.sleep(self.load_delay)
        return "Loaded"

    def _run(self):
        time.sleep(self.run_delay)
        return f"Result {self.runs+1}"


if pn.state.served:
    pn.extension(sizing_mode="stretch_width")

    App().servable()
```

:::

Serve the app via `panel serve app.py` and open [http://localhost:5006/app](http://localhost:5006/app) in your browser to see what it does.

## Create a conftest.py

The `conftest.py` file should be placed alongside your tests and will be loaded automatically by pytest. It is often used to declare [fixtures](https://docs.pytest.org/en/latest/explanation/fixtures.html) that allow you declare reusable components. It will:

- provide us with an available `port`.
- clean up the Panel *state* after each test.

Create the file `conftest.py` and add the code below.

:::{card} conftest.py

```{code-block} python

"""Shared configuration and fixtures for testing Panel"""
import panel as pn
import pytest

PORT = [6000]

@pytest.fixture
def port():
    PORT[0] += 1
    return PORT[0]

@pytest.fixture(autouse=True)
def server_cleanup():
    """
    Clean up server state after each test.
    """
    try:
        yield
    finally:
        pn.state.reset()
```

:::

For more inspiration see the [Panel `conftest.py` file](https://github.com/holoviz/panel/blob/main/panel/tests/conftest.py)

### Test the app UI

Now let us actually set up some UI tests, we will want to assert that the app:

- Responds when we make an initial request
- Renders a *Run* button
- Updates as expected when the *Run* button is clicked

Create the file `test_app_frontend.py` and add the code below.

:::{card} test_app_frontend.py

```{code-block} python

import time

import panel as pn
from app import App

CLICKS = 2

def test_component(page, port):
    # Given
    component = App()
    url = f"http://localhost:{port}"
    # When
    server = pn.serve(component, port=port, threaded=True, show=False)
    time.sleep(0.2)
    # Then
    page.goto(url)
    page.get_by_role("button", name="Run").wait_for()

    for index in range(CLICKS):
        page.get_by_role("button", name="Run").first.click()
        page.get_by_text(f"Finished run {index+1}").wait_for()
    # Clean up
    server.stop()
```

:::

Let's run `pytest`. We will add the `--headed` and `--slowmo` arguments to see what is going on in the browser. This is very illustrative and also helpful for debugging purposes.

```bash
pytest test_app_frontend.py --headed --slowmo 1000
```

![Playwright UI test with --headed enabled](https://assets.holoviz.org/panel/gifs/uitest.gif)

### Record the test code

Writing code to test complex UIs can be quite cumbersome, thankfully there is an easier way. Playwright allows you to record UI interactions as you navigate your live app and translates these interactions as code (see the [Playwright codegen](https://playwright.dev/python/docs/codegen) documentation for more detail).

You can try it yourself by launching the app again:

```bash
panel serve app.py
```

and starting the Playwright recorder:

```bash
playwright codegen http://localhost:5006/app
```

![Playwright Code generation demo](https://assets.holoviz.org/panel/gifs/codegen.gif)

## Related Resources
