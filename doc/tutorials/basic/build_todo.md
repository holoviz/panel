# Build a Todo App

In this section we will build a *Todo App* so that our wind turbine technicians can keep track of their tasks. The app will provide functionality to

- Add, remove and *remove all* tasks
- Mark a task as solved
- Keep track of how many completed tasks there are
- Disable or hide Buttons it does not make sense to click

:::{note}
When we ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Create the App

```{pyodide}
import panel as pn

pn.extension(sizing_mode="stretch_width", design="material")

BUTTON_WIDTH = 125

# We use intslider to avoid teaching users pn.rx. Is that a good thing?
state_changed_count = pn.widgets.IntInput()
tasks = pn.Column()

def update_state_changed_count(*args):
    state_changed_count.value += 1

def remove_task(task, *args):
    index = tasks.index(task)
    tasks.pop(index)

def remove_all_tasks(*args):
    tasks.clear()

def create_task(text):
    state = pn.widgets.Checkbox(align="center", sizing_mode="fixed")
    content = pn.pane.Markdown(text)
    remove = pn.widgets.Button(width=BUTTON_WIDTH, icon="trash", sizing_mode="fixed")
    task = pn.Row(state, content, remove, sizing_mode="stretch_width")

    pn.bind(remove_task, task, remove, watch=True)
    # We have to bind the below after the above!
    pn.bind(update_state_changed_count, state, remove, watch=True)

    return task

def add_task(text, *args):
    if not text:
        return

    new_task = create_task(text)
    tasks.append(new_task)

    return tasks

def get_state(*args):
    total_tasks = len(tasks)
    completed_tasks = sum(check[0].value for check in tasks)
    return f"{completed_tasks} of {total_tasks} tasks completed"

def can_add(value_input):
    return not bool(value_input)

def has_tasks(*args):
    return len(tasks)>0


add_task("Inspect the blades")
add_task("Inspect the nacelle")
add_task("Tighten the bolts")

text_input = pn.widgets.TextInput(name="Task", placeholder="Enter a task")

submit_task = pn.widgets.Button(
    name="Add",
    align="center",
    button_type="primary",
    width=BUTTON_WIDTH,
    sizing_mode="fixed",
    disabled=pn.bind(can_add, text_input.param.value_input)
)
clear = pn.widgets.Button(
    name="Remove All",
    button_type="primary",
    button_style="outline",
    width=BUTTON_WIDTH,
    sizing_mode="fixed",
    visible=pn.bind(has_tasks, state_changed_count)
)

def reset_text_input(*args):
    text_input.value = text_input.value_input = ""

pn.bind(add_task, text_input, submit_task, watch=True)
pn.bind(reset_text_input, text_input, submit_task, watch=True)
pn.bind(remove_all_tasks, clear, watch=True)
# We have to bind the below after the above!
pn.bind(update_state_changed_count, text_input, submit_task, clear, watch=True)

status_report = pn.bind(get_state, state_changed_count, tasks.param.objects)

pn.Column(
    "## WTG Task List",
    status_report,
    pn.Row(text_input, submit_task),
    tasks,
    pn.Row(pn.Spacer(), clear),
    max_width=500,
).servable()
```

Try to

- Remove one task
- Remove all tasks
- Add 3 Tasks
- Check 1 of 3 tasks and see the `status_message` update accordingly.

:::{note}
A todo app can be build in many other ways. The main purpose of this example is for you to acquire the basic skills needed to develop *stateful*, *dynamically updating* apps like this one.
:::

## Break it down

We will now break down the example together to get a better understanding of the code.

COMING UP

## Recap

In this section we have built a *Todo App* with many features. We needed to combine many of the things we have learned so far.

## Resources

COMING UP
