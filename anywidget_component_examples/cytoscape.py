"""Cytoscape graph visualization pane using CDN library."""
import param
import panel as pn
from panel.custom import AnyWidgetComponent

class CytoscapeAnyWidget(AnyWidgetComponent):
    object = param.List()

    layout = param.Selector(
        default="cose",
        objects=[
            "breadthfirst", "circle", "concentric", "cose",
            "grid", "preset", "random",
        ],
    )
    style = param.String("", doc="Use to set the styles of the nodes/edges")
    zoom = param.Number(1, bounds=(1, 100))
    pan = param.Dict({"x": 0, "y": 0})
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

    _stylesheets = ["""
.__________cytoscape_container {
    position: relative;
}
"""]

component = CytoscapeAnyWidget(
    object=[
        {"data": {"id": "A", "label": "A"}},
        {"data": {"id": "B", "label": "B"}},
        {"data": {"id": "A-B", "source": "A", "target": "B"}},
    ],
    sizing_mode="stretch_width",
    height=400,
    styles={"border": "1px solid black"},
)
