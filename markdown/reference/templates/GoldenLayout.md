# GoldenLayout
---
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
* **`header_background`** (str): Optional header background color override.
* **`header_color`** (str): Optional header text color override.
* **`logo`** (str): URI of logo to add to the header (if local file, logo is base64 encoded as URI).
* **`site`** (str): Name of the site. Will be shown in the header. Default is '', i.e. not shown.
* **`site_url`** (str): Url of the site and logo. Default is "/".
* **`title`** (str): A title to show in the header.
* **`theme`** (Theme): A Theme class (available in `panel.template.theme`)
* **`sidebar_width`** (int): The width of the sidebar in percent. Default is 20.

________

In this case we are using the `GoldenTemplate`, built using the [Golden Layout CSS](https://golden-layout.com/), which allows for the creation of tabs that can be moved around. Due to the movable tabs this Template is a little different than the others. The sidebar works similarly to the other templates, but to have your displays render in different tabs, we have to make separate calls to `<template_name>.main.append()`. Here is an example of how you can set up a display using this template:

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
template = pn.template.GoldenTemplate(
    title='GoldenTemplate',
    sidebar=[freq, phase],
)
# Append a layout to the main area, to demonstrate the list-like API
template.main.append(
    pn.Row(
        pn.Card(dfi_sine.hvplot(**plot_opts).output(), title='Sine'),
        pn.Card(dfi_cosine.hvplot(**plot_opts).output(), title='Cosine'),
    )
)

template.servable();
```

Each built-in template comes with a *light* (default) and *dark* theme. The theme can be set when instantiating the template with the `theme` parameter, or [globally](../../how_to/styling/themes.md).

<h3><b>GoldenTemplate with DefaultTheme</b></h3>

</br>
<h3><b>GoldenTemplate with DarkTheme</b></h3>

---
