# Control Size

This guide addresses how to control the size of components.

---

Components can use either one of the responsive sizing modes or absolute sizing.

:::{admonition} Important
:class: important

Unlike other components, the size of a plot component is usually determined by the underlying plotting library, so it may be necessary to ensure that you set the size and aspect when declaring the plot.

:::

## Absolute Sizing

To set a fixed size on a component, it is usually sufficient to set a `width` or `height`, but in certain cases setting ``sizing_mode='fixed'`` explicitly may also be required.

Let's create a simple example that fixes the height or width of several components:

```{pyodide}
import panel as pn
pn.extension() # for notebook

pn.Row(
    pn.pane.Markdown('ABCDE', styles={'background': '#f0f0f0'}, width=75, height=100),
    pn.widgets.FloatSlider(width=200, styles={'background': '#f0f0f0'}),
    pn.pane.PNG('https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png', width=300, styles={'background': '#f0f0f0'}),
)
```

Now let's use ``sizing_mode='fixed'`` to create a fixed-size component. This will retain the object's original width and height regardless of any subsequent browser window resize events. This is usually the default behavior and simply respects the provided width and height.

```{pyodide}
pn.pane.PNG('https://upload.wikimedia.org/wikipedia/commons/8/89/PNG-Gradient.png', sizing_mode='fixed')
```

## Responsive Sizing

Most panel objects support reactive sizing which adjusts depending on the size of the visible area of a web page. Responsive sizing modes can be controlled using the ``sizing_mode`` parameter with the following options:

* **"stretch_width"**: Component will responsively resize to stretch to the available width, without maintaining any aspect ratio. The height of the component depends on the type of the component and may be fixed or fit to component's contents. To demonstrate this behavior we create a Row with a fixed height and responsive width to fill:

```{pyodide}
pn.Row(
    pn.pane.Str(styles={'background': '#f0f0f0'}, height=100, sizing_mode='stretch_width'),
    width_policy='max', height=200
)
```

* **"stretch_height"**: Component will responsively resize to stretch to the available height, without maintaining any aspect ratio. The width of the component depends on the type of the component and may be fixed or fit to component's contents. To demonstrate the filling behavior in a document we declare a Column with a fixed height for the component to fill:

```{pyodide}
pn.Column(
    pn.pane.Str(styles={'background': '#f0f0f0'}, sizing_mode='stretch_height', width=200),
    height=200
)
```

* **"stretch_both"**: Component is completely responsive, independently in width and height, and will occupy all the available horizontal and vertical space, even if this changes the aspect ratio of the component. To demonstrate this behavior we will declare a Column with a fixed height and responsive width for the component to fill:

```{pyodide}
pn.Column(
    pn.pane.Str(styles={'background': '#f0f0f0'}, sizing_mode='stretch_both'),
    height=200, width_policy='max'
)
```

* **"scale_height"**: Component will responsively resize to stretch to the available height, while maintaining the original or provided aspect ratio.
* **"scale_width"**: Component will responsively resize to stretch to the available width, while maintaining the original or provided aspect ratio.
* **"scale_both"**: Component will responsively resize to both the available width and height, while maintaining the original or provided aspect ratio. For example:


```{pyodide}
pn.Column(
    pn.pane.PNG(
        'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png',
        sizing_mode='scale_both'
    ), height=400, width=500, styles={'background': '#f0f0f0'})
```

## Constrain Responsive Sizes

The `min_width`, `max_width`, `min_height`, and `max_height` parameters limit
how far a responsive component can shrink or grow. A bound only affects an
adjustable dimension, so pair `max_width` with a width-responsive sizing mode
and `max_height` with a height-responsive sizing mode.

For example, the pane below fills the available width until it reaches 500
pixels, and never shrinks below 200 pixels:

```{pyodide}
pn.pane.Markdown(
    "Resize the browser to see the width change.",
    sizing_mode="stretch_width",
    min_width=200,
    max_width=500,
    styles={"background": "#f0f0f0", "padding": "1rem"},
)
```

The `width` and `height` parameters act as preferred sizes when the
corresponding dimension is responsive. The minimum and maximum bounds still
take precedence.

## Set a Default Sizing Mode

To avoid repeating the same `sizing_mode` on every component, set a default
when loading Panel:

```python
pn.extension(sizing_mode="stretch_width")
```

The equivalent configuration setting is useful when Panel has already been
loaded:

```python
pn.config.sizing_mode = "stretch_width"
```

These defaults apply to components created afterwards. A `sizing_mode`
specified directly on a component takes precedence.

## Fine-grained Width and Height Policies

The `width_policy` and `height_policy` parameters provide lower-level control
over each dimension. They take precedence over `sizing_mode` and accept the
same policy choices for the horizontal and vertical axes:

| Policy | Behavior |
| --- | --- |
| `"auto"` | Use the component's preferred policy. |
| `"fixed"` | Use exactly `width` or `height`; the component may overflow its container. |
| `"fit"` | Prefer `width` or `height`, but fit within the available space and any minimum or maximum bounds. |
| `"min"` | Use as little space as possible without crossing the minimum bound. |
| `"max"` | Use as much space as possible without crossing the maximum bound. |

For example, `width_policy="max"` makes this row use the available horizontal
space, while `max_width` prevents it from becoming wider than 600 pixels:

```{pyodide}
pn.Row(
    pn.widgets.TextInput(name="Name", width_policy="max"),
    pn.widgets.Button(name="Submit"),
    width_policy="max",
    max_width=600,
)
```

---

## Related Resources
