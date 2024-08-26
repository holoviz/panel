# Create Panes with ReactiveHTML

In this guide we will show you how to efficiently implement `ReactiveHTML` panes to display Python objects.

## Creating a ChartJS Pane

This example will show you the basics of creating a [ChartJS](https://www.chartjs.org/docs/latest/) pane.

```{pyodide}
import panel as pn
import param

from panel.custom import PaneBase, ReactiveHTML

class ChatJSComponent(ReactiveHTML):

    object = param.Dict()

    _template = """
    <div style="width: 100%; height:100%"><canvas id="canvas_el"></canvas></div>
    """

    _scripts = {
        "after_layout": "if (state.chart == null) { self.object() }",
        "remove": """
          state.chart.destroy();
          state.chart = null;
        """,
        "object": """
          if (state.chart) { self.remove() }
          state.chart = new Chart(canvas_el.getContext('2d'), data.object);
        """,
    }

    __javascript__ = [
        "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
    ]


def data(chart_type="line"):
    return {
        "type": chart_type,
        "data": {
            "labels": ["January", "February", "March", "April", "May", "June", "July"],
            "datasets": [
                {
                    "label": "Data",
                    "backgroundColor": "rgb(255, 99, 132)",
                    "borderColor": "rgb(255, 99, 132)",
                    "data": [0, 10, 5, 2, 20, 30, 45],
                }
            ],
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
        },
    }


chart_type = pn.widgets.RadioBoxGroup(
    name="Chart Type", options=["bar", "line"], inline=True
)
grid = ChatJSComponent(
    object=pn.bind(data, chart_type), height=400, sizing_mode="stretch_width"
)
pn.Column(chart_type, grid).servable()
```

Note that the chart is not created inside the `after_layout` callback since ChartJS requires the layout to be fully initialized before render. Dealing with layout issues like this sometimes requires a bit of iteration, if you get stuck, share your question and minimum, reproducible code example on [Discourse](https://discourse.holoviz.org/).

## Creating a Cytoscape Pane

This example will show you how to build a more advanced [CytoscapeJS](https://js.cytoscape.org/) pane.

```{pyodide}
import param
import panel as pn

from panel.custom import ReactiveHTML


class Cytoscape(ReactiveHTML):

    object = param.List()

    layout = param.Selector(default="cose", objects=["breadthfirst", "circle", "concentric", "cose", "grid", "preset", "random"])
    style = param.String("", doc="Use to set the styles of the nodes/edges")

    zoom = param.Number(1, bounds=(0,100))
    pan = param.Dict({"x": 0, "y": 0})

    data = param.List(doc="Use to send node's data/attributes to Cytoscape")

    selected_nodes = param.List()
    selected_edges = param.List()

    _template = '<div id="cy" style="width: 100%; height: 100%; position: relative; border: 1px solid"></div>'

    __javascript__ = ['https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.umd.js']

    _scripts = {
        "render": """
          if (state.cy == undefined) {
            state.cy = cytoscape({
              container: cy,
              layout: {name: data.layout},
              elements: data.object,
              zoom: data.zoom,
              pan: data.pan,
            });
            state.cy.on('select unselect', function (evt) {
              data.selected_nodes = state.cy.elements('node:selected').map(el => el.id())
              data.selected_edges = state.cy.elements('edge:selected').map(el => el.id())
            });
            self.style()
            const mainEle = document.querySelector("body")
            mainEle.addEventListener("scrollend", (event) => {state.cy.resize().fit()})
          };
        """,
        "remove": """
          state.cy.destroy()
          delete state.cy
        """,
        "object": "state.cy.json({elements: data.object});state.cy.resize().fit()",
        "layout": "state.cy.layout({name: data.layout}).run()",
        "zoom": "state.cy.zoom(data.zoom)",
        "pan": "state.cy.pan(data.pan)",
        "style": "state.cy.style().resetToDefault().append(data.style).update()",
    }

    _extension_name = 'cytoscape'

pn.extension('cytoscape', sizing_mode='stretch_width')

elements =  [{"data":{"id":'A', "label":'A'}},{"data":{"id":'B', "label":'B'}}, {"data":{"id": "A-B", "source":'A', "target":'B'}}]
graph = Cytoscape(object=elements, sizing_mode="stretch_width", height=600)
pn.Row(
    pn.Param(graph, parameters=["object", "zoom", "pan", "layout", "style", "selected_nodes", "selected_edges"], sizing_mode="fixed", width=300),
    graph
).servable()
```

Please notice that we `resize` and `fit` the graph on `scrollend`. This is a *hack* needed to make the graph show up and fit nicely to the screen.

Hacks like these are sometimes needed and requires a bit of experience to find. If you get stuck share your question and minimum, reproducible code example on [Discourse](https://discourse.holoviz.org/).
