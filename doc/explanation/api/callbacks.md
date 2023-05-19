# Callbacks

The callback API in Panel is the lowest-level approach, affording the greatest amount of flexibility but also quickly growing in complexity because each new interactive behavior requires additional callbacks that can interact in complex ways. Nonetheless, callbacks are important to know about, and can often be used to complement the other approaches. For instance, one specific callback could be used in addition to the more reactive approaches the other APIs provide.

For more details on defining callbacks see the [linking how-to guides](../how_to/links/index.md).

## Pros:

+ Complete and modular control over specific events

## Cons:

- Complexity grows very quickly with the number of callbacks
- If you have interactive plots, you need to handle initializing them separately

## Example

In this approach we once again define the widgets. Unlike in other approaches we then have to define the actual layout up front, to ensure that the callback we define has something that it can update or replace. In this case we use a single callback to update the plot, but in many cases multiple callbacks might be required.

```{pyodide}
import hvplot.pandas
import panel as pn

from bokeh.sampledata.autompg import autompg

columns = list(autompg.columns[:-2])

x = pn.widgets.Select(value='mpg', options=columns, name='x')
y = pn.widgets.Select(value='hp', options=columns, name='y')
color = pn.widgets.ColorPicker(name='Color', value='#880588')

layout = pn.Row(
    pn.Column('## MPG Explorer', x, y, color),
    autompg.hvplot.scatter(x.value, y.value, c=color.value, padding=0.1)
)

def update(event):
    layout[1].object = autompg.hvplot.scatter(x.value, y.value, c=color.value, padding=0.1)

x.param.watch(update, 'value')
y.param.watch(update, 'value')
color.param.watch(update, 'value')

layout
```
