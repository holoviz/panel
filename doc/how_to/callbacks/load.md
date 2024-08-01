# Defer Long Running Tasks to Improve the User Experience

This guide addresses how to defer and orchestrate long running background tasks with `pn.state.onload`. You can use this to improve the user experience of your app.

---

## Motivation

When a user opens your app, the app is *loaded* as follows

- the app file is executed
- the app template is sent to the user and rendered
- a web socket connection is opened to enable fast, bi-directional communication as your interact with the app.

Thus any long running code executed before the app is loaded will increase the the waiting time before your users see your apps template. **If the waiting time is more than 2-5 seconds your users might get confused and even leave the application behind**.

Here is an example of an app that takes +5 seconds to load.

```python
import time
import panel as pn

pn.extension(template="bootstrap")

layout = pn.pane.Markdown()

def some_long_running_task():
    time.sleep(5) # Some long running task
    layout.object = "# Wow. That took some time. Are you still here?"

some_long_running_task()

layout.servable()
```

![panel-longrunning-task-example](https://assets.holoviz.org/panel/gifs/long_load.gif)

Now lets learn how to defer long running tasks to after the application has loaded.

## Defer a Task

```python
import time
import panel as pn

pn.extension(template="bootstrap")

layout = pn.pane.Markdown("# Loading...")

def some_long_running_task():
    time.sleep(5) # Some long running task
    layout.object = "# Done"

pn.state.onload(some_long_running_task)

layout.servable()
```

![panel-onload-example](https://assets.holoviz.org/panel/gifs/onload_callback.gif)

Note that `pn.state.onload` accepts both *sync* and *async* functions and also accepts a `threaded` argument, which, when combined with [enabling `config.nthreads`](../concurrency/threading.md) will run the callbacks concurrently on separate threads.

This example could also be implemented using a *bound and displayed function*. We recommend using that method together with `defer_load` when possible. See the [Defer Bound and Displayed Functions Guide](defer_load.md).

## Defer and Orchestrate Dependent Tasks

Sometimes you have multiple tasks that depend on each other and you need to *orchestrate* them. To handle those scenarios you use `pn.state.onload` to defer background tasks and `pn.bind` to trigger *bound and displayed* functions when the the background tasks have finished.

Lets take an example where we

- load a shared dataset.
- display the dataset in a Table
- transform the dataset and display it as a plot

```python
import time
import panel as pn
import pandas as pd
import param
import hvplot.pandas

pn.extension(sizing_mode="stretch_width", template="bootstrap", theme="dark")

class AppState(param.Parameterized):
    data = param.DataFrame()

    def update(self):
        time.sleep(2)
        state.data = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 3, 2, 4]})

def loading_indicator(label):
    return pn.indicators.LoadingSpinner(
        value=True, name=label, size=25, align="center"
    )

def short_running_task():
    return "# I'm shown on load"

def table(data):
    if data is None:
        return loading_indicator("Loading data")

    return pn.pane.DataFrame(data)

def plot(data):
    if data is None:
        yield loading_indicator("Waiting for data")
        return

    yield loading_indicator("Transforming data")
    time.sleep(2)  # Some long running transformation
    yield data.hvplot()

state = AppState()
pn.state.onload(state.update)

pn.Column(
    short_running_task,
    pn.bind(table, data=state.param.data),
    pn.bind(plot, data=state.param.data),
).servable()
```

![panel-onload-dependent-tasks-example](https://assets.holoviz.org/panel/gifs/onload_dependent.gif)
