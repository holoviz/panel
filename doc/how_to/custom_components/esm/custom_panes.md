# Create Panes with ReactiveHTML

In this guide we will show you how to efficiently implement custom panes using `JSComponent`, `ReactComponent` and `AnyWidgetComponent` to get input from the user.

## Creating a ChartJS Pane

This example will show you the basics of creating a [ChartJS](https://www.chartjs.org/docs/latest/) pane.

::::{tab-set}

:::{tab-item} `JSComponent`
```{pyodide}
import panel as pn
import param
from panel.custom import JSComponent


class ChartJSComponent(JSComponent):
    object = param.Dict()

    _esm = """
import { Chart } from "https://esm.sh/chart.js/auto"

export function render({ model, el }) {
  const canvasEl = document.createElement('canvas')
  // Add DOM node before creating the chart
  el.append(canvasEl)
  const create_chart = () => new Chart(canvasEl.getContext('2d'), model.object)
  let chart = create_chart()
  model.on("object", () => {
     chart.destroy()
     chart = create_chart()
   })
  model.on('remove', () => chart.destroy());
}
"""


def plot(chart_type="line"):
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
    object=pn.bind(plot, chart_type), height=400, sizing_mode="stretch_width"
)
pn.Column(chart_type, chart).servable()
```

Note how we had to add the `canvasEl` to the `el` before we could render the chart. Some libraries will require the element to be attached to the DOM before we could render it. Dealing with layout issues like this sometimes requires a bit of iteration. If you get stuck, share your question and minimum, reproducible code example on [Discourse](https://discourse.holoviz.org/).
:::

:::{tab-item} `ReactComponent`
```{pyodide}
import panel as pn
import param

from panel.custom import ReactComponent


class ChartReactComponent(ReactComponent):

    object = param.Dict()

    _esm = """
import { Chart } from 'https://esm.sh/react-chartjs-2@4.3.1';
import { Chart as ChartJS, registerables } from "https://esm.sh/chart.js@3.9.1";

ChartJS.register(...registerables);

export function render({ model }) {
  const [plot] = model.useState('object')
  return <Chart {...plot}></Chart>
};
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
chart = ChartReactComponent(
    object=pn.bind(data, chart_type), height=600, sizing_mode="stretch_width"
)
pn.Column(chart_type, chart).servable()
```
:::

::: {tab-item} `AnyWidgetComponent`
```{pyodide}
import panel as pn
import param
from panel.custom import AnyWidgetComponent


class AnyWidgetComponent(AnyWidgetComponent):
    object = param.Dict()

    _esm = """
import { Chart } from "https://esm.sh/chart.js/auto"

function render({ model, el }) {
  const canvasEl = document.createElement('canvas')
  // Add DOM node before creating the chart
  el.append(canvasEl)
  const create_chart = () => new Chart(canvasEl.getContext('2d'), model.object)
  let chart = create_chart()
  model.on("object", () => {
     chart.destroy()
     chart = create_chart()
   })
}

export default { render };
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
chart = AnyWidgetComponent(
    object=pn.bind(data, chart_type), height=400, sizing_mode="stretch_width"
)
pn.Column(chart_type, chart).servable()
```

Note, again, that we have to append the `canvasEl` to the `el` before we create the chart.
:::

::::

## Creating a Cytoscape Pane

This example will show you how to build a more advanced [CytoscapeJS](https://js.cytoscape.org/) pane.

::::{tab-set}

:::{tab-item} `JSComponent`
```{pyodide}
import param
import panel as pn

from panel.custom import JSComponent


class CytoscapeJS(JSComponent):

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


pn.extension(sizing_mode="stretch_width")

elements = [
    {"data": {"id": "A", "label": "A"}},
    {"data": {"id": "B", "label": "B"}},
    {"data": {"id": "A-B", "source": "A", "target": "B"}},
]
graph = CytoscapeJS(
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
:::

:::{tab-item} `ReactComponent`
```{pyodide}
import param
import panel as pn

from panel.custom import ReactComponent


class CytoscapeReact(ReactComponent):

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
import CytoscapeComponent from 'https://esm.sh/react-cytoscapejs';

export function render({ model }) {
  function configure(cy){
    cy.on('select unselect', function (evt) {
      model.selected_nodes = cy.elements('node:selected').map(el => el.id())
      model.selected_edges = cy.elements('edge:selected').map(el => el.id())
    });
  }


  const [layout] = model.useState('layout')
  const [object] = model.useState('object')
  const [pan] = model.useState('pan')
  const [style] = model.useState('style')
  const [zoom] = model.useState('zoom')

  return (
    <CytoscapeComponent
        elements={object}
        //layout={ { 'name': layout} }
        zoom={zoom}
        pan={pan}
        stylesheet={style}
        style={{ width: '100%', height: model.height, position: 'relative' }}
        cy={configure}
    />
  );
}
"""

pn.extension(sizing_mode="stretch_width")

elements = [
    {"data": {"id": "A", "label": "A"}},
    {"data": {"id": "B", "label": "B"}},
    {"data": {"id": "A-B", "source": "A", "target": "B"}},
]
graph = CytoscapeReact(
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
            "height",
        ],
        sizing_mode="fixed",
        width=300,
    ),
    graph,
).servable()
```
:::

:::{tab-item} `AnyWidgetComponent`
```{pyodide}
import param
import panel as pn

from panel.custom import AnyWidgetComponent


class CytoscapeAnyWidget(AnyWidgetComponent):

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

function render({ model, el }) {
    removeCy();

    cy = cytoscape({
        container: el,
        layout: {name: model.get('layout')},
        elements: model.get('object'),
        zoom: model.get('zoom'),
        pan: model.get('pan')
    })
    cy.style().resetToDefault().append(model.get('style')).update()
    cy.on('select unselect', function (evt) {
        model.set("selected_nodes", cy.elements('node:selected').map(el => el.id()))
        model.set("selected_edges", cy.elements('edge:selected').map(el => el.id()))
        model.save_changes()
    });

    model.on('change:object', () => {cy.json({elements: model.get('object')});cy.resize().fit()})
    model.on('change:layout', () => {cy.layout({name: model.get('layout')}).run()})
    model.on('change:zoom', () => {cy.zoom(model.get('zoom'))})
    model.on('change:pan', () => {cy.pan(model.get('pan'))})
    model.on('change:style', () => {cy.style().resetToDefault().append(model.get('style')).update()})

    window.addEventListener('resize', function(event){
        cy.center();
        cy.resize().fit();
    });
}

export default { render };
"""
    _stylesheets=["""
.__________cytoscape_container {
    position: relative;
}
"""]


pn.extension("cytoscape", sizing_mode="stretch_width")

elements = [
    {"data": {"id": "A", "label": "A"}},
    {"data": {"id": "B", "label": "B"}},
    {"data": {"id": "A-B", "source": "A", "target": "B"}},
]
graph = CytoscapeAnyWidget(
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
:::

::::
