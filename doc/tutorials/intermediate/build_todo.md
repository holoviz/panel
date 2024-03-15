# Build a Todo App

Welcome to the "Build a Todo App" tutorial! In this section, we're going to create a dynamic *Todo App* together. Imagine our wind turbine technicians being able to manage their tasks efficiently with this application. We'll collaborate to develop an app with features like:

- Adding, removing, and clearing tasks
- Marking tasks as completed
- Tracking the number of completed tasks
- Dynamically disabling or hiding buttons

Previously, we built a [basic todo app](../basic/build_todo.md) using a function-based approach. This time, we'll employ a more sophisticated `Parameterized` class-based approach. This method will enhance the extensibility and maintainability of our todo app in the long run.

<iframe src="https://panel-org-build-todo-app.hf.space" frameborder="0" style="width: 100%;height:500px"></iframe>

:::{dropdown} Requirements

```bash
panel
```

:::

:::{dropdown} Code

```python
"""An app to manage tasks"""
from typing import List

import param

import panel as pn

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

    value: List[Task] = param.List(item_type=Task, doc="A list of Tasks")

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

    value: Task = param.ClassSelector(item_type=Task, doc="""The Task input by the user""")

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
    pn.extension(sizing_mode="stretch_width", design="material")

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

## Explanation

Let's break down the todo app.

### Import Necessary Libraries

```{pyodide}
"""An app to manage tasks"""
from typing import List
import param
import panel as pn

pn.extension(sizing_mode="stretch_width", design="material")
```

Here, we import the required libraries for our task management app. We use `List` from the `typing` module to define a list of tasks, [`param`](https://param.holoviz.org) for declaring parameters, and `panel` for creating the user interface. We configure the `"material"` design to give the todo app a modern look and feel.

### Define Constants

```{pyodide}
BUTTON_WIDTH = 125
```

We set a constant `BUTTON_WIDTH` to control the width of buttons in our app.

### Define Task Model

```{pyodide}
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

Task(value="Inspect the blades")
```

This class defines the model of a task. It has two attributes: `value` (description of the task) and `completed` (whether the task is completed or not). The `__panel__` method renders the task as a row containing a checkbox for completion status and the task description.

### Define TaskList Class

```{pyodide}
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

TaskList(value=[Task(value="Inspect the blades")])
```

This class represents a list of tasks. It provides methods to add and remove tasks, as well as calculate summary statistics such as the total number of tasks, the number of completed tasks, and a status message.

:::{note}

The `TaskList` and the rest of the todo app follows the *DataStore design pattern* introduced in [Structure with a DataStore](structure_data_store.md).

:::

### Define TaskInput Class

```{pyodide}
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

TaskInput()
```

This class represents a widget for users to input tasks.

The `__panel__` method defines the appearance and behavior of the task input widget. It consists of a text input field for entering task descriptions and a button to submit the task.

### Define TaskRow Class

```{pyodide}
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

TaskRow(value=Task(value="Inspect the blades"))
```

This method defines the appearance of the task row, which consists of the task description and a button to remove the task.

### Define TaskListEditor Class

```{pyodide}
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

task_list = TaskList(
    value=[
        Task(value="Inspect the blades", completed=True),
        Task(value="Inspect the nacelle"),
        Task(value="Tighten the bolts"),
    ]
)
TaskListEditor(value=task_list).servable()
```

This class represents a component that allows users to manage a list of tasks.

This `__panel__` method defines the appearance and behavior of the task list editor component. It consists of an input field for adding tasks, a list of tasks, and a button to remove all tasks.

## Recap

We've built a todo app using a `Parameterized` class-based approach and the *DataStore design pattern*. Now, our wind turbine technicians can manage their tasks efficiently and collaboratively.
