# Batching Updates with `hold`

When working with interactive dashboards and applications in Panel, you might encounter situations where updating multiple components simultaneously causes unnecessary re-renders. This is because Panel generally dispatches any change to a parameter immediately. This can lead to performance issues and a less responsive user experience because each individual update may trigger re-renders on the frontend. The `hold` utility in Panel allows you to batch updates to the frontend, reducing the number of re-renders and improving performance.

In this guide, we'll explore how to use `hold` both as a context manager and as a decorator to optimize your Panel applications.

## What is `hold`?

The `hold` function is a context manager and decorator that temporarily holds events on a Bokeh Document. When you update multiple components within a `hold` block, the events are collected and dispatched all at once when the block exits. This means that the frontend will only re-render once, regardless of how many updates were made, leading to a smoother and more efficient user experience.

Let’s try first **without `hold`** to understand the difference `hold` can make:

```{pyodide}
import panel as pn
from panel.io import hold

def increment(e):
    for obj in column_0:
        obj.object = str(e.new)

column_0 = pn.FlexBox(*['0']*100)
button = pn.widgets.Button(name='Increment', on_click=increment)

pn.Column(column_0, button).servable()
```

## Using `hold`

### As a Decorator

If you have a function that updates components and you want to ensure that all updates are held, you can use `hold` as a decorator. For example, here we update 100 components at once. If you do not use `hold`, each of these events is sent and applied in series, potentially resulting in visible updates.

```{pyodide}
import panel as pn
from panel.io import hold

@hold()
def increment(e):
    for obj in column_1:
        obj.object = str(e.new)

column_1 = pn.FlexBox(*['0']*100)
button = pn.widgets.Button(name='Increment', on_click=increment)

pn.Column(column_1, button).servable()
```

Applying the `hold` decorator means all the updates are sent in a single WebSocket message and applied on the frontend simultaneously.

### As a Context Manager

Alternatively, the `hold` function can be used as a context manager, potentially giving you finer-grained control over which events are batched and which are not:

```{pyodide}
import time

import panel as pn
from panel.io import hold

def increment(e):
    with button.param.update(name='Incrementing...', disabled=True):
        with hold():
            for obj in column_2:
                obj.object = str(e.new)

column_2 = pn.FlexBox(*['0']*100)
button = pn.widgets.Button(name='Increment', on_click=increment)

pn.Column(column_2, button).servable()
```

Here the updates to the `Button` are dispatched immediately, while the updates to the counters are batched.
