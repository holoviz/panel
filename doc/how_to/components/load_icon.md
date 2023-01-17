# Customize Loading Icon

All components also have a `loading` parameter which indicates that they are currently processing some event. Setting the parameter will display the global `loading_spinner` on top of the component.

First, to configure the type and color of loading spinner you can set the:

* `pn.config.loading_spinner`: The style of the global loading indicator, e.g. 'arc', 'arcs', 'bar', 'dots', 'petal'.
* `pn.config.loading_color`: The color of the global loading indicator as a hex color or color name, e.g. '#6a6a6a', 'black'.

```{pyodide}

import panel as pn
pn.config.loading_spinner = 'petal'
pn.config.loading_color = 'black'

```

If we are working in a notebook, we can now activate the panel extension after having set the config parameters. Alternatively, we could have set the config with `pn.extension(loading_spinner='petal', loading_color='black')`

```{pyodide}

pn.extension()

```

Next, let's display a simple component and set `loading=True`:

```{pyodide}

pn.pane.HTML(background='#00aa41', width=100, height=100, loading=True)

```
