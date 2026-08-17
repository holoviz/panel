# Divider
---
```python
import panel as pn
import panel.widgets as pnw

pn.extension()
```

A `Divider` draws a horizontal rule (a `<hr>` tag in HTML) to separate multiple components in a layout. It automatically spans the full width of the container.
___

## Divider

The `Divider` is useful for clearly separating different components in a panel:

```python
text = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation 
ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt
mollit anim id est laborum.
"""

pn.Column(
    '# Lorem Ipsum',
    pn.layout.Divider(),
    text,
    styles=dict(background='whitesmoke'),
    width=400,
)
```

If we enable responsive sizing on the container (or globally) the `Divider` will automatically span the full width:

```python
pn.config.sizing_mode='stretch_width'

pn.Column(
    '## Slider',
    pn.layout.Divider(margin=(-20, 0, 0, 0)),
    pn.Row(
        pnw.FloatSlider(label='Float'), pnw.IntSlider(label='Int'),
        pnw.RangeSlider(label='Range'), pnw.IntRangeSlider(label='Int Range')
    ),
    '## Input',
    pn.layout.Divider(margin=(-20, 0, 0, 0)),
    pn.Row(
        pnw.TextInput(label='Text'), pnw.DatetimeInput(label='Date'),
        pnw.PasswordInput(label='Password'), pnw.Spinner(label='Number')
    )
)
```

---
