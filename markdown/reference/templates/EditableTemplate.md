# EditableTemplate
---
The `EditableTemplate` builds on the `VanillaTemplate` extending it with functionality for editing the layout of the components on the page. It is a list-like variant where the `main` area acts like a list-like container, unlike the grid-like templates such as `React` and `FastGridTemplate`. Specifically it allows for the following actions:

- **Hide** outputs
- **Resize** outputs
- **Rearrange** outputs

In this way a dashboard can be built using a drag and drop approach. The resulting layout can then be persisted into local storage. To open the dashboard in `editable` mode you can either set the `editable=True` option or append `?editable=true` as a URL parameter.

The `EditableTemplate` is used by the Panel layout builder functionality which makes it trivial to go from a notebook to a deployed dashboard by using the drag-and-drop interface to lay out components on the page.

## Basic Templates

For a large variety of use cases we do not need complete control over the exact layout of each individual component on the page, as could be achieved with a [custom template](../../explanation/styling/templates_overview.md), we just want to achieve a more polished look and feel. For these cases Panel ships with a number of default templates, which are defined by declaring four main content areas on the page, which can be populated as desired:

* **`header`**: The header area of the HTML page
* **`sidebar`**: A collapsible sidebar
* **`main`**: The main area of the application
* **`modal`**: A modal area which can be opened and closed from Python

These four areas behave very similarly to other Panel layout components and have list-like semantics. This means we can easily append new components into these areas. Unlike other layout components however, the contents of the areas is fixed once rendered. If you need a dynamic layout you should therefore insert a regular Panel layout component (e.g. a `Column` or `Row`) and modify it in place once added to one of the content areas.

Templates can allow for us to quickly and easily create web apps for displaying our data. Panel comes with a default Template, and includes multiple Templates that extend the default which add some customization for a better display.

#### Parameters:

In addition to the four different areas we can populate the default templates also provide a few additional parameters:

* **`busy_indicator`** (BooleanIndicator): Visual indicator of application busy state.
* **`collapsed_sidebar`** (str, `default=False`): Whether the sidebar (if present) is initially collapsed.
* **`editable`** (bool, `default=True`): Whether the layout of the template should be editable.
* **`header_background`** (str): Optional header background color override.
* **`header_color`** (str): Optional header text color override.
* **`logo`** (str): URI of logo to add to the header (if local file, logo is base64 encoded as URI).
* **`site`** (str): Name of the site. Will be shown in the header. Default is '', i.e. not shown.
* **`site_url`** (str): Url of the site and logo. Default is "/".
* **`title`** (str): A title to show in the header.
* **`theme`** (Theme): A Theme class (available in `panel.template.theme`)
* **`sidebar_width`** (int): The width of the sidebar in pixels. Default is 330.

________

The `EditableTemplate` can be populated like any other list-like template, by extending the `main` layout:

```python
import hvplot.pandas
import numpy as np
import panel as pn
import pandas as pd

xs = np.linspace(0, np.pi)

freq = pn.widgets.FloatSlider(label="Frequency", start=0, end=10, value=2)
phase = pn.widgets.FloatSlider(label="Phase", start=0, end=np.pi)

def sine(freq, phase):
    return pd.DataFrame(dict(y=np.sin(xs*freq+phase)), index=xs)

def cosine(freq, phase):
    return pd.DataFrame(dict(y=np.cos(xs*freq+phase)), index=xs)

dfi_sine = hvplot.bind(sine, freq, phase).interactive()
dfi_cosine = hvplot.bind(cosine, freq, phase).interactive()

plot_opts = dict(responsive=True, min_height=400)

# Instantiate the template with widgets displayed in the sidebar
template = pn.template.EditableTemplate(
    editable=True,
    title='EditableTemplate',
    sidebar=[freq, phase],
)
# Append a layout to the main area, to demonstrate the list-like API
template.main.extend([
    dfi_sine.hvplot(title='Sine Plot', **plot_opts).output(),
    dfi_cosine.hvplot(title='Cosine Plot', **plot_opts).output(),
])

template.servable();
```

The resulting default layout will simply initialize each component on top of one another:

If the template is in editable mode we can delete, resize, and rearrange the outputs on the page using a drag and drop interface.

- Delete: Hover on the top-right to reveal the delete icon

- Resize: Hover on the bottom-right to reveal the resize handle

- Rearrange: Hover on the top-left to reveal the drag icon

In edit mode we additionally have undo, reset and save icons in the header:

- Undo: Undo previous delete, resize and re-arrange actions.

- Reset: Resets the arrangement and order of the individual components to the default.

- Save: Persists the current layout into the browser storage overriding the layout persisted on the server.

---
