# Accept User Input

In this guide you will learn to accept user input with *widgets*:

- *Widgets* are available in the `pn.widgets` namespace.
- *Widgets* normally provide the user input via the `value` parameter.
- *Widgets* normally allow you to provide the initial `value`.
- *Widgets* have common parameters like `name`, `description` and `disabled`.
  - The `name` is often used as a *label*.
  - The `description` is often used as a tooltip.
- Accept *click* input with the `Button` widget.
- Accept *text* input with the `TextInput` widget.
- Accept an object from a list of objects with the `Select` widget.
- Panels widgets come in groups of *interchangeable* widgets.
  - Replace the `Select` widget with the `RadioButtonGroup` widget to change the user experience.
- Discover all *Widgets* and their *reference guides* in the [Widgets Section](../../reference/index.md#widgets) of the [Component Gallery](../../reference/index.md).

In this tutorial you will **not learn** how to

- Use specific *Widgets* in detail. Details are covered by the *[reference guides](../../reference/index.md#widgets)*.
- React to user input. This is covered by the [React to User Input](bind.md) tutorial
- Style or align *Widgets*. These topics are covered by other tutorials.

:::{note}
A *Widget* is a component that can accept user inputs via the `value` parameter. Certain, more complex, widgets, such as [`Tabulator`](../../reference/widgets/Tabulator.ipynb) may allow additional forms of input via other parameters.

A *Widget* is defined as a component that inherits from the `Widget` base class.
:::

:::{note}
In some cases Panes can accept user input too. For example the [`ECharts`](../../reference/panes/ECharts.ipynb), [`Plotly`](../../reference/panes/Plotly.ipynb) and [`Vega`](../../reference/panes/Vega.ipynb) (Altair) panes can accept user inputs. These are usually selections, instead of modifying the underlying `object`.
:::

:::{note}
When we ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Accept Clicks

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.widgets.Button(
    name="Refresh",
    icon="refresh",
    button_type="primary",
    description="Click to refresh the data",
).servable()
```

As you can see the `Button` is quite feature rich supporting `icon`, `button_type` and `description`.

Try hovering over the button. You will see the `description` shown as a tooltip.

:::{note}
We add `.servable()` to the component to add it to the app served by `panel serve app.py --autoreload`. Adding `.servable()` is not needed to display the component in a notebook.
:::

:::{note}
To learn in detail how a *widget* like `Button` works you should refer to its *reference guide*.
:::

Click [this link](../../reference/widgets/Button.ipynb) to the `Button` Reference Guide and spend a few minutes to familiarize your self with its organization and content.

It should look like

[![Button reference guide](../../_static/images/widgets_button_reference.png)](../../reference/widgets/Button.ipynb)

## Accept Text

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.widgets.TextInput(
    description="The text given to the AI",
    disabled=True,
    max_length=15,
    name="Prompt",
    placeholder="What is Python?",
).servable()
```

Try hovering over the the circle with the question mark inside. You will see the `description` displayed as a tooltip.

If you are in a notebook or serving as an app try:

- enabling the `TextInput` by changing `disabled=True` to `disabled=False`.
- entering the text `1234567890123456` in the. You cannot because the `max_length` is `15`. The final `6` cannot be entered.

:::{admonition}
Its key for your success with Panel, that you learn how to navigate the [Component Gallery](../../reference/index.md) and use the *reference guides*.
:::

Click [this link](../../reference/index.md#widgets) to the Widgets Section of the [Component Gallery](../../reference/index.md). Identify the [TextInput Reference Guide](../../reference/widgets/TextInput.ipynb) and open it. You don't have to spend time studying the details right now.

It should look like

[![Widgets Gallery and TextInput Reference Guide](../../_static/images/widgets_textinput_reference.png)](../../reference/index.md#widgets)

## Accept an object from a list

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.widgets.Select(
    description="Select a Study",
    name="Study",
    options=["Biology", "Chemistry", "Physics"],
).servable()
```

:::{note}
Panels widgets comes in groups of *interchangeable* widgets. For example its very easy to replace the `Select` widget with the `RadioButtonGroup` widget.
:::

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.widgets.RadioButtonGroup(
    description="Select a Study",
    name="Study",
    options=["Biology", "Chemistry", "Physics"],
).servable()
```

:::{Admonition} Note
Usually widgets allow you to specify the *initial* `value`.
:::

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.widgets.RadioButtonGroup(
    button_type="primary",
    button_style="outline",
    description="Select a Study",
    name="Study",
    options=["Biology", "Chemistry", "Physics"],
    value="Physics",
).servable()
```

You will notice how `Physics` is now displayed as the *initial* `value` and how the `Button`s type and style was changed.

## Recap

In this tutorial you have learned:

- *Widgets* are available in the `pn.widgets` namespace.
- *Widgets* normally provide the user input via the `value` parameter.
- *Widgets* normally allow you to provide the initial `value`.
- *Widgets* have common parameters like `name`, `description` and `disabled`.
  - The `name` is often used as a *label*.
  - The `description` is often used as a tooltip.
- Accept *click* input with the `Button` widget.
- Accept *text* input with the `TextInput` widget.
- Accept an object from a list of objects with the `Select` widget.
- Panels widgets come in groups of *interchangeable* widgets.
  - Replace the `Select` widget with the `RadioButtonGroup` widget to change the user experience.
- Discover all *Widgets* and their *reference guides* in the [Widgets Section](../../reference/index.md#widgets) of the [Component Gallery](../../reference/index.md).

## Resources

### Tutorials

- [React to User Input](bind.md)

### How-To

- [Migrate from Streamlit | Accept User Input](../../how_to/streamlit_migration/widgets.md)

### Explanation

- [Components Overview](../../explanation/components/components_overview.md)

### Component Gallery

- [Widgets](../../reference/index.md#widgets)
