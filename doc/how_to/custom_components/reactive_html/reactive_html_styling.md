# Style your ReactiveHTML template

In this guide we will show you how to style your `ReactiveHTML` `_template` using the `_stylesheets` attribute and CSS.

If you are not familiar with CSS then the [W3 CSS School](https://www.w3schools.com/css/default.asp)
is a good resource to learn from. You can also ask ChatGPT for help. It can often provide you with
an HTML and CSS starting point that you can fine tune.

## A Layout with CSS Styling

```{pyodide}
import param
import panel as pn
from panel.reactive import ReactiveHTML

pn.extension()

class SensorLayout(ReactiveHTML):
    object = param.Parameter()

    _ignored_refs = ("object",)

    _template = """
    <div class="pn-container styled-container">
        <h1 id="name">Temperature</h1>
        <h2 id="subtitle">A measurement from the sensor</h1>
        <div id="object" class="styled-object">${object}</div>
    </div>
"""

    _stylesheets = ["""
        .pn-container {height: 100%;width: calc(100% - 20px); margin:10px;}
        .styled-container {border-radius: 10px;border: 2px solid gray;text-align: center; padding:10px;}
        .styled-object {display: inline-block;}
    """]

dial = pn.widgets.Dial(
    name="°C", value=37, format="{value}", colors=[(0.40, "green"), (1, "red")], bounds=(0, 100),
)
SensorLayout(
    object=dial, name="Temperature",
    styles={"border": "2px solid lightgray"},
).servable()
```

Note the difference between `styles` and `_stylesheets`.

- `styles` styles the outer HTML element wrapping the component
- `_stylesheets` styles the HTML elements inside the component
