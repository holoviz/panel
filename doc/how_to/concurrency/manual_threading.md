# Set Up Manual Threading

Enabling threading in Panel, as demonstrated in the [automatic threading guide](threading.md), provides a simple method to achieve concurrency. However, there are situations where greater control is necessary.

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
            f"## TaskRunner {id(self)}",
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

Since processing occurs on a separate thread, the application remains responsive to further user interactions, such as queuing new tasks.

:::{note}
To use threading efficiently:

- We terminate the thread upon session destruction to prevent it from consuming resources indefinitely.
- We use daemon threads (`daemon=True`) to allow the server to be stopped using CTRL+C.
- We employ the `Event.wait` method for efficient task-waiting, which is more resource-efficient compared to repeatedly sleeping and checking for new tasks using `time.sleep`.

:::
