# Testing the Todo App

In the previous section, we constructed a Todo app using the `Parameterized` class-based approach. Now, we'll delve into how this approach enables easy testing of your app in Python. Ensuring your app's testability guarantees its extensibility and maintainability over time.

We firmly believe that the simplicity and accessibility of testing Panel components underscore a truly invaluable facet of Panel.

<iframe src="https://panel-org-build-todo-app.hf.space" frameborder="0" style="width: 100%;height:500px"></iframe>

## Running the Tests

First, copy the app code below into a file named `app.py`, and the test code into a file named `test_app.py`.

:::{dropdown} Code: app.py

```python
"""An app to manage tasks"""
import param
import panel as pn

BUTTON_WIDTH = 125

pn.extension(sizing_mode="stretch_width")

class Task(pn.viewable.Viewer):
    """A model of a Task"""

    value: str = param.String(doc="A description of the task")
    completed: bool = param.Boolean(
        doc="If True the task has been completed. Otherwise not."
    )

    def __panel__(self):
        completed = pn.ui.Checkbox.from_param(
            self.param.completed, label="", align="center", sizing_mode="fixed"
        )
        content = pn.ui.Markdown(object=self.param.value)
        return pn.ui.Row(completed, content, sizing_mode="stretch_width")


class TaskList(param.Parameterized):
    """Provides methods to add and remove tasks as well as calculate summary statistics"""

    value: list[Task] = param.List(item_type=Task, doc="A list of Tasks")

    total_tasks = param.Integer(doc="The number of Tasks")

    has_tasks = param.Boolean(doc="Whether or not the TaskList contains Tasks")

    completed_tasks = param.Integer(doc="The number of completed tasks")

    status = param.String(
        doc="A string explaining the number of completed tasks and total number of tasks."
    )

    def __init__(self, **params):
        self._task_watchers = {}

        super().__init__(**params)

    def add_task(self, task: Task):
        """Adds a Task to the value list"""
        self.value = [*self.value, task]

    def remove_task(self, task: Task):
        """Removes a Task from the value list"""
        self.value = [item for item in self.value if item is not task]

    def remove_all_tasks(self):
        """Removes all tasks from the value list"""
        self.value = []

    def _handle_completed_changed(self, _=None):
        self.completed_tasks = sum(task.completed for task in self.value)

    @param.depends("value", watch=True, on_init=True)
    def _add_task_watchers(self):
        for task in list(self._task_watchers):
            if task not in self.value:
                task.param.unwatch(self._task_watchers.pop(task))
        for task in self.value:
            if task not in self._task_watchers:
                self._task_watchers[task] = task.param.watch(
                    self._handle_completed_changed, "completed"
                )

    @param.depends("value", watch=True, on_init=True)
    def _handle_value_changed(self):
        self.param.update(
            total_tasks=len(self.value),
            has_tasks=len(self.value) > 0,
            completed_tasks=sum(task.completed for task in self.value),
        )

    @param.depends("total_tasks", "completed_tasks", watch=True, on_init=True)
    def _update_status(self):
        self.status = f"{self.completed_tasks} of {self.total_tasks} tasks completed"


class TaskInput(pn.viewable.Viewer):
    """A Widget that provides tasks as input"""

    value: Task = param.ClassSelector(class_=Task, doc="""The Task input by the user""")

    def __init__(self, **params):
        super().__init__(**params)
        self.text_input = pn.ui.TextInput(
            label="Task", placeholder="Enter a task", sizing_mode="stretch_width"
        )
        self.submit_task = pn.ui.Button(
            label="Add",
            align="center",
            color="primary",
            width=BUTTON_WIDTH,
            sizing_mode="fixed",
            disabled=self.text_input.param.value_input.rx.not_(),
            on_click=self._submit,
        )
        pn.bind(self._submit, self.text_input, watch=True)
        self._layout = pn.ui.Row(self.text_input, self.submit_task, sizing_mode="stretch_width")

    def _submit(self, *_):
        if self.text_input.value_input:
            self.value = Task(value=self.text_input.value_input)
            self.text_input.value = self.text_input.value_input = ""

    def __panel__(self):
        return self._layout


class TaskRow(pn.viewable.Viewer):
    """Display a task in a Row together with a Remove button"""

    value: Task = param.ClassSelector(
        class_=Task, allow_None=True, doc="The Task to display"
    )

    remove: bool = param.Event(
        doc="The event is triggered when the user clicks the Remove Button"
    )

    def __init__(self, **params):
        super().__init__(**params)
        self.remove_button = pn.ui.Button.from_param(
            self.param.remove, width=BUTTON_WIDTH, icon="delete", sizing_mode="fixed"
        )
        self._layout = pn.ui.Row(self.value, self.remove_button)

    def __panel__(self):
        return self._layout


class TaskListEditor(pn.viewable.Viewer):
    """Component that enables a user to manage a list of tasks"""

    value: TaskList = param.ClassSelector(class_=TaskList)

    def __init__(self, **params):
        super().__init__(**params)
        self._task_rows = {}
        self.task_input = TaskInput()
        self.task_column = pn.ui.Column()
        self.clear_button = pn.ui.Button(
            label="Remove All",
            color="primary",
            variant="outlined",
            width=BUTTON_WIDTH,
            sizing_mode="fixed",
            visible=self.value.param.has_tasks,
            on_click=lambda e: self.value.remove_all_tasks(),
        )
        pn.bind(self.value.add_task, self.task_input.param.value, watch=True)
        self._layout = pn.ui.Column(
            "## WTG Task List",
            pn.ui.Markdown(self.value.param.status),
            self.task_input,
            self.task_column,
            pn.ui.Row(pn.ui.Spacer(), self.clear_button),
            max_width=500,
        )
        self._update_task_rows()

    @param.depends("value.value", watch=True)
    def _update_task_rows(self):
        task_rows = {}
        for task in self.value.value:
            if task in self._task_rows:
                task_rows[task] = self._task_rows[task]
                continue
            row = TaskRow(value=task)

            def remove(_, task=task):
                self.value.remove_task(task)

            pn.bind(remove, row.param.remove, watch=True)
            task_rows[task] = row
        self._task_rows = task_rows
        self.task_column.objects = list(task_rows.values())

    def __panel__(self):
        return self._layout

if pn.state.served:
    task_list = TaskList(
        value=[
            Task(value="Inspect the blades", completed=True),
            Task(value="Inspect the nacelle"),
            Task(value="Tighten the bolts"),
        ]
    )
    pn.ui.Page(title="Todo App", main=[TaskListEditor(value=task_list)]).servable()
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
    """We can create a Task list without Tasks"""
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


def test_can_remove_tasks():
    """We can remove a single task or all tasks from the task list"""
    completed_task = Task(value="Inspect the blades", completed=True)
    task = Task(value="Inspect the nacelle")
    task_list = TaskList(value=[completed_task, task])

    task_list.remove_task(completed_task)

    assert task_list.value == [task]
    assert task_list.status == "0 of 1 tasks completed"

    completed_task.completed = False
    assert task_list.status == "0 of 1 tasks completed"

    task_list.remove_all_tasks()

    assert task_list.value == []
    assert not task_list.has_tasks
    assert task_list.status == "0 of 0 tasks completed"


def test_create_task_input():
    """We can create a TaskInput widget"""
    task_input = TaskInput()
    assert not task_input.value
    assert task_input.submit_task.disabled


def test_enter_text_into_task_input():
    """When we enter text into a TaskInput a Task is created"""
    task_input = TaskInput()

    task_input.text_input.value_input = "some value"
    assert not task_input.submit_task.disabled

    task_input.text_input.value = "some value"
    assert task_input.value
    assert task_input.value.value == "some value"
    assert task_input.text_input.value == ""
    assert task_input.submit_task.disabled


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
    assert len(task_list_editor.task_column) == 3


def test_task_list_editor_can_add_and_remove_tasks():
    """We can add and remove tasks using the TaskListEditor"""
    task_list = TaskList(value=[Task(value="Inspect the blades", completed=True)])
    task_list_editor = TaskListEditor(value=task_list)

    task_list_editor.task_input.text_input.value_input = "Tighten the bolts"
    task_list_editor.task_input.submit_task.clicks += 1

    assert [task.value for task in task_list.value] == ["Inspect the blades", "Tighten the bolts"]
    assert len(task_list_editor.task_column) == 2
    assert task_list.status == "1 of 2 tasks completed"

    task_list_editor.clear_button.clicks += 1

    assert task_list.value == []
    assert len(task_list_editor.task_column) == 0
    assert not task_list_editor.clear_button.visible
    assert task_list.status == "0 of 0 tasks completed"
```

:::

Run the tests with `pytest test_app.py`. It should look like this:

```bash
$ pytest test_app.py
============================================ test session starts =============================================
platform linux -- Python 3.10.13, pytest-8.1.1, pluggy-1.4.0 -- /home/jovyan/panel/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/jovyan/panel
configfile: pyproject.toml
plugins: dash-2.14.2, anyio-3.7.1
collected 10 items

test_app.py::test_create_task PASSED                                                             [ 10%]
test_app.py::test_can_create_task_list_without_tasks PASSED                                      [ 20%]
test_app.py::test_can_create_task_list_with_tasks PASSED                                         [ 30%]
test_app.py::test_can_add_new_task_to_task_list PASSED                                           [ 40%]
test_app.py::test_can_replace_tasks PASSED                                                       [ 50%]
test_app.py::test_can_remove_tasks PASSED                                                        [ 60%]
test_app.py::test_create_task_input PASSED                                                       [ 70%]
test_app.py::test_enter_text_into_task_input PASSED                                              [ 80%]
test_app.py::test_can_create_task_list_editor PASSED                                             [ 90%]
test_app.py::test_task_list_editor_can_add_and_remove_tasks PASSED                               [100%]

============================================== warnings summary ==============================================
...
======================================= 10 passed, 2 warnings in 1.43s ========================================
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

This test ensures that a `Task` instance can be created successfully. It initializes a task with the description "Do this" and marks it as completed. Then, it checks if the task's attributes are correctly set and if the `__panel__()` method returns a valid Panel component.

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

This test validates the behavior of creating a `TaskList` instance without any tasks. It checks if the task list initializes with an empty list and if the status attributes are correctly set to reflect no tasks.

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

### `test_can_remove_tasks`

```python
def test_can_remove_tasks():
    """We can remove a single task or all tasks from the task list"""
    completed_task = Task(value="Inspect the blades", completed=True)
    task = Task(value="Inspect the nacelle")
    task_list = TaskList(value=[completed_task, task])

    task_list.remove_task(completed_task)

    assert task_list.value == [task]
    assert task_list.status == "0 of 1 tasks completed"

    completed_task.completed = False
    assert task_list.status == "0 of 1 tasks completed"

    task_list.remove_all_tasks()

    assert task_list.value == []
    assert not task_list.has_tasks
    assert task_list.status == "0 of 0 tasks completed"
```

This test verifies that removing tasks keeps the summary statistics in sync. After removing the completed task, the status must no longer count it, and changing the removed task must not affect the task list anymore. Finally, it removes all tasks and checks that the task list is empty again.

### `test_create_task_input`

```python
def test_create_task_input():
    """We can create a TaskInput widget"""
    task_input = TaskInput()
    assert not task_input.value
    assert task_input.submit_task.disabled
```

This test ensures that we can create a `TaskInput` widget successfully. It checks if the initial value of the widget is `None` and that the *Add* button starts out disabled.

### `test_enter_text_into_task_input`

```python
def test_enter_text_into_task_input():
    """When we enter text into a TaskInput a Task is created"""
    task_input = TaskInput()

    task_input.text_input.value_input = "some value"
    assert not task_input.submit_task.disabled

    task_input.text_input.value = "some value"
    assert task_input.value
    assert task_input.value.value == "some value"
    assert task_input.text_input.value == ""
    assert task_input.submit_task.disabled
```

This test verifies the behavior of entering text into the `TaskInput` widget. Because the `TaskInput` exposes its widgets as the `text_input` and `submit_task` attributes, the test can interact with them directly without depending on how they are laid out. Typing enables the *Add* button. Setting the value, which is what happens when the user presses <kbd>Enter</kbd>, creates a task whose value matches the entered text. Additionally, it ensures that the input field is cleared and the button disabled again afterwards.

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
    assert len(task_list_editor.task_column) == 3
```

This test validates if we can create a `TaskListEditor` successfully. It initializes a task list with predefined tasks and creates a task list editor from it, ensuring that the editor is correctly instantiated and displays a row for each task.

### `test_task_list_editor_can_add_and_remove_tasks`

```python
def test_task_list_editor_can_add_and_remove_tasks():
    """We can add and remove tasks using the TaskListEditor"""
    task_list = TaskList(value=[Task(value="Inspect the blades", completed=True)])
    task_list_editor = TaskListEditor(value=task_list)

    task_list_editor.task_input.text_input.value_input = "Tighten the bolts"
    task_list_editor.task_input.submit_task.clicks += 1

    assert [task.value for task in task_list.value] == ["Inspect the blades", "Tighten the bolts"]
    assert len(task_list_editor.task_column) == 2
    assert task_list.status == "1 of 2 tasks completed"

    task_list_editor.clear_button.clicks += 1

    assert task_list.value == []
    assert len(task_list_editor.task_column) == 0
    assert not task_list_editor.clear_button.visible
    assert task_list.status == "0 of 0 tasks completed"
```

This test simulates a user working with the `TaskListEditor`. It types a new task and clicks the *Add* button by incrementing its `clicks`, then checks that the task was added to the task list and displayed. Then it clicks the *Remove All* button and checks that all tasks are removed, the column of tasks is empty and the button is hidden.

## Recap

In this tutorial, you have learned how to test Panel apps built using the class-based approach.

We firmly believe that the simplicity and accessibility of testing Panel components underscore a truly invaluable facet of Panel.

## Further Learning

To dive deeper into testing Panel apps, explore the [Testing How-To Guides](../../how_to/test/index.md) and [Panel's own tests](https://github.com/holoviz/panel/tree/main/panel/tests). The tests above exercise the Python side of the app only. To check that the app also renders and responds correctly in a real browser, see [Test UI rendering](../../how_to/test/uitests.md), which shows how to test a Panel app with Pytest and Playwright.
