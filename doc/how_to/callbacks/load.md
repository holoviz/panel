# Load callbacks

This guide addresses how to set up callbacks to defer a task until the application is loaded.

---

A useful callback strategy is to define the `onload` callback which will trigger execution when a session is first initialized in a server context. Imagine for example that we have to fetch the options from some database which might take a little while, by deferring the loading of the options to the callback we can get something on the screen as quickly as possible and only run the expensive callback when we have already rendered something for the user to look at.

Let us for example define a minimal example inside a function which we could pass to `pn.serve` (this emulates what happens when we call `panel serve` on the command line). In this example, we will create a widget without populating its options, then we will add an `onload` callback, which will set the options once the initial page is loaded.

```{pyodide}
import time

import panel as pn

def app():
    widget = pn.widgets.Select()

    def on_load():
        time.sleep(1) # Emulate some long running process
        widget.options = ['A', 'B', 'C']

    pn.state.onload(on_load)

    return widget

# pn.serve(app)
```

Alternatively we may also use the `defer_load` option to wait to evaluate a function until the page is loaded. This will render a placeholder and display the global `config.loading_spinner`:

```{pyodide}
def render_on_load():
    return pn.widgets.Select(options=['A', 'B', 'C'])

pn.Row(pn.panel(render_on_load, defer_load=True))
```

## Related Resources
