# Hvplot Explorer

```python
import io
import panel as pn
import panel_material_ui as pmui
import pandas as pd
import hvplot.pandas

pn.extension()
```

This example demonstrates how to leverage the hvPlot explorer functionality when combined with a FileInput widget to allow users to explore their own data. When a user uploads their own data it gets added to the list of datasets the user can select from.

```python
upload = pmui.FileInput(label='Upload file', height=50)
select = pmui.Select(options={
    'Penguins': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv',
    'Diamonds': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv',
    'Titanic': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv',
    'MPG': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv'
})

def add_data(event):
    b = io.BytesIO()
    upload.save(b)
    b.seek(0)
    name = '.'.join(upload.filename.split('.')[:-1])
    select.options[name] = b
    select.param.trigger('options')
    select.value = b
    
upload.param.watch(add_data, 'filename')

def explore(csv):
    df = pd.read_csv(csv)
    explorer = hvplot.explorer(df)
    def plot_code(**kwargs):
        code = f'```python\n{explorer.plot_code()}\n```'
        return pn.pane.Markdown(code, sizing_mode='stretch_width')
    return pn.Column(
        explorer,
        '**Code**:',
        pn.bind(plot_code, **explorer.param.objects())
    )

widgets = pn.Column(
    "Select an existing dataset or upload one of your own CSV files and start exploring your data.",
    pn.Row(
        select,
        upload,
    )
)

output = pn.panel(pn.bind(explore, select))

pn.Column(widgets, output)
```

## Served App

```python
if pn.state.served:
    pmui.Page(
        title="hvPlot Explorer",
        main=[widgets, output],
    ).servable()
```
