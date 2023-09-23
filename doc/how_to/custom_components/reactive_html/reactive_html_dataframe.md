# DataFrames and ReactiveHTML

In this guide you will learn how to efficiently implement `ReactiveHTML` components with a
`DataFrame` parameter.

## Creating a Table Pane

In this example we will show you how to create a custom Table Pane. The example will be based on
the [GridJS table](https://gridjs.io/).

```{pyodide}
import random
import pandas as pd
import param
import panel as pn


class GridJSComponent(pn.reactive.ReactiveHTML):
    value = param.DataFrame()
    _template = '<div id="wrapper" styles="height:100%;width:100%;"></div>'
    _scripts = {
      "render": """
console.log(data.value)
state.config= ()=>{
  const columns = Object.keys(data.value).filter(key => key !== "index");
  var rows= []
  for (let index=0;index<data.value["index"].shape[0];index++){
    const row=columns.map((key)=>{
      return data.value[key][index]
    })
    rows.push(row)
  }
  return {columns: columns, data: rows, resizable: true, sort: true }
}
config = state.config()
console.log(config)
state.grid = new gridjs.Grid(config).render(wrapper);
""", "value": """
config = state.config()
state.grid.updateConfig(config).forceRender()
"""
    }
    __css__ = [
      "https://unpkg.com/gridjs/dist/theme/mermaid.min.css"
    ]
    __javascript__ = [
      "https://unpkg.com/gridjs/dist/gridjs.umd.js"
    ]

def data(event):
  return pd.DataFrame([
    ["John", "john@example.com", "(353) 01 222 3333", random.uniform(0, 1)],
    ["Mark", "mark@gmail.com", "(01) 22 888 4444", random.uniform(0, 1)],
    ["Eoin", "eoin@gmail.com", "0097 22 654 00033", random.uniform(0, 1)],
    ["Sarah", "sarahcdd@gmail.com", "+322 876 1233", random.uniform(0, 1)],
    ["Afshin", "afshin@mail.com", "(353) 22 87 8356", random.uniform(0, 1)]
  ],
    columns= ["Name", "Email", "Phone Number", "Random"]
  )
update_button = pn.widgets.Button(name="UPDATE", button_type="primary")
grid = GridJSComponent(value=pn.bind(data, update_button), sizing_mode="stretch_width")
pn.Column(update_button, grid).servable()
```

If you look in the *browser console* you can see the *DataFrame* `data.value` and transformed `config` values.

![DataFrame in the console](../../../_static/reactive-html-dataframe-in-console.png)
