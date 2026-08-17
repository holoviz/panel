# Spacer
---
```python
import panel as pn

pn.extension()
```

The ``Spacer`` component adds fixed or responsive empty space to a layout. The ``HSpacer`` and ``VSpacer`` variants expand along the horizontal and vertical axes, respectively.

#### Parameters:

* **``width``** (int): The fixed width of a ``Spacer`` in pixels.
* **``height``** (int): The fixed height of a ``Spacer`` in pixels.
* **``sizing_mode``** (str): Controls whether a ``Spacer`` has fixed dimensions or expands with its container. ``HSpacer`` uses ``'stretch_width'`` and ``VSpacer`` uses ``'stretch_height'``.

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

___

## Fixed spacing

Set ``width`` or ``height`` on a ``Spacer`` to reserve a fixed amount of room between components. This is useful when the spacing should remain unchanged as the browser is resized:

```python
pn.Row(
    pn.widgets.Button(name="One", width=100),
    pn.Spacer(width=50),
    pn.widgets.Button(name="Two", width=100),
    pn.Spacer(width=100),
    pn.widgets.Button(name="Three", width=100),
)
```

## Responsive horizontal spacing

An ``HSpacer`` expands to use the available horizontal space. Placing one before, between, and after the components distributes them evenly across the row:

```python
pn.Row(
    pn.HSpacer(),
    pn.widgets.Button(name="Left", width=100),
    pn.HSpacer(),
    pn.widgets.Button(name="Center", width=100),
    pn.HSpacer(),
    pn.widgets.Button(name="Right", width=100),
    pn.HSpacer(),
    width=700,
    styles={"border": "1px solid #d9d9d9"},
)
```

## Responsive vertical spacing

A ``VSpacer`` works the same way along the vertical axis. In a fixed-height column, the spacers grow and shrink to keep the components evenly distributed:

```python
pn.Column(
    pn.VSpacer(),
    pn.widgets.Button(name="Top", width=120),
    pn.VSpacer(),
    pn.widgets.Button(name="Middle", width=120),
    pn.VSpacer(),
    pn.widgets.Button(name="Bottom", width=120),
    pn.VSpacer(),
    height=350,
    width=180,
    align="center",
    styles={"border": "1px solid #d9d9d9"},
)
```

``HSpacer`` and ``VSpacer`` can also be combined to align a component within a larger layout. Here the horizontal spacer pushes the button to the right, while the vertical spacer pushes it to the bottom:

```python
pn.Column(
    pn.VSpacer(),
    pn.Row(
        pn.HSpacer(),
        pn.widgets.Button(name="Bottom right", width=120),
        sizing_mode="stretch_width",
    ),
    height=220,
    width=420,
    styles={"border": "1px solid #d9d9d9"},
)
```

---
