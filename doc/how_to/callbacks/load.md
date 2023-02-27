# Defer Callbacks Until Load

This guide addresses how to set up callbacks to defer a task until the application is loaded.

---

Using the `onload` callback, we can trigger execution when a session is first initialized in a server context. An example of when this could be a helpful strategy is when we have to fetch something from some database, like the options that will go into a selection widget. Since this operation might take some time, we can quickly render something on the screen for the user to look at while the `onload` callback is continuing to fetch the options in the background.

Let us for example define a minimal example inside a function which we could pass to `pn.serve` (this emulates what happens when we call `panel serve` on the command line). In this example, we will create a widget without populating its options, then we will add an `onload` callback, which will set the options once the initial page is loaded.

```{pyodide}
import time
import panel as pn

def app():
    widget = pn.widgets.Select()

    def on_load():
        time.sleep(2) # Emulate some long running process
        widget.options = ['A', 'B', 'C']

    pn.state.onload(on_load)

    return widget

# pn.serve(app) # launches the app
```

Alternatively, we may also use the `defer_load` argument to wait to evaluate a function until the page is loaded. In a situation where page loading takes some time, a placeholder and the global `config.loading_spinner` will be displayed.

```{pyodide}

def render_on_load():
    return pn.widgets.Select(options=['A', 'B', 'C'])

pn.Row(pn.panel(render_on_load, defer_load=True))
```

## Related Resources
