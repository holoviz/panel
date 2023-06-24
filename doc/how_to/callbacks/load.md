# Defer Long Running Tasks to Improve the User Experience

This guide addresses how to defer long running tasks to after the application has loaded.
You can use this to improve the user experience of your app.

---

## Motivation

When you `panel serve` your app, the app is *loaded* as follows

- the app file is read and executed
- the apps template is populated, sent to the user and rendered
- a web socket connection is created between the server and the users client to handle additional communication as you interact with the app.

Thus any long running code executed when the app file is first executed will increase the the waiting time before your users see any signs that your app is working. **If the waiting time is more than 2-5 seconds your users might get confused and even leave the application behind**.

Here is an example of an app that takes +5 seconds to load.

```python
import time
import panel as pn

pn.extension(template="bootstrap")


def some_long_running_task():
    time.sleep(5)
    return "# Wow. That took some time. Are you still here?"


pn.panel(some_long_running_task).servable()
```

![panel-longrunning-task-example](https://user-images.githubusercontent.com/42288570/245752515-1329b4c3-da45-41e7-b3b5-b1b4f09eecd4.gif)

Now lets learn how to defer long running tasks to after the application has loaded.

## Defer all Tasks

Its easy defer the execution of all displayed tasks with `pn.config.defer_load=True` or
`pn.extension(defer_load=True)`. Lets take an example.

```python
import time
import panel as pn

pn.extension(defer_load=True, loading_indicator=True, template="bootstrap")

def long_running_task():
    time.sleep(3)
    return "# I'm deferred and shown after load"

pn.Column("# I'm shown on load", long_running_task).servable()
```

![panel-defer-all-example](https://user-images.githubusercontent.com/42288570/245752511-b2970c4c-7144-4b1a-af36-4c90b1873de6.gif)

## Defer Specific Tasks

Its also easy to defer the execution of selected, displayed tasks with `pn.panel(..., defer_load=True)`.

```python
import time
import panel as pn

pn.extension(loading_indicator=True, template="bootstrap")


def short_running_task():
    return "# I'm shown on load"


def long_running_task():
    time.sleep(3)
    return "# I'm deferred and shown after load"


pn.Column(
    short_running_task,
    pn.panel(long_running_task, defer_load=True, min_height=50, min_width=200),
).servable()
```

![panel-defer-specific-example](https://user-images.githubusercontent.com/42288570/245752506-9ac676e9-65b2-4d9d-a01a-ce01a12dfda4.gif)

## Defer Tasks That are not Displayed

So far the tasks have been producing and returning viewable objects to be displayed in a your app. Sometimes that is not what you want. Sometimes you want to load or pre-compute one or more parameter values, send a message somewhere or similar.

For those use cases you can use `pn.state.onload` to run one or more tasks when the application has loaded.

```python
import time
import panel as pn
import pandas as pd
import param

pn.extension(loading_indicator=True, template="bootstrap")

class AppState(param.Parameterized):
    data = param.DataFrame()

def short_running_task():
    return "# I'm shown on load"

state = AppState()

def update():
    time.sleep(2)
    state.data = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 3, 2, 4]})

pn.state.onload(update)

pn.Column(
    short_running_task,
    pn.pane.DataFrame(state.param.data),
).servable()
```

![panel-defer-onload-example](https://user-images.githubusercontent.com/42288570/245752503-a8042242-503e-4ba3-ad24-1f1a16aac058.gif)

## Defer and Orchestrate Dependent Tasks

Sometimes you have multiple tasks that depend on each other and you need to *orchestrate* them. To handle those scenarios you can combine what you have learned so far with `pn.bind` and/ or `pn.depends`.

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

def loading_indicator():
    return pn.indicators.LoadingSpinner(value=True, height=25, width=25, align="center")

def short_running_task():
    return "# I'm shown on load"

def table(data):
    if data is None:
        return pn.Row(loading_indicator(), "Loading data")

    return pn.pane.DataFrame(data)

def plot(data):
    if data is None:
        yield pn.Row(loading_indicator(), "Waiting for data")
        return

    yield pn.Row(loading_indicator(), "Transforming data")
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

![panel-defer-dependent-tasks-example](https://user-images.githubusercontent.com/42288570/245752488-b2963489-bdff-4323-b801-03a763992af9.gif)

## Tips and Tricks

You can

- use caching to avoid rerunning expensive tasks
- use periodic callbacks or async generator functions to update the `data` and rerun the tasks on a periodic schedule.
- schedule `async` tasks with `pn.panel`, `pn.state.onload`, `pn.bind` and `pn.depends` to improve the user experience further.
