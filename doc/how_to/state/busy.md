# Access Busyness state

This guide addresses how to access the busy state.

---

Often an application will have longer running callbacks which are being processed on the server, to give users some indication that the server is busy you may therefore have some way of indicating that busy state. The `pn.state.busy` parameter indicates whether a callback is being actively processed and may be linked to some visual indicator.

Below we will create a little application to demonstrate this, we will create a button which executes some longer running task on click and then create an indicator function that displays `'I'm busy'` when the `pn.state.busy` parameter is `True` and `'I'm idle'` when it is not:

```{pyodide}
import time
import panel as pn
pn.extension() # for notebook

def processing(event):
    # Some longer running task
    time.sleep(1)

button = pn.widgets.Button(name='Click me!')
button.on_click(processing)

def indicator(busy):
    return "I'm busy" if busy else "I'm idle"

pn.Row(button, pn.bind(indicator, pn.state.param.busy)).servable()
```

This way we can create a global indicator for the busy state instead of modifying all our callbacks.

## Relate Resources
