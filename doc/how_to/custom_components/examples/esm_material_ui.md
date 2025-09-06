# Wrapping Material UI components

:::{note}
The `MaterialBase` component is defined before the call to `pn.extension` to allow us to load the `_extension_name` and thereby initialize the required JS and CSS resources. Ordinarily the component would be defined in an external module.
:::

```{pyodide}
import param
import panel as pn

from panel.custom import ReactComponent

class MaterialComponent(ReactComponent):

    _importmap = {
        "imports": {
            "@mui/material/": "https://esm.sh/@mui/material@5.16.7/",
        }
    }

pn.extension(template='material')
```

This example demonstrates how to wrap Material UI components using `ReactComponent`.

```{pyodide}

class Button(MaterialComponent):

    disabled = param.Boolean(default=False)

    label = param.String(default='')

    variant = param.Selector(objects=["contained", "outlined", "text"])

    _esm = """
    import Button from '@mui/material/Button';

    export function render({ model }) {
      const [label] = model.useState("label")
      const [variant] = model.useState("variant")
      const [disabled] = model.useState("disabled")
      return (
        <Button disabled={disabled} variant={variant}>{label || 'Click me!'}</Button>
      )
    }
    """

class Rating(MaterialComponent):

    value = param.Number(default=0, bounds=(0, 5))

    _esm = """
    import Rating from '@mui/material/Rating'

    export function render({model}) {
      const [value, setValue] = model.useState("value")
      return (
        <Rating
          value={value}
          onChange={(event, newValue) => setValue(newValue) }
        />
      )
    }
    """

class DiscreteSlider(MaterialComponent):

    marks = param.List(default=[
        {'value': 0, 'label': '0°C'},
        {'value': 20, 'label': '20°C'},
        {'value': 37, 'label': '37°C'},
        {'value': 100, 'label': '100°C'},
    ])

    value = param.Number(default=20)

    _esm = """
    import Box from '@mui/material/Box';
    import Slider from '@mui/material/Slider';

    export function render({ model }) {
      const [value, setValue] = model.useState("value")
      const [marks] = model.useState("marks")
      return (
        <Box sx={{ width: 300 }}>
          <Slider
            aria-label="Restricted values"
            defaultValue={value}
            marks={marks}
            onChange={(e) => setValue(e.target.value)}
            step={null}
            valueLabelDisplay="auto"
          />
        </Box>
      );
    }
    """

button = Button()
rating = Rating(value=3)
slider = DiscreteSlider()

pn.Row(
    pn.Column(button.controls(['disabled', 'label', 'variant']), button),
    pn.Column(rating.controls(['value']), rating),
    pn.Column(slider.controls(['value']), slider),
).servable()
```
