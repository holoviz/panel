# Test functionality and performance

This guide addresses how to use unit and performance testing on a Panel app with Pytest.

---

Testing is key to developing robust and performant applications. You can test Panel data apps using familiar Python testing tools.

[Pytest](https://docs.pytest.org/en/latest/) is the most common Python testing framework. We will use it below to write unit and performance tests. Before we get started, you should

```bash
pip install panel pytest pytest-benchmark
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

        button = pn.widgets.Button.from_param(self.param.run, sizing_mode="fixed")
        self._view = pn.Column(
            pn.Row(button, self._status_pane),
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
        self.runs += 1
        self.status = f"Finished run {self.runs} in {duration}sec"

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

Now serve the app via `panel serve app.py` and open [http://localhost:5006/app](http://localhost:5006/app) in your browser to see what it does.

## Create the unit tests

Let's test:

- The initial *state* of the App
- That the app *state* changes appropriately when the *Run* button is clicked.

Create the file `test_app.py` and add the code below.

:::{card} test_app.py

```{code-block} python

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
    app.param.trigger('run')
    # Then
    assert app.runs == 1
    assert app.status.startswith("Finished run 1 in")

def test_run_twice(app):
    """Tests behaviour when Run button is clicked twice"""
    # When
    app.param.trigger('run')
    app.param.trigger('run')
    # Then
    assert app.runs == 2
    assert app.status.startswith("Finished run 2 in")
```

:::

Let's run `pytest test_app.py`:

```bash
$ pytest test_app.py
=================================== test session starts
...
collected 3 items

test_app.py ...                                                                       [100%]

=============================== 3 passed
```

## Create a performance test

The performance of your data app is key to providing a good user experience. You can test the performance of functions and methods using [pytest-benchmark](https://github.com/ionelmc/pytest-benchmark).

Let's test that:

- the *duration* of the run is as expected.

Create the file `test_app_performance.py`:

:::{card} test_app_performance.py

```{code-block} python
# test_app_performance.py
import pytest
from app import App

@pytest.fixture
def app():
    return App(run_delay=0.001, load_delay=0.001)

def test_run_performance(app: App, benchmark):
    """Test the duration when the Run button is clicked"""
    app.run_delay=0.3

    def run():
        app.param.trigger('run')

    benchmark(run)
    assert benchmark.stats['min'] >= 0.3
    assert benchmark.stats['max'] < 0.4
```

:::

Run `pytest test_app_performance.py`.

```bash
$ pytest test_app_performance.py
============================================================================================================================= test session starts
...
collected 1 item

test_app_performance.py .                                                                                                                                                                                                                                                 [100%]

------------------------------------------------- benchmark: 1 tests ------------------------------------------------
Name (time in ms)             Min       Max      Mean  StdDev    Median     IQR  Outliers     OPS  Rounds  Iterations
---------------------------------------------------------------------------------------------------------------------
test_run_performance     307.6315  316.8270  312.2731  4.2335  314.1614  7.5190       3;0  3.2023       5           1
---------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
========================================================================================================================= 1 passed in 3.23s
```

Notice how we used the `benchmark` *fixture* of [pytest-benchmark](https://pytest-benchmark.readthedocs.io/en/latest/) to test the performance of the `run` event.

## Related Resources
