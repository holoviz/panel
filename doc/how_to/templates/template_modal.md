# Toggle Modal

This guide addresses how to toggle the modal area of a template.

```{admonition} Prerequisites
1. The [How to > Set a Template](./template_set.md) guide demonstrates how to set a template for a deployable app.
```

---

A modal can be opened and closed with `.open_modal()` and `.close_modal()` methods, respectively. Let's create a modal that is activated by a button on the sidebar. We'll first save this script below into a file called `app.py`:

:::{card} app.py
``` {code-block} python
:emphasize-lines: 24-36

import panel as pn
import numpy as np
import holoviews as hv

# Explicitly set template and add some text to the header area
bootstrap = pn.template.BootstrapTemplate(title='Bootstrap Template')

# Data and Widgets
xs = np.linspace(0, np.pi)
freq = pn.widgets.FloatSlider(name="Frequency", start=0, end=10, value=2)
phase = pn.widgets.FloatSlider(name="Phase", start=0, end=np.pi)

# Plotting function bound to widgets
@pn.depends(freq=freq, phase=phase)
def sine(freq, phase):
    return hv.Curve((xs, np.sin(xs*freq+phase))).opts(
        height=400, width=400)

# Add components to the sidebar, main, and header
bootstrap.sidebar.extend([freq, phase])
bootstrap.main.append(pn.Card(hv.DynamicMap(sine), title='Sine'))
bootstrap.header.append('## Header')

# Add some content to the modal area
bootstrap.modal.append("## This is a modal")

# Create a button
modal_btn = pn.widgets.Button(name="Click for modal")

# Callback that will open the modal when the button is clicked
def about_callback(event):
    bootstrap.open_modal()

# Link the button to the callback and append it to the sidebar
modal_btn.on_click(about_callback)
bootstrap.sidebar.append(modal_btn)

bootstrap.servable()
```
:::

Now we can activate this app on the command line. When we click the button in the sidebar, we see the modal pop up:

```bash
panel serve app.py --show --autoreload
```

<img src="../../_static/template_arrange_modal.png" alt="example panel app with an active modal">

## Related Resources

- See [How-to > Apply Templates > Set a Template](./template_set.md) for alternate approaches to set a template.
- Read [Background > Templates](../../background/templates/templates_overview.md) for explanation.
