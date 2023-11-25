# Style Matplotlib Plots

This guide addresses how to style Matplotlib plots displayed using the [Matplotlib pane](../../../examples/reference/panes/Matplotlib.ipynb).

There are nearly 30 builtin styles to Matplotlib that can be activated with the `plt.style.use` function. The style names are listed in the `plt.style.available` array.

For more info check out the [Matplotlib style sheets reference](https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html) and the alternative themes [dracula theme](https://draculatheme.com/matplotlib) and [gadfly](https://towardsdatascience.com/a-new-plot-theme-for-matplotlib-gadfly-2cffc745ff84).

The gif below displays an example of what can be achieved with a little styling of the `Matplotlib` figure and the `FastListTemplate`.

![Matplotlib + FastListTemlate Styling Example](https://assets.holoviews.org/panel/thumbnails/gallery/styles/matplotlib-styles.gif)

## A Matplotlib plot with dark theme and accent color

In this example we will give the Matplotlib plot a dark theme and a custom accent color.

```{pyodide}
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.figure import Figure

import panel as pn

pn.extension()

ACCENT_COLOR = "#F08080"
STYLE = "dark_background"

x = np.arange(-2, 8, .1)
y = .1 * x ** 3 - x ** 2 + 3 * x + 2


plt.style.use("default") # reset to not be affected by previous style changes
plt.style.use(STYLE) # change to the specified style

fig0 = Figure(figsize=(12, 6))
ax0 = fig0.subplots()
ax0.plot(x, y, linewidth=10.0, color=ACCENT_COLOR)
ax0.set_title(f'Matplotlib Style: {STYLE}');

plt.style.use("default") # reset to not affect style of other plots

pn.pane.Matplotlib(fig0, max_height=500, sizing_mode="scale_height").servable()
```

## The Matplotlib Styles

Lets list the available styles for your convenience

```{pyodide}
pn.panel(plt.style.available).servable()
```
