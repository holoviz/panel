# DataFrames and ReactiveHTML

In this guide you will learn how to efficiently implement `ReactiveHTML` components with a
`DataFrame` parameter.

## Creating a Table Pane

In this example we will shop you how to create a custom Table Pane. The example will be based on the [GridJS table](https://gridjs.io/).

```{pyodide}
import panel as pn
import param
import pandas as pd

class GridJSComponent(pn.reactive.ReactiveHTML):
    value = param.DataFrame()
    _template = '<div id="wrapper" styles="height:100%;width:100%;"></div>'
    _scripts = {
      "render": """
console.log(data.value)
const columns = Object.keys(data.value).filter(key => key !== "index");
var rows= []
for (let index=0;index<data.value["index"].shape[0];index++){
  const row=columns.map((key)=>{
    return data.value[key][index]
  })
  rows.push(row)
}
new gridjs.Grid({columns: columns, data: rows }).render(wrapper);
"""
    }
    __css__ = [
      "https://unpkg.com/gridjs/dist/theme/mermaid.min.css"
    ]
    __javascript__ = [
      "https://unpkg.com/gridjs/dist/gridjs.umd.js"
    ]

data=pd.DataFrame([
  ["John", "john@example.com", "(353) 01 222 3333"],
  ["Mark", "mark@gmail.com", "(01) 22 888 4444"],
  ["Eoin", "eoin@gmail.com", "0097 22 654 00033"],
  ["Sarah", "sarahcdd@gmail.com", "+322 876 1233"],
  ["Afshin", "afshin@mail.com", "(353) 22 87 8356"]
],
  columns= ["Name", "Email", "Phone Number"]
)
GridJSComponent(value=data, width=600).servable()
```

If you look in the *browser console* you will see the `data.value`

![DataFrame in the console](../../../_static/reactive-html-dataframe-in-console.png)

# Todo: Figure out if we should make this example more complete
# Todo: Figure out how to explain what `data.value` is and how to efficiently transform it
