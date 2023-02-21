# Arrange Components in a Template

This guide addresses how to arrange components in a template layout.

```{admonition} Prerequisites
1. The [How to > Set a Template](./template_set.md) guide demonstrates how to set a template for a deployable app.
```

---

The default templates that are provided with Panel define four content areas on the page, which can be populated as desired: `header`, `sidebar`, `main`, and `modal` (a dialog box/popup window).

Let's create a simple app and place components in the `header`, `sidebar`, and `main` areas (see the dedicated guide on the [`modal`](./template_modal.md)). We'll first save this script below into a file called `app.py`:

:::{card} app.py
``` {code-block} python
:emphasize-lines: 19-22

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
        height=200, width=400)

# Add components to the sidebar, main, and header
bootstrap.sidebar.extend([freq, phase])
bootstrap.main.append(pn.Card(hv.DynamicMap(sine), title='Sine'))
bootstrap.header.append('## Header')

bootstrap.servable()
```
:::

Now, we can activate this app on the command line:

``` bash
panel serve app.py --show --autoreload
```

<img src="../../_static/template_arrange.png" alt="example panel app">

## Related Resources

- See [How-to > Apply Templates > Toggle Modal](./template_modal.md) for a dedicated guide to toggling the modal.
- See [How-to > Apply Templates > Set a Template](./template_set.md) for alternate approaches to set a template.
- Read [Background > Templates](../../background/templates/templates_overview.md) for explanation.
