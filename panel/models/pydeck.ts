import { HTMLBox, HTMLBoxView } from "models/layouts/html_box"

import { div } from "core/dom"
import * as p from "core/properties"

const createDeck = (window as any).createDeck;

export class PyDeckPlotView extends HTMLBoxView {
    model: PyDeckPlot

    connect_signals(): void {
        console.log("connect_signals")
        super.connect_signals()

        this.connect(this.model.properties.json_input.change, () => {
            this.render();
        })

        this.connect(this.model.properties.mapbox_api_key.change, () => {
            this.render();
        })

        this.connect(this.model.properties.tooltip.change, () => {
            this.render();
        })
    }

    render(): void {
        super.render()

        if (!(window as any).createDeck) { return }

        const container = this.el.appendChild(div({ class: "deck_gl", style: { height: "400px", width: "800px" } }));

        const jsonInput = JSON.parse(this.model.json_input);
        const MAPBOX_API_KEY = this.model.mapbox_api_key;
        const tooltip = this.model.tooltip;

        createDeck({
            mapboxApiKey: MAPBOX_API_KEY,
            container: container,
            jsonInput,
            tooltip
        });
    }
}

export namespace PyDeckPlot {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        json_input: p.Property<string>
        mapbox_api_key: p.Property<string>
        tooltip: p.Property<boolean>
    }
}

export interface PyDeckPlot extends PyDeckPlot.Attrs { }

export class PyDeckPlot extends HTMLBox {
    properties: PyDeckPlot.Props

    constructor(attrs?: Partial<PyDeckPlot.Attrs>) {
        super(attrs)
    }

    static init_PyDeckPlot(): void {
        this.prototype.default_view = PyDeckPlotView;

        this.define<PyDeckPlot.Props>({
            json_input: [p.String],
            mapbox_api_key: [p.String],
            tooltip: [p.Boolean]
        })
    }
}
