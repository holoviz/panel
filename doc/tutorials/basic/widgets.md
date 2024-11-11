# Accept Inputs with Widgets

Welcome to the tutorial on accepting user inputs with widgets in Panel! Let's dive into the world of interactive components and explore how they can enhance your Panel applications.

## Introduction to Widgets

Widgets, found within the `pn.widgets` namespace, are powerful tools for capturing user input and interaction. They offer a wide range of functionality and customization options, making them essential for creating dynamic and engaging apps.

You can explore the full array of available widgets and their detailed reference guides in the [Widgets Section](../../reference/index.rst#widgets) of the [Component Gallery](../../reference/index.rst).

:::{note}
Widgets typically utilize the `value` parameter to capture user input.
Some widgets, such as the [`Button`](../../reference/widgets/Button.md), even allow you to register callback functions that trigger actions upon interaction.

For more complex scenarios, widgets like the [`Tabulator`](../../reference/widgets/Tabulator.md) offer versatile input capabilities.

In some cases, Panes can accept user input too. For example, the [`ECharts`](../../reference/panes/ECharts.md), [`Plotly`](../../reference/panes/Plotly.md), and [`Vega`](../../reference/panes/Vega.md) (Altair) panes can accept user inputs.

:::

## Leveraging Widgets for Input

Beyond just capturing clicks, widgets allow for a myriad of input types, from simple text to selection from lists. Let's explore some common scenarios:

### Accept Clicks with Buttons

Let's start by examining how to create a button that users can click to trigger actions:

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

With features like icons, button types, and descriptions, buttons provide both functionality and visual cues to users. Hover over the button to see its description displayed as a helpful tooltip.

:::{note}
The `.servable()` method is used to include the component in the app served by `panel serve app.py --dev`. This is not necessary for displaying the component in a notebook.
:::

For a deeper understanding of the `Button` widget and its capabilities, refer to its detailed [reference guide](../../reference/widgets/Button.md).

### Accept Text Input

Next, let's explore capturing textual input from users:

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

Hover over the input field to see its description as a tooltip. Try enabling the input by changing `disabled=True` to `disabled=False`. You'll also notice how the `max_length` parameter limits input length.

To delve into the details of the `TextInput` widget, check out its [reference guide](../../reference/widgets/TextInput.md).

### Selecting from a List

Another common scenario is allowing users to select options from a list:

```{pyodide}
import panel as pn

pn.extension()

pn.widgets.Select(
    description="Select a Technology",
    name="Study",
    options=["Wind Turbine", "Solar Panel", "Battery Storage"],
).servable()
```

Widgets like `Select` offer straightforward selection mechanisms. You can easily replace it with alternatives like `RadioButtonGroup` for different user experiences:

```{pyodide}
import panel as pn

pn.extension()

pn.widgets.RadioButtonGroup(
    description="Select a Technology",
    name="Study",
    options=["Wind Turbine", "Solar Panel", "Battery Storage"],
).servable()
```

## Recap

In this tutorial, we've covered various ways to accept user input using widgets in Panel. From simple clicks to text input and selection from lists, widgets provide powerful tools for building interactive applications.

Don't forget to explore the [Component Gallery](../../reference/index.rst#widgets) for more widgets and their detailed reference guides.

## Resources

### Tutorials

- [React to User Input](pn_bind.md)

### How-To

- [Migrate from Streamlit | Accept User Input](../../how_to/streamlit_migration/widgets.md)

### Explanation

- [Components Overview](../../explanation/components/components_overview.md)

### Component Gallery

- [Widgets](../../reference/index.rst#widgets)
