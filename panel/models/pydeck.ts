import { HTMLBox, HTMLBoxView } from "models/layouts/html_box"

import { div } from "core/dom"
import * as p from "core/properties"

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

        this.el.appendChild(div({
            style: {
                padding: '2px',
                color: '#b88d8e',
                backgroundColor: '#2a3153',
            },
        }, `${this.model.json_input}: ${this.model.mapbox_api_key} ${this.model.tooltip}`))
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
