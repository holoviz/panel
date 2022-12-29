# How to test Panel apps

Testing is key to developing robust and performant applications.

Panel is a reactive, python framework based on Param. This makes it easy to test Panel data apps using Python and the test tools you know and love.

Before we get started you should

```bash
pip install panel pytest pytest-benchmark locust-plugins pytest-playwright playwright
```

and install the browsers

```bash
playwright install
```

## Create the app

Lets create a data app in a file called `app.py`.

```python
# app.py
import asyncio
import time

import panel as pn
import param

class App(pn.viewable.Viewer):
    run = param.Event()
    runs = param.Integer()
    status = param.String("Click Run")

    load_delay = param.Number(0.5)
    click_delay = param.Number(0.5)
    
    def __init__(self, **params):
        super().__init__(**params)
        
        self.load()
        self._time = time.time()


        self._status_pane = pn.pane.Markdown(self.status, height=33)
        self._view = pn.Column(
            pn.widgets.Button.from_param(self.param.run, align="end"),
            self._status_pane
        )

    def __panel__(self):
        return self._view

    def _start_run(self):
        self.status = f"Running ..."
        self._start = time.time()

    def _stop_run(self):
        now = time.time()
        duration = round(now-self._time,3)
        self._time = now
        self.runs+=1
        self.status=f"Finished run {self.runs} in {duration}sec"

    @pn.depends("run", watch=True)
    def _run(self):
        self._start_run()
        self.handle_click()
        self._stop_run()        

    @pn.depends("status", watch=True)
    def _update_status_pane(self):
        print(self.status)
        self._status_pane.object = self.status

    def load(self):
        time.sleep(self.load_delay)

    def handle_click(self):
        time.sleep(self.click_delay)
    
if __name__.startswith("bokeh"):
    app = App()
    pn.panel(app).servable()
```

Try serving the app: `panel serve app.py`. It should look like

![app.py](https://user-images.githubusercontent.com/42288570/209909169-23849050-7401-4f01-bbdb-79ded3a33b4f.gif)

## Test the backend with Pytest

Lets test

- The initial *state* of the App
- That the app *state* changes appropriately when the *Run* button is clicked.
- That the duration of the *run* is as expected.

We can test all these things via the `test_app.py` file below.

```python
# test_app.py
import pytest

from app import App

@pytest.fixture
def app():
    return App(sleep_delay=0.001, load_delay=0.001)

def test_constructor(app):
    """Tests default values of App"""
    # Then
    assert app.run == False
    assert app.status == "Click Run"
    assert app.runs == 0

def test_run(app):
    """Tests behaviour when Run button is clicked once"""
    # When
    app.run=True
    # Then
    assert app.runs == 1
    assert app.status.startswith("Finished run 1 in")

def test_run_twice(app):
    """Tests behaviour when Run button is clicked twice"""
    # When
    app.run=True
    app.run=True
    # Then
    assert app.runs == 2
    assert app.status.startswith("Finished run 2 in")

def test_run_performance(app: App, benchmark):
    """Test the duration when Run button is clicked"""
    app.click_delay=0.3

    def run():
        app.run=True

    benchmark(run)
    assert benchmark.stats['min'] >= 0.3
    assert benchmark.stats['max'] < 0.4
```

Lets run `pytest`.

```bash
$ pytest test_app.py
======================================================================= test session starts

collected 4 items

test_app.py ....                                                                                                                                             [100%]


------------------------------------------------- benchmark: 1 tests ------------------------------------------------
Name (time in ms)             Min       Max      Mean  StdDev    Median     IQR  Outliers     OPS  Rounds  Iterations
---------------------------------------------------------------------------------------------------------------------
test_run_performance     308.4448  311.8413  310.1718  1.2477  310.1379  1.5623       2;0  3.2240       5           1
---------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
================================================================== 4 passed in 4.82s
```

Please note that **normally Panel users just need to test the backend behaviour**. The Panel developers have already tested the frontend behaviour. This makes Panel data apps really simple to test.

## Test the frontend with pytest and PlayWright

Sometimes, for example when you create [custom components](https://panel.holoviz.org/user_guide/Custom_Components.html), it can be useful to test the frontend behaviour.

For testing the frontend we recommend the framework [Playwright](https://playwright.dev/) by Microsoft. Panel it self is tested by this framework.

### Create the conftest.py

The `conftest.py` file contains pytest fixtures. it will 

- provide us with an available `port`
- clean up the Panel server after each test.

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

### Test the app

Lets test that the app will

- respond when we make an initial request
- provide a *Run* button
- Update the app as expected when the *Run* button is clicked

We can test all this via the `test_app_frontend.py` file below.

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

![panel-pytest-frontend.gif](https://user-images.githubusercontent.com/42288570/209915079-d2dfd7dd-77e1-4e04-b022-5f2f49852c31.gif)

### Record the test code

Its relatively easy to create the test code because Playwright allows you to record the code as you navigate your live app. See the PlayWright [codegen](https://playwright.dev/python/docs/codegen) docs.

You can try it by starting the Panel server

```bash
panel serve app.py
```

and starting the PlayWright recorder

```bash
playwright codegen http://localhost:5006/app
```

![panel-playwright-recording.gif](https://user-images.githubusercontent.com/42288570/209916542-acd17660-90ae-4246-a417-5fd8fc79dc3f.gif)

## Test the load

Load testing refers to testing the performance of the entire Panel application and the server(s) running it.

This kind of testing is really useful if you want to 

- develop fast and snappy apps and/ or
- develop apps that scale to many users

[Locust]() will help you mimic the behaviour of users that interacts with your Panel app. It will provide many useful statistics for the duration of the interactions.

```python

```

### Test requests with Locust

We can test how our app performs when users request the page to load.

Create the file `locust.py`.

```python
#locust.py
from locust import HttpUser, task

class RequestOnlyUser(HttpUser):
    @task
    def app(self):
        self.client.get("/app")
```

Start the Panel server

```bash
panel serve app.py
```

Start the Locust server

```bash
locust --host http://localhost:5006
```

Keep the default settings and click the *Start swarming* button. This should look like the below.

![panel-locust.gif](https://user-images.githubusercontent.com/42288570/209923009-521554d4-dcf8-49b3-8cca-c714037af901.gif)

The median response time (on my laptop) is ~530ms when one user requests the page every second.

If you try to increase to 10 simultanous users you will see a median response time of ~5300ms. If this is a likely scenario, you will have to look into how to improve the performance of your app.

### Test advanced interactions with Locust and PlayWright

According to [locust-plugins](https://github.com/SvenskaSpel/locust-plugins) it should be possible to possible to combine Locust and PlayWright. I've tried. Unfortunately it does not work for me on Windows. You can check out the issue with code [here](https://github.com/SvenskaSpel/locust-plugins/issues/101#issuecomment-1367216919).
