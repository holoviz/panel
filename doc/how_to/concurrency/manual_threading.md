# Set Up Manual Threading

Enabling threading in Panel, as demonstrated in the [automatic threading guide](threading), provides a simple method to achieve concurrency. However, there are situations where greater control is necessary.

Below, we will demonstrate how to safely implement threads either per session or globally across multiple sessions.

## Session Thread

This section illustrates how to use a `Thread` to process tasks within a queue, with one thread initiated per session to handle tasks individually per session.

We simulate task processing using `time.sleep`, but this could represent any long-running computation.

```python
import datetime
import threading
import time

from typing import Callable

import param

import panel as pn

pn.extension()

class SessionTaskRunner(pn.viewable.Viewer):
    value = param.Parameter(
        doc="The last result or exception", label="Last Result", constant=True
    )

    tasks: int = param.Integer(doc="Number of tasks in the queue", constant=True)
    status: str = param.String(
        default="The queue is empty", doc="Status message", constant=True
    )

    worker: Callable = param.Callable(
        allow_None=False, doc="Function that processes the task"
    )

    def __init__(self, **params):
        super().__init__(**params)
        self._queue = []
        self._stop_thread = False
        self._event = threading.Event()
        self._thread = threading.Thread(target=self._task_runner, daemon=True)
        self._thread.start()
        pn.state.on_session_destroyed(self._session_destroyed)

    def _log(self, message):
        print(f"{id(self)} - {message}")

    def _task_runner(self):
        while not self._stop_thread:
            while self._queue:
                with param.edit_constant(self):
                    self.status = f"Processing: {len(self._queue)} items left."
                self._log(self.status)
                task = self._queue.pop(0)
                try:
                    result = self.worker(task)
                    with param.edit_constant(self):
                        self.value = result
                except Exception as ex:
                    self.value = ex

                with param.edit_constant(self):
                    self.tasks = len(self._queue)
                    self.status = self.param.status.default

            self._event.clear()
            if not self._queue and not self._stop_thread:
                self._log("Waiting for a task")
                self._event.wait()

        self._log("Finished Task Runner")

    def _stop_thread_func(self):
        self._log(f"{id(self)} - Stopping Task Runner")
        self._stop_thread = True
        self._event.set()

    def _session_destroyed(self, session_context):
        self._stop_thread_func()

    def __del__(self):
        self._stop_thread_func()

    def __panel__(self):
        return pn.Column(
            f"## Session TaskRunner {id(self)}",
            pn.pane.Str(self.param.status),
            pn.pane.Str(pn.rx("Last Result: {value}").format(value=self.param.value)),
        )

    def append(self, task):
        """Appends a task to the queue"""
        self._queue.append(task)
        with param.edit_constant(self):
            self.tasks = len(self._queue)
        self._event.set()

```

We will now create a task runner and a callback that queues new tasks for processing when a button is clicked:

```python
def example_worker(task):
    time.sleep(1)
    return datetime.datetime.now()

task_runner = SessionTaskRunner(worker=example_worker)

def add_task(event):
    task_runner.append("task")

button = pn.widgets.Button(name="Add Task", on_click=add_task, button_type="primary")

pn.Column(button, task_runner).servable()
```

The application should look like:

<video muted controls loop poster="../../_static/images/session-task-runner.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/how_to/concurrency/session-task-runner.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

Since processing occurs on a separate thread, the application remains responsive to further user interactions, such as queuing new tasks.

:::{note}
To use threading efficiently:

- We terminate the thread upon session destruction to prevent it from consuming resources indefinitely.
- We use daemon threads (`daemon=True`) to allow the server to be stopped using CTRL+C.
- We employ the `Event.wait` method for efficient task-waiting, which is more resource-efficient compared to repeatedly sleeping and checking for new tasks using `time.sleep`.

:::

## Global Thread

When we need to share data periodically across all sessions, it is often inefficient to fetch and process this data separately for each session.

Instead, we can utilize a single thread. When initiating global threads, it's crucial to avoid starting them multiple times, especially in sessions or modules subject to the `--dev` flag. To circumvent this issue, we can globally share a worker or thread through the Panel cache (`pn.state.cache`).

Let's create a `GlobalTaskRunner` that accepts a function (`worker`) and executes it repeatedly, pausing for `sleep` seconds between each execution.

This worker can be used to ingest data from a database, the web, or any server resource.

```python
import datetime
import threading
import time

from typing import Callable

import param

import panel as pn

pn.extension()

class GlobalTaskRunner(pn.viewable.Viewer):
    """The GlobalTaskRunner creates a singleton instance for each key."""
    value = param.Parameter(doc="The most recent result", label="Last Result", constant=True)
    exception: Exception = param.ClassSelector(
        class_=Exception,
        allow_None=True,
        doc="The most recent exception, if any",
        label="Last Exception",
        constant=True,
    )
    worker: Callable = param.Callable(
        allow_None=False, doc="Function that generates a result"
    )
    seconds: float = param.Number(
        default=1.0, doc="Interval between worker calls", bounds=(0.001, None)
    )
    key: str = param.String(allow_None=False, constant=True)

    _global_task_runner_key = "__global_task_runners__"

    def __init__(self, key: str, **params):
        super().__init__(key=key, **params)

        self._stop_thread = False
        self._thread = threading.Thread(target=self._task_runner, daemon=True)
        self._thread.start()
        self._log("Created")

    def __new__(cls, key, **kwargs):
        task_runners = pn.state.cache[cls._global_task_runner_key] = pn.state.cache.get(
            cls._global_task_runner_key, {}
        )
        task_runner = task_runners.get(key, None)

        if not task_runner:
            task_runner = super(GlobalTaskRunner, cls).__new__(cls)
            task_runners[key] = task_runner

        return task_runner

    def _log(self, message):
        print(f"{id(self)} - {message}")

    def _task_runner(self):
        while not self._stop_thread:
            try:
                result = self.worker()
                with param.edit_constant(self):
                    self.value = result
                    self.exception = None
            except Exception as ex:
                with param.edit_constant(self):
                    self.exception = ex
            if not self._stop_thread:
                self._log("Sleeping")
                time.sleep(self.seconds)

        self._log("Task Runner Finished")

    def remove(self):
        """Securely stops and removes the GlobalThreadWorker."""
        self._log("Removing")
        self._stop_thread = True
        self._thread.join()

        cache = pn.state.cache.get(self._global_task_runner_key, {})
        if self.key in cache:
            del cache[self.key]
        self._log("Removed")

    @classmethod
    def remove_all(cls):
        """Securely stops and removes all GlobalThreadWorkers."""
        for gtw in list(pn.state.cache.get(cls._global_task_runner_key, {}).values()):
            gtw.remove()
        pn.state.cache[cls._global_task_runner_key] = {}

    def __panel__(self):
        return pn.Column(
            f"## Global TaskRunner {id(self)}",
            self.param.seconds,
            pn.pane.Str(pn.rx("Last Result: {value}").format(value=self.param.value)),
            pn.pane.Str(
                pn.rx("Last Exception: {value}").format(value=self.param.exception)
            ),
        )
```

Let's test this with a simple example worker that generates timestamps every 0.33 seconds.

```python
def example_worker():
    time.sleep(1)
    return datetime.datetime.now()

task_runner = GlobalTaskRunner(
    key="example-worker", worker=example_worker, seconds=0.33
)

results = []

@pn.depends(task_runner.param.value)
def result_view(value):
    results.append(value)
    return f"{len(results)} results produced during this session"

pn.Column(
    task_runner, result_view,
).servable()
```

The application should look like:

<video muted controls loop poster="../../_static/images/global-task-runner.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/how_to/concurrency/global-task-runner.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

:::{note}

For efficient use of global threading:

- We employ the *singleton* principle (`__new__`) to create only one instance and thread per key.
- We use daemon threads (`daemon=True`) to ensure the server can be halted using CTRL+C.

:::
