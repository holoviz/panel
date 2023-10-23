# Test operating capacity

This guide addresses how to test performance by simulating multiple users accessing an app concurrently.

---

*Load testing* means testing the performance of the entire Panel application and the server(s) running it.

This kind of testing is really useful if you want to

- develop fast and snappy applications and/ or
- develop applications that scale to many users

Before you get started ensure you have installed the required dependencies:

```bash
pip install panel pytest locust pytest-playwright pytest-asyncio loadwright
```

and ensure `playwright` sets up the browsers it will use to display the applications:

```bash
playwright install
```

## Create the app

Lets create a simple data app for testing. The app sleeps 0.5 seconds (default) when loaded and when the button is clicked.

![app.py](https://assets.holoviz.org/panel/gifs/pytest.gif)

Create the file `app.py` and add the code below:

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

Serve the app via `panel serve app.py` and open [http://localhost:5006/app](http://localhost:5006/app) in your browser.

## Create a conftest.py

The `conftest.py` file should be placed alongside your tests and will be loaded automatically by pytest. It is often used to declare [fixtures](https://docs.pytest.org/en/6.2.x/fixture.html) that allow you declare reusable components. It will:

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

## Test the initial load with Locust

[Locust](https://locust.io/) can help you test the behaviour of users that load (i.e. request) your Panel app. Locust provides many useful performance related statistics and charts.

Create the file `locustfile.py` and add the code below.

:::{card} locustfile.py

```{code-block} python

from locust import HttpUser, task

class RequestOnlyUser(HttpUser):
    @task
    def goto(self):
        self.client.get("/app")
```

:::

Start the Panel server:

```bash
panel serve app.py
```

Start the Locust server

```bash
locust --host http://localhost:5006
```

Open [http://localhost:8089](http://localhost:8089). Keep the default settings and click the *Start swarming* button. This should look like the below:

![panel-locust.gif](https://assets.holoviz.org/panel/gifs/locust.gif)

The median response time is ~530ms when one user requests the page every second. If you try to increase to 10 simultaneous users you will see a median response time of ~5300ms. If this is a likely scenario, you will have to look into how to improve the performance of your app.

## Test advanced interactions with Loadwright

[Loadwright](https://github.com/awesome-panel/loadwright) is a young load testing framework built on top of Playwright and Panel.

Lets replicate a user that:

- Opens the app in the browser
- Clicks the *Run* button `n_clicks` times.

Create the file `test_loadwright.py` and add the code below:

:::{card} test_loadwright.py

```{code-block} python

import param
import pytest

from loadwright import LoadTestRunner, LoadTestViewer, User

import panel as pn

from app import App

HEADLESS = False

class LoadAndClickUser(User):
    """A custom User that loads a page and clicks a button n_clicks times"""

    n_clicks = param.Integer(
        default=1, bounds=(0, None), doc="The number of times to click the button"
    )

    async def run(self):
        with self.event(name="load", user=self.name):
            await self.page.goto(self.url)
            await self.page.get_by_role("button", name="Run").wait_for()
        await self.sleep()

        for click_index in range(self.n_clicks):
            with self.event(name="interact", user=self.name):
                await self.page.get_by_role("button", name="Run").first.click()
                await self.page.get_by_text(f"Finished run {click_index+1}").wait_for()
            await self.sleep()

@pytest.mark.asyncio
async def test_component_2(port=6001):
    """We can run the LoadTestRunner with 5 users each clicking 5 times"""
    async with LoadTestRunner.serve(App, port=port) as host:
        runner = LoadTestRunner(host=host, headless=HEADLESS, user=LoadAndClickUser(n_clicks=5), n_users=5)
        await runner.run()
        # You can access the data of the run via runner.logger.data
        assert runner.logger.data.duration.mean()<=10

if pn.state.served:
    import panel as pn
    pn.extension(sizing_mode="stretch_width")
    viewer = LoadTestViewer(data="test_results/loadwright.csv")
    pn.template.FastListTemplate(
        site="LoadWright",
        title="Load Testing with Playwright and Panel",
        main=[viewer]
    ).servable()
```

:::

Run the tests with pytest

```bash
pytest test_loadwright.py
```

View the results with Panel

```bash
$ panel serve test_loadwright.py
...
2023-01-01 15:53:03,396 Bokeh app running at: http://localhost:5006/test_loadwright
```

![Loadwright Demo](https://assets.holoviz.org/panel/gifs/loadwright.gif).

You will find an *archive* of *test results* in the `tests_results/archive` folder.

## Related Resources
