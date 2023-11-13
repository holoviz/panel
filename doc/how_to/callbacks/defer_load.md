# Defer Bound Functions to Improve the User Experience

This guide addresses how to defer long running, bound and displayed functions with `defer_load`. You can use this to improve the user experience of your app.

If you need to defer and orchestrate multiple, dependent tasks then check out the [Defer Long Running Tasks Guide](load.md).

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

def some_long_running_task():
    time.sleep(5)
    return "# Wow. That took some time. Are you still here?"

pn.panel(some_long_running_task).servable()
```

![panel-longrunning-task-example](https://assets.holoviz.org/panel/gifs/long_running_task.gif)

Now lets learn how to defer long running tasks to after the application has loaded.

## Defer all Tasks

Its easy defer the execution of all bound and displayed functions with `pn.extension(..., defer_load=True)`.

```python
import time
import panel as pn

pn.extension(defer_load=True, loading_indicator=True, template="bootstrap")

def long_running_task():
    time.sleep(3)
    return "# I'm deferred and shown after load"

pn.Column("# I'm shown on load", long_running_task).servable()
```

![panel-defer-all-example](https://assets.holoviz.org/panel/gifs/defer_all_tasks.gif)

## Defer Specific Tasks

Its also easy to defer the execution of specific, bound and displayed functions with `pn.panel(..., defer_load=True)`.

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

![panel-defer-specific-example](https://assets.holoviz.org/panel/gifs/defer_specific_task.gif)

```{note}
If you [enable threading](../concurrency/threading.md) by setting `config.nthreads` or `--num-threads` on the commandline deferred callbacks will be executed concurrently on separate threads.
```
