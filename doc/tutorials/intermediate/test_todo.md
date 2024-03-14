# Test Todo App

In the previous section we built a Todo app using the `Parameterized` class based approach. In this tutorial we will show how this makes you app easily testable in Python. This ensures you app will be extensible and maintainable in the long term.

## Run the tests

Copy the app code above into a file `app.py` and the test code into a file `test_app.py`.

:::{dropdown} Code: app.py

```python
"""An app to manage tasks"""
from typing import List

import param

import panel as pn

pn.extension(sizing_mode="stretch_width", design="material")

BUTTON_WIDTH = 125


class Task(pn.viewable.Viewer):
    """A model of a Task"""

    value: str = param.String(doc="A description of the task")
    completed: bool = param.Boolean(
        doc="If True the task has been completed. Otherwise not."
    )

    def __panel__(self):
        completed = pn.widgets.Checkbox.from_param(
            self.param.completed, name="", align="center", sizing_mode="fixed"
        )
        content = pn.pane.Markdown(object=self.param.value)
        return pn.Row(completed, content, sizing_mode="stretch_width")


class TaskList(param.Parameterized):
    """Provides methods to add and remove tasks as well as calculate summary statistics"""

    value: List[Task] = param.List(class_=Task, doc="A list of Tasks")

    total_tasks = param.Integer(doc="The number of Tasks")
    has_tasks = param.Boolean(doc="Whether or not the TaskList contains Tasks")

    completed_tasks = param.Integer(doc="The number of completed tasks")

    status = param.String(
        doc="A string explaining the number of completed tasks and total number of tasks."
    )

    def __init__(self, **params):
        self._task_watchers = {}

        super().__init__(**params)

        self._handle_completed_changed()

    def add_task(self, task: Task):
        """Adds a Task to the value list"""
        self.value = [*self.value, task]

    def remove_all_tasks(self):
        """Removes all tasks from the value list"""
        self._task_watchers = {}
        self.value = []

    def _handle_completed_changed(self, _=None):
        self.completed_tasks = sum(task.completed for task in self.value)

    @param.depends("value", watch=True, on_init=True)
    def _add_task_watchers(self):
        for task in self.value:
            if not task in self._task_watchers:
                self._task_watchers[task] = task.param.watch(
                    self._handle_completed_changed, "completed"
                )

    @param.depends("value", watch=True, on_init=True)
    def _handle_value_changed(self):
        self.total_tasks = len(self.value)
        self.has_tasks = self.total_tasks > 0

    @param.depends("total_tasks", "completed_tasks", watch=True, on_init=True)
    def _update_status(self):
        self.status = f"{self.completed_tasks} of {self.total_tasks} tasks completed"


class TaskInput(pn.viewable.Viewer):
    """A Widget that provides tasks as input"""

    value: Task = param.ClassSelector(class_=Task, doc="""The Task input by the user""")

    def _no_value(self, value):
        return not bool(value)

    def __panel__(self):
        text_input = pn.widgets.TextInput(
            name="Task", placeholder="Enter a task", sizing_mode="stretch_width"
        )
        text_input_has_value = pn.rx(self._no_value)(text_input.param.value_input)
        submit_task = pn.widgets.Button(
            name="Add",
            align="center",
            button_type="primary",
            width=BUTTON_WIDTH,
            sizing_mode="fixed",
            disabled=text_input_has_value,
        )

        @pn.depends(text_input, submit_task, watch=True)
        def clear_text_input(*_):
            if text_input.value:
                self.value = Task(value=text_input.value)
                text_input.value = text_input.value_input = ""

        return pn.Row(text_input, submit_task, sizing_mode="stretch_width")


class TaskRow(pn.viewable.Viewer):
    """Display a task in a Row together with a Remove button"""

    value: Task = param.ClassSelector(
        class_=Task, allow_None=True, doc="The Task to display"
    )

    remove: bool = param.Event(
        doc="The event is triggered when the user clicks the Remove Button"
    )

    def __panel__(self):
        remove_button = pn.widgets.Button.from_param(
            self.param.remove, width=BUTTON_WIDTH, icon="trash", sizing_mode="fixed"
        )
        return pn.Row(self.value, remove_button)


class TaskListEditor(pn.viewable.Viewer):
    """Component that enables a user to manage a list of tasks"""

    value: TaskList = param.ClassSelector(class_=TaskList)

    @param.depends("value.value")
    def _layout(self):
        tasks = self.value.value
        rows = [TaskRow(value=task) for task in tasks]
        for row in rows:

            def remove(_, task=row.value):
                self.value.value = [item for item in tasks if not item == task]

            pn.bind(remove, row.param.remove, watch=True)

        return pn.Column(*rows)

    def __panel__(self):
        task_input = TaskInput()
        pn.bind(self.value.add_task, task_input.param.value, watch=True)
        clear = pn.widgets.Button(
            name="Remove All",
            button_type="primary",
            button_style="outline",
            width=BUTTON_WIDTH,
            sizing_mode="fixed",
            visible=self.value.param.has_tasks,
            on_click=lambda e: self.value.remove_all_tasks(),
        )

        return pn.Column(
            "## WTG Task List",
            pn.pane.Markdown(self.value.param.status),
            task_input,
            self._layout,
            pn.Row(pn.Spacer(), clear),
            max_width=500,
        )


if pn.state.served:
    task_list = TaskList(
        value=[
            Task(value="Inspect the blades", completed=True),
            Task(value="Inspect the nacelle"),
            Task(value="Tighten the bolts"),
        ]
    )
    TaskListEditor(value=task_list).servable()
```

:::

:::{dropdown} Code: test_app.py

```python
"""Test of the Todo App components"""
from app import (
    Task,
    TaskInput,
    TaskList,
    TaskListEditor,
)


def test_create_task():
    """We can create a Task"""
    task = Task(value="Do this", completed=True)
    assert task.value == "Do this"
    assert task.completed
    assert task.__panel__()


def test_can_create_task_list_without_tasks():
    """We can create a Task list with Tasks"""
    task_list = TaskList()
    assert task_list.value == []
    assert not task_list.has_tasks
    assert task_list.total_tasks == 0
    assert task_list.status == "0 of 0 tasks completed"


def test_can_create_task_list_with_tasks():
    """We can create a Task list with Tasks"""
    tasks = [
        Task(value="Inspect the blades", completed=True),
        Task(value="Inspect the nacelle"),
        Task(value="Tighten the bolts"),
    ]

    task_list = TaskList(value=tasks)
    assert task_list.value == tasks
    assert task_list.has_tasks
    assert task_list.total_tasks == 3
    assert task_list.status == "1 of 3 tasks completed"


def test_can_add_new_task_to_task_list():
    """We can add a new task to the task list"""
    task_list = TaskList()
    task = Task(value="Inspect the nacelle")

    task_list.add_task(task)

    assert task_list.value == [task]
    assert task_list.has_tasks
    assert task_list.total_tasks == 1
    assert task_list.status == "0 of 1 tasks completed"

    task.completed = True
    assert task_list.status == "1 of 1 tasks completed"


def test_can_replace_tasks():
    """We can replace the list of tasks"""
    task_list = TaskList()
    task = Task(value="Inspect the nacelle")

    task_list.value = [task]

    assert task_list.value == [task]
    assert task_list.has_tasks
    assert task_list.total_tasks == 1
    assert task_list.status == "0 of 1 tasks completed"

    task.completed = True
    assert task_list.status == "1 of 1 tasks completed"


def test_create_task_input():
    """We can create a TaskInput widget"""
    task_input = TaskInput()
    assert not task_input.value


def test_enter_text_into_task_input():
    """When we enter text into a TaskInput a Task is created"""
    task_input = TaskInput()
    text_input, _ = task_input.__panel__()

    text_input.value = "some value"
    assert task_input.value
    assert task_input.value.value == "some value"
    assert text_input.value == ""


def test_can_create_task_list_editor():
    """We can create a TaskListEditor"""
    tasks = [
        Task(value="Inspect the blades", completed=True),
        Task(value="Inspect the nacelle"),
        Task(value="Tighten the bolts"),
    ]

    task_list = TaskList(value=tasks)
    task_list_editor = TaskListEditor(value=task_list)
    assert task_list_editor.__panel__()
```

:::

Run the tests with `pytest test_app.py`. It should look like

```bash
$ pytest test_app.py
============================================ test session starts =============================================
platform linux -- Python 3.10.13, pytest-8.1.1, pluggy-1.4.0 -- /home/jovyan/panel/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/jovyan/panel
configfile: pyproject.toml
plugins: dash-2.14.2, anyio-3.7.1
collected 8 items

test_app.py::test_create_task PASSED                                                                   [ 12%]
test_app.py::test_can_create_task_list_without_tasks PASSED                                            [ 25%]
test_app.py::test_can_create_task_list_with_tasks PASSED                                               [ 37%]
test_app.py::test_can_add_new_task_to_task_list PASSED                                                 [ 50%]
test_app.py::test_can_replace_tasks PASSED                                                             [ 62%]
test_app.py::test_create_task_input PASSED                                                             [ 75%]
test_app.py::test_enter_text_into_task_input PASSED                                                    [ 87%]
test_app.py::test_can_create_task_list_editor PASSED                                                   [100%]

============================================== warnings summary ==============================================
...
======================================= 8 passed, 2 warnings in 1.43s ========================================
```

## Explanation

### `test_create_task`

```python
def test_create_task():
    """We can create a Task"""
    task = Task(value="Do this", completed=True)
    assert task.value == "Do this"
    assert task.completed
    assert task.__panel__()
```

This test verifies if we can create a `Task` instance successfully. It initializes a task with a description "Do this" and marks it as completed. Then, it checks if the task's attributes are correctly set and if the `__panel__()` method returns a valid Panel component.

### `test_can_create_task_list_without_tasks`

```python
def test_can_create_task_list_without_tasks():
    """We can create a Task list without Tasks"""
    task_list = TaskList()
    assert task_list.value == []
    assert not task_list.has_tasks
    assert task_list.total_tasks == 0
    assert task_list.status == "0 of 0 tasks completed"
```

This test validates the behavior of creating a `TaskList` instance without any tasks. It checks if the task list initializes with an empty list, and if the status attributes are correctly set reflecting no tasks.

### `test_can_create_task_list_with_tasks`

```python
def test_can_create_task_list_with_tasks():
    """We can create a Task list with Tasks"""
    tasks = [
        Task(value="Inspect the blades", completed=True),
        Task(value="Inspect the nacelle"),
        Task(value="Tighten the bolts"),
    ]

    task_list = TaskList(value=tasks)
    assert task_list.value == tasks
    assert task_list.has_tasks
    assert task_list.total_tasks == 3
    assert task_list.status == "1 of 3 tasks completed"
```

This test ensures that we can create a `TaskList` instance with a predefined list of tasks. It checks if the task list initializes with the provided tasks, calculates the total number of tasks accurately, and sets the status attribute accordingly.

### `test_can_add_new_task_to_task_list`

```python
def test_can_add_new_task_to_task_list():
    """We can add a new task to the task list"""
    task_list = TaskList()
    task = Task(value="Inspect the nacelle")

    task_list.add_task(task)

    assert task_list.value == [task]
    assert task_list.has_tasks
    assert task_list.total_tasks == 1
    assert task_list.status == "0 of 1 tasks completed"

    task.completed = True
    assert task_list.status == "1 of 1 tasks completed"
```

This test verifies if we can add a new task to the `TaskList` instance successfully. It adds a new task to the task list, checks if the task list reflects the addition, and updates the status attribute accordingly when the task is marked as completed.

### `test_can_replace_tasks`

```python
def test_can_replace_tasks():
    """We can replace the list of tasks"""
    task_list = TaskList()
    task = Task(value="Inspect the nacelle")

    task_list.value = [task]

    assert task_list.value == [task]
    assert task_list.has_tasks
    assert task_list.total_tasks == 1
    assert task_list.status == "0 of 1 tasks completed"

    task.completed = True
    assert task_list.status == "1 of 1 tasks completed"
```

This test validates if we can replace the list of tasks in the `TaskList` instance successfully. It replaces the task list with a new list containing a single task, checks if the task list reflects the replacement, and updates the status attribute accordingly when the task is marked as completed.

### `test_create_task_input`

```python
def test_create_task_input():
    """We can create a TaskInput widget"""
    task_input = TaskInput()
    assert not task_input.value
```

This test ensures that we can create a `TaskInput` widget successfully. It checks if the initial value of the widget is `None`.

### `test_enter_text_into_task_input`

```python
def test_enter_text_into_task_input():
    """When we enter text into a TaskInput a Task is created"""
    task_input = TaskInput()
    text_input, _ = task_input.__panel__()

    text_input.value = "some value"
    assert task_input.value
    assert task_input.value.value == "some value"
    assert text_input.value == ""
```

This test verifies the behavior of entering text into the `TaskInput` widget. It sets a text value into the input field, checks if a task is created from the entered text, and if the task value matches the entered text. Additionally, it ensures that the input field is cleared after setting the value.

### `test_can_create_task_list_editor`

```python
def test_can_create_task_list_editor():
    """We can create a TaskListEditor"""
    tasks = [
        Task(value="Inspect the blades", completed=True),
        Task(value="Inspect the nacelle"),
        Task(value="Tighten the bolts"),
    ]

    task_list = TaskList(value=tasks)
    task_list_editor = TaskListEditor(value=task_list)
    assert task_list_editor.__panel__()
```

This test validates if we can create a `TaskListEditor` successfully. It initializes a task list with predefined tasks and creates a task list editor from it, ensuring that the editor is correctly instantiated.
