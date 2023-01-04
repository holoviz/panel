# How to test the UI of data apps with Pytest and PlayWright

Testing is key to developing robust and performant applications. You can test Panel data apps using Python and the test tools you know and love.

Sometimes, for example when you create [custom components](https://panel.holoviz.org/user_guide/Custom_Components.html), it can be useful to also test the UI.

For testing the UI we recommend the framework [Playwright](https://playwright.dev/) by Microsoft. Panel itself is tested with this framework.

Before you get started please install the packages

```bash
pip install panel pytest pytest-playwright
```

and the browsers

```bash
playwright install
```

## Create the app

Lets create a simple data app for testing. The app sleeps 0.5 seconds (default) when loaded and when the button is clicked.

![app.py](https://user-images.githubusercontent.com/42288570/210162656-ae771b17-d406-4aa2-8e58-182270fbd7c1.gif)

Create the file `app.py` and add the code below.

```python
# app.py
import time

import panel as pn
import param

class App(pn.viewable.Viewer):
    run = param.Event(doc="Runs for click_delay seconds when clicked")
    runs = param.Integer(doc="The number of runs")
    status = param.String("No runs yet")

    load_delay = param.Number(0.5)
    run_delay = param.Number(0.5)

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

    @pn.depends("run", watch=True)
    def _run_with_status_update(self):
        self._start_run()
        self._result_pane[:] = [self._run()]
        self._stop_run()

    @pn.depends("status", watch=True)
    def _update_status_pane(self):
        self._status_pane.object = self.status

    def _load(self):
        time.sleep(self.load_delay)
        return "Loaded"

    def _run(self):
        time.sleep(self.run_delay)
        return f"Result {self.runs+1}"

if __name__.startswith("bokeh"):
    pn.extension(sizing_mode="stretch_width")
    App().servable()
```

Serve the app via `panel serve app.py` and open [http://localhost:5006/app](http://localhost:5006/app) in your browser.

### Create the conftest.py

The `conftest.py` file contains pytest fixtures. it will

- provide us with an available `port`
- clean up the Panel *state* after each test.

Create the file `conftest.py` and add the code below.

```python
# conftest.py
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
        pn.state.kill_all_servers()
        pn.state._indicators.clear()
        pn.state._locations.clear()
        pn.state._templates.clear()
        pn.state._views.clear()
        pn.state._loaded.clear()
        pn.state.cache.clear()
        pn.state._scheduled.clear()
        if pn.state._thread_pool is not None:
            pn.state._thread_pool.shutdown(wait=False)
            pn.state._thread_pool = None
```

For more inspiration check out the [Panel `conftest.py` file](https://github.com/holoviz/panel/blob/master/panel/tests/conftest.py)

### Test the app UI

Lets test that the app will

- respond when we make an initial request
- provide a *Run* button
- Update the app as expected when the *Run* button is clicked

Create the file `test_app_frontend.py` and add the code below.

```python
# test_app_frontend.py
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

Lets run `pytest`. We will add the `--headed` argument to see what is going on in the browser. This is very illustrative and also helpful for debugging purposes.

```bash
pytest test_app_frontend.py --headed
```

![panel-pytest-frontend.gif](https://user-images.githubusercontent.com/42288570/210163005-29e26514-02a3-4076-92c5-ba4e8d14dd30.gif)

### Record the test code

Its relatively easy to create the test code because Playwright allows you to record the code as you navigate your live app. See the Playwright [codegen](https://playwright.dev/python/docs/codegen) docs.

You can try it by starting the Panel server

```bash
panel serve app.py
```

and starting the Playwright recorder

```bash
playwright codegen http://localhost:5006/app
```

![panel-playwright-recording.gif](https://user-images.githubusercontent.com/42288570/210163133-bf08e9cd-2599-4c7e-a017-ba447547f0e0.gif)
