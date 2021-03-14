// See https://docs.bokeh.org/en/latest/docs/reference/models/layouts.html
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

// See https://docs.bokeh.org/en/latest/docs/reference/core/properties.html
import * as p from "@bokehjs/core/properties"

// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class ChartJSView extends HTMLBoxView {
    model: ChartJS
    objectElement: any // Element

    connect_signals(): void {
        super.connect_signals()

        this.connect(this.model.properties.object.change, () => {
            this.render();
        })
    }

    render(): void {
        super.render()
        this.el.innerHTML = `<button type="button">${this.model.object}</button>`
        this.objectElement = this.el.firstElementChild

        this.objectElement.addEventListener("click", () => {this.model.clicks+=1;}, false)
    }
}

export namespace ChartJS {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        object: p.Property<string>,
        clicks: p.Property<number>,
    }
}

export interface ChartJS extends ChartJS.Attrs { }

// The Bokeh .ts model corresponding to the Bokeh .py model
export class ChartJS extends HTMLBox {
    properties: ChartJS.Props

    constructor(attrs?: Partial<ChartJS.Attrs>) {
        super(attrs)
    }

    static __module__ = "panel.models.chartjs"

    static init_ChartJS(): void {
        this.prototype.default_view = ChartJSView;

        this.define<ChartJS.Props>(({Int, String}) => ({
            object: [String, "Click Me!"],
            clicks: [Int, 0],
        }))
    }
}