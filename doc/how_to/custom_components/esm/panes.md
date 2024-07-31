# Create Panes with ReactiveHTML

In this guide we will show you how to efficiently implement custom panes using `JSComponent`, `ReactComponent` and `AnyWidgetComponent` to get input from the user.

## Creating a ChartJS Pane

This example will show you the basics of creating a [ChartJS](https://www.chartjs.org/docs/latest/) pane.

```{pyodide}
import panel as pn
import param
from panel.custom import JSComponent


class ChartJSComponent(JSComponent):
    object = param.Dict()

    _esm = """
import { Chart } from "https://esm.sh/chart.js/auto"

let chart = null;

function createChart(canvasEl, model) {
    removeChart();
    chart = new Chart(canvasEl.getContext('2d'), model.object);
}

function removeChart() {
    if (chart) {
        chart.destroy();
    }
}

export function render({ model }) {
    const canvasEl = document.createElement('canvas');
    // The chart will not render before after the layout has been created
    model.on('after_render', () => createChart(canvasEl, model))

    const updateChart = () => createChart(canvasEl, model);
    model.on('object', updateChart);
    model.on('remove', removeChart);
    return canvasEl;
}
"""


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
chart = ChartJSComponent(
    object=pn.bind(data, chart_type), height=400, sizing_mode="stretch_width"
)
pn.Column(chart_type, chart).servable()
```

Note the use of the `model.on('after_render', ...)` to postpone the rendering of the chart to after the rendering of the element. Dealing with layout issues like this sometimes requires a bit of iteration. If you get stuck, share your question and minimum, reproducible code example on [Discourse](https://discourse.holoviz.org/).

## Creating a Cytoscape Pane

This example will show you how to build a more advanced [CytoscapeJS](https://js.cytoscape.org/) pane.

```{pyodide}
import param
import panel as pn

from panel.custom import JSComponent


class Cytoscape(JSComponent):

    object = param.List()

    layout = param.Selector(
        default="cose",
        objects=[
            "breadthfirst",
            "circle",
            "concentric",
            "cose",
            "grid",
            "preset",
            "random",
        ],
    )
    style = param.String("", doc="Use to set the styles of the nodes/edges")

    zoom = param.Number(1, bounds=(1, 100))
    pan = param.Dict({"x": 0, "y": 0})

    data = param.List(doc="Use to send node's data/attributes to Cytoscape")

    selected_nodes = param.List()
    selected_edges = param.List()

    _esm = """
import { default as cytoscape} from "https://esm.sh/cytoscape"
let cy = null;

function removeCy() {
    if (cy) { cy.destroy() }
}

export function render({ model }) {
    removeCy();

    const div = document.createElement('div');
    div.style.width = "100%";
    div.style.height = "100%";
    // Cytoscape raises warning of position is static
    div.style.position = "relative";

    model.on('after_render', () => {
        cy = cytoscape({
            container: div,
            layout: {name: model.layout},
            elements: model.object,
            zoom: model.zoom,
            pan: model.pan
        })
        cy.style().resetToDefault().append(model.style).update()
        cy.on('select unselect', function (evt) {
            model.selected_nodes = cy.elements('node:selected').map(el => el.id())
            model.selected_edges = cy.elements('edge:selected').map(el => el.id())
        });

        model.on('object', () => {cy.json({elements: model.object});cy.resize().fit()})
        model.on('layout', () => {cy.layout({name: model.layout}).run()})
        model.on('zoom', () => {cy.zoom(model.zoom)})
        model.on('pan', () => {cy.pan(model.pan)})
        model.on('style', () => {cy.style().resetToDefault().append(model.style).update()})

        window.addEventListener('resize', function(event){
            cy.center();
            cy.resize().fit();
        });
        model.on('remove', removeCy)
    })

    return div
}
"""


pn.extension("cytoscape", sizing_mode="stretch_width")

elements = [
    {"data": {"id": "A", "label": "A"}},
    {"data": {"id": "B", "label": "B"}},
    {"data": {"id": "A-B", "source": "A", "target": "B"}},
]
graph = Cytoscape(
    object=elements,
    sizing_mode="stretch_width",
    height=600,
    styles={"border": "1px solid black"},
)
pn.Row(
    pn.Param(
        graph,
        parameters=[
            "object",
            "zoom",
            "pan",
            "layout",
            "style",
            "selected_nodes",
            "selected_edges",
        ],
        sizing_mode="fixed",
        width=300,
    ),
    graph,
).servable()
```
