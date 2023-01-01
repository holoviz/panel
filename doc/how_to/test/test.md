# How to test Panel apps

Testing is key to developing robust and performant applications. You can test Panel data apps using Python and the test tools you know and love.

Before we get started, you should

```bash
pip install panel pytest pytest-benchmark locust-plugins pytest-playwright playwright
```

and install the browsers

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

## Test the backend with Pytest

Lets test

- The initial *state* of the App
- That the app *state* changes appropriately when the *Run* button is clicked.
- That the duration of the *run* is as expected.

Create the file `test_app.py` and add the code below.

```python
import pytest

from app import App

@pytest.fixture
def app():
    return App(sleep_delay=0.001, load_delay=0.001)

def test_constructor(app):
    """Tests default values of App"""
    # Then
    assert app.run == False
    assert app.status == "No runs yet"
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
    app.run_delay=0.3

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

## Test the frontend with pytest and PlayWright

Sometimes, for example when you create [custom components](https://panel.holoviz.org/user_guide/Custom_Components.html), it can be useful to test the frontend behaviour.

For testing the frontend we recommend the framework [Playwright](https://playwright.dev/) by Microsoft. Panel it self is tested by this framework.

### Create the conftest.py

The `conftest.py` file contains pytest fixtures. it will 

- provide us with an available `port`
- clean up the Panel server after each test.

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

### Test the app

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

Its relatively easy to create the test code because Playwright allows you to record the code as you navigate your live app. See the PlayWright [codegen](https://playwright.dev/python/docs/codegen) docs.

You can try it by starting the Panel server

```bash
panel serve app.py
```

and starting the PlayWright recorder

```bash
playwright codegen http://localhost:5006/app
```

![panel-playwright-recording.gif](https://user-images.githubusercontent.com/42288570/210163133-bf08e9cd-2599-4c7e-a017-ba447547f0e0.gif)

## Test the load

Load testing refers to testing the performance of the entire Panel application and the server(s) running it.

This kind of testing is really useful if you want to 

- develop fast and snappy apps and/ or
- develop apps that scale to many users

### Test the initial load with Locust

[Locust](https://locust.io/) can help you the the behaviour of users that loads (i.e. requests) your Panel app. Locust provides many performance related statistics and charts.

Create the file `locustfile.py` and add the code below.

```python
#locustfile.py
from locust import HttpUser, task

class RequestOnlyUser(HttpUser):
    @task
    def goto(self):
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

Open [http://localhost:8089](http://localhost:8089). Keep the default settings and click the *Start swarming* button. This should look like the below.

![panel-locust.gif](https://user-images.githubusercontent.com/42288570/209923009-521554d4-dcf8-49b3-8cca-c714037af901.gif)

The median response time (on my laptop) is ~530ms when one user requests the page every second.

If you try to increase to 10 simultanous users you will see a median response time of ~5300ms. If this is a likely scenario, you will have to look into how to improve the performance of your app.

According to [locust-plugins](https://github.com/SvenskaSpel/locust-plugins) it should also be possible to possible to combine Locust and PlayWright to test more advanced interactions. Unfortunately it does not work for me on Windows. You can check out the issue with code [here](https://github.com/SvenskaSpel/locust-plugins/issues/101#issuecomment-1367216919).

### Test advanced interactions with Panel and PlayWright

We can actually use Panel and PlayWright test make advanced load testing of a Panel app!

```python
# load_tester.py
from __future__ import annotations
import asyncio
import time
from typing import Dict, List, Type
import datetime
import pandas as pd
import panel as pn
import param
from playwright.async_api import Page, async_playwright
from pathlib import Path

from app import App

USERS = 10
USER_DELAY = 1
USER_REACTION_TIME = 0.5
USER_CLICKS = 10
TEST_RESULTS_PATH = Path("test_results")

from contextlib import contextmanager


class Logger(param.Parameterized):
    results: Dict = param.List(class_=dict)
    path: str = param.String("test_results")
    file: str = param.String("load_test.csv")
    archive: str = param.Boolean(True)

    def __init__(self, **params):
        super().__init__(**params)

        self.reset()

    @contextmanager
    def event(self, name: str, user: str, **kwargs):
        start = time.time()
        if not self._start:
            self._start = start
        yield
        stop = time.time()
        result = {
            "event": name,
            "user": user,
            "start": pd.to_datetime(start, unit="s"),
            "stop": pd.to_datetime(stop, unit="s"),
            "start_seconds": start - self._start,
            "stop_seconds": stop - self._start,
            "duration": stop - start,
            **kwargs,
        }
        self.results.append(result)
        self.save()

    @property
    def data(self) -> pd.DataFrame:
        return pd.DataFrame(self.results)

    def reset(self):
        self.results = []
        self._start = None

    def _save(self):
        path = Path(self.path)
        path.mkdir(parents=True, exist_ok=True)
        file = path / self.file
        self.data.to_csv(file, index=True)

    def save(self):
        self._save()
        if self.archive:
            path = Path(self.path)
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M")
            filename, extension = self.file.split(".")
            file = path/"archive"/f"{filename}_{timestamp}.{extension}"
            file.parent.mkdir(parents=True, exist_ok=True)
            self.data.to_csv(file, index=True)


class User(param.Parameterized):
    page: Page = param.ClassSelector(class_=Page, constant=True)
    host: str = param.String("http://localhost:5006")
    event: callable = param.Callable(default=print)
    reaction_time: float = param.Number(default=USER_REACTION_TIME)

    endpoint: str = param.String("/")

    @property
    def url(self):
        return self.host + self.endpoint

    async def _reaction(self):
        await asyncio.sleep(self.reaction_time)

    async def run(self):
        with self.event(name="load", user=self.name):
            await self.page.goto(self.url)
            await self.page.get_by_role("button", name="Run").wait_for()
        await self._reaction()

class LoadTest(pn.viewable.Viewer):
    host: str = param.String("http://localhost:5006")
    logger: Logger = param.ClassSelector(class_=Logger)
    headless: bool = param.Boolean()
    user_count: int = param.Integer(default=USERS)
    user_delay: float = param.Number(default=USER_DELAY)
    user: Type[User] = param.Selector(objects=[User])

    def __init__(self, user: Type[User]|None=None, users: List[Type[User]] | None=None, **params):
        if user and not users:
            users=[user]
        if users:
            self.param.user.objects=users
        if user:
            self.param.user.default=user
        if not self.param.user.default in self.param.user.objects and self.param.user.objects:
            self.param.user.default = self.param.user.objects[0]
        params["logger"]=params.get("logger", Logger())
        super().__init__(**params)

    async def _create_task(self, index, browser, **kwargs):
        await asyncio.sleep(delay=index*self.user_delay)
        page = await browser.new_page()
        await self.user(name=str(index), host=self.host, page=page, event=self.logger.event, **kwargs).run()
        await asyncio.sleep(USER_REACTION_TIME)
        await page.close()

    def _create_tasks(self, browser):
        return [self._create_task(index=index, browser=browser) for index in range(self.user_count)]


    async def run(self):
        self.logger.reset()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            await asyncio.sleep(0.2)
            # Then()
            tasks = self._create_tasks(browser=browser)
            await asyncio.gather(*tasks)
            await browser.close()
        self.logger.save()

class LoadAndClickUser(param.Parameterized):
    page: Page = param.ClassSelector(class_=Page, constant=True)
    host: str = param.String("http://localhost:5006")
    event: callable = param.Callable(default=print)
    reaction_time: float = param.Number(default=USER_REACTION_TIME)

    endpoint: str = param.String("/")

    @property
    def url(self):
        return self.host + self.endpoint

    async def _reaction(self):
        await asyncio.sleep(self.reaction_time)

    async def run(self):
        with self.event(name="load", user=self.name):
            await self.page.goto(self.url)
            await self.page.get_by_role("button", name="Run").wait_for()
        await self._reaction()

        for click_index in range(USER_CLICKS):
            with self.event(name="interact", user=self.name):
                await self.page.get_by_role("button", name="Run").first.click()
                await self.page.get_by_text(f"Finished run {click_index+1}").wait_for()
            await self._reaction()

async def test_component(port=6001):
    # When
    # Given
    component = App
    host = f"http://localhost:{port}"
    server = pn.serve(component, port=port, threaded=True, show=False)
    await asyncio.sleep(0.2)

    try:
        test = LoadTest(host=host, headless=False, user=LoadAndClickUser)
        await test.run()
    except Exception as ex:
        server.stop()
        raise Exception from ex
    finally:
        # Clean up
        server.stop()


if __name__ == "__main__":
    asyncio.run(test_component())
```

```python
# load_test_viewer.py
from __future__ import annotations
import pandas as pd
import hvplot.pandas
import holoviews as hv
from holoviews import opts
import panel as pn
import param
from bokeh.models import HoverTool


pn.extension(sizing_mode="stretch_width", template="fast")
hv.extension("bokeh")

def do_nothing():
    pass

class LoadTestViewer(pn.viewable.Viewer):
    max_load_duration = param.Number(2, bounds=(0.1, 5.0), step=0.1)
    max_interaction_duration = param.Number(1.0, bounds=(0.1, 5.0), step=0.1)
    aggregation = param.Selector(objects=["None", "Median", "Mean", "Min", "Max"])
    data = param.DataFrame()
    periodic_callback = param.Parameter()
    file = param.String("test_results/load_test.csv")

    def __init__(self, add_periodic_callback: bool=False, **params):
        super().__init__(**params)
        if not "data" in params:
            self.read()
        
        # self.data = self.clean(data=self.data)

        self._view = pn.Column(
            pn.Param(self, parameters=["max_load_duration", "max_interaction_duration"]),
            self.segment_plot,
            pn.widgets.RadioButtonGroup.from_param(self.param.aggregation),
            self.mean_duration_plot,
            self.active_users,
        )

        if not self.periodic_callback:
            self.periodic_callback = pn.state.add_periodic_callback(self.read, period=2000, start=add_periodic_callback)

    def __panel__(self):
        return self._view

    def read(self):
        try:
            self.data = pd.read_csv(self.file, parse_dates=["start", "stop"], dtype={"user": "str"}, index_col=0)
        except Exception as ex:
            print(ex)
            raise Exception() from ex

    @staticmethod
    def clean(data):
        data = data.copy(deep=True)
        data["start_seconds"]=(data["start"]-data["start"].min()).dt.total_seconds()
        data["stop_seconds"]=(data["stop"]-data["start"].min()).dt.total_seconds()

        return data

    @pn.depends("max_load_duration", "max_interaction_duration", "data")
    def segment_plot(self):
        data: pd.DataFrame = self.data[["user", "event", "start_seconds", "stop_seconds", "duration"]].copy()
        # sort indirectly by user, start_seconds
        min_start_by_user = data.groupby("user")["start_seconds"].min()
        data = data.join(min_start_by_user, on="user", rsuffix="_min")
        data = data.sort_values(by=["start_seconds_min", "start_seconds"])
        
        data["color"]="green"
        data.loc[(data["event"]=="load") & (data["duration"]>=self.max_load_duration),"color"]="red"
        data.loc[(data["event"]=="interact") & (data["duration"]>=self.max_interaction_duration),"color"]="red"
        plot = hv.Segments(data, [hv.Dimension('start_seconds', label='Time in seconds'), 
                         hv.Dimension('user', label='User'), 'stop_seconds', 'user'])
        hover = HoverTool(tooltips=[("event", "@event"), ("user", "@user"), ("start", "@start_seconds"), ("end", "@stop_seconds"), ("duration", "@duration")])
        plot.opts(color="color", line_width=20, tools=[hover], xlim=self._xlim)
        return plot

    @pn.depends("max_load_duration", "max_interaction_duration", "data")
    def mean_duration_plot(self):
        data = self.data.copy()
        data = data.sort_values("start_seconds")
        tmp = data.groupby(['event']).expanding().duration
        if self.aggregation=="Median":
            data["value"]=tmp.median().reset_index().set_index("level_1")["duration"]
        elif self.aggregation=="Mean":
            data["value"]=tmp.mean().reset_index().set_index("level_1")["duration"]
        elif self.aggregation=="Min":
            data["value"]=tmp.min().reset_index().set_index("level_1")["duration"]
        elif self.aggregation=="Max":
            data["value"]=tmp.max().reset_index().set_index("level_1")["duration"]
        else:
            data["value"]=data.duration
        data["color"]=data["event"].map({"load": "#0072B5", "interact": "#DF9F1F"})
        data=data.sort_values("start_seconds")
        
        plot = data.hvplot(x="start_seconds", y="value", by="event", xlabel="Time in seconds", ylabel="Duration in seconds", hover=False, color="color", ylim=(0,None), xlim=self._xlim, height=400).opts(legend_position='bottom') *\
            data.hvplot(x="start_seconds", y="value", by="event", xlabel="Time in seconds", ylabel="Duration in seconds", kind="scatter", hover=True, color="color")

        plot = plot * hv.HLine(self.max_load_duration).opts(color="red", line_width=1)
        plot = plot * hv.HLine(self.max_interaction_duration).opts(color="red", line_width=1)
        return plot

    @property
    def _xlim(self):
        return (self.data["start_seconds"].min(), self.data["stop_seconds"].max())

    @pn.depends("data")
    def active_users(self):
        data = self.data.copy()
        timestamps = sorted(set(data.start_seconds.unique()).union(set(data.stop_seconds.unique())))
        user_start = data.groupby("user")["start_seconds"].min()
        user_stop = data.groupby("user")["stop_seconds"].max()
        results = []
        for timestamp in timestamps:
            active_users = sum((user_start<=timestamp) & (user_stop>=timestamp))
            results.append({"start_seconds": timestamp, "active_users": active_users})
        data = pd.DataFrame(results)
        max_users = data["active_users"].max()
        return data.hvplot(x="start_seconds", y="active_users", xlabel="Time in seconds", ylabel="Active users", color="#0072B5", hover=False, yticks=list(range(0, max_users+1))) *\
        data.hvplot(x="start_seconds", y="active_users", xlabel="Time in seconds", ylabel="Active users", color="#0072B5", kind="scatter", ylim=(0,None), yticks=list(range(0, max_users+1)))

if __name__.startswith("bokeh"):
    app = LoadTestViewer(add_periodic_callback=True)
    pn.panel(app).servable()
```

Run

```bash
panel serve load_test_viewer.py
```

```bash
python load_tester.py
```

It should look something like

![panel-playwright-load-tester.gif](https://user-images.githubusercontent.com/42288570/210130957-92dee566-4fcf-4a02-a8ee-830af6297307.gif)