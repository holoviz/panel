# Load callbacks

Another useful callback to define the onload callback, in a server context this will execute when a session is first initialized. Let us for example define a minimal example inside a function which we will pass to `pn.serve`. This emulates what happens when we call `panel serve` on the commandline. We will create a widget without populating its options, then we will add an `onload` callback, which will set the options once the initial page is loaded. Imagine for example that we have to fetch the options from some database which might take a little while, by deferring the loading of the options to the callback we can get something on the screen as quickly as possible and only run the expensive callback when we have already rendered something for the user to look at.

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
