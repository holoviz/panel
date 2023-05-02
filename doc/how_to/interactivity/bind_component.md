# Binding on components

## Binding the parameters on components

The power to binding parameters to components is being used behind the scene for all of panels widgets, which make it easy to create powerful components.

Below is an [Tabulator](https://panel.holoviz.org/reference/widgets/Tabulator.html) widget where the `page_size` is bound to the slider used in the previous example.


```python
import pandas as pd

pn.extension('tabulator')

df = pd.read_csv("https://datasets.holoviz.org/penguins/v1/penguins.csv")

pn.widgets.Tabulator(df, page_size=slider, pagination="remote")
```
