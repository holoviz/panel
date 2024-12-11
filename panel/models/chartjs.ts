// See https://docs.bokeh.org/en/latest/docs/reference/models/layouts.html
import { HTMLBox, HTMLBoxView } from "./layout"
import {div} from "@bokehjs/core/dom"

// See https://docs.bokeh.org/en/latest/docs/reference/core/properties.html
import * as p from "@bokehjs/core/properties"

// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class ChartJSView extends HTMLBoxView {
    declare model: ChartJS
    container: Element
    objectElement: any // Element

    override connect_signals(): void {
        super.connect_signals()

        this.on_change(this.model.properties.object, () => {
            this.render();
        })
    }

    override render(): void {
        super.render()
        this.container = div({style: {height: "100%", width: "100%"}})
        this.container.innerHTML = `<button type="button">${this.model.object}</button>`
        this.objectElement = this.container.firstElementChild
        this.objectElement.addEventListener("click", () => {this.model.clicks+=1;}, false)
        this.shadow_el.append(this.container)
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
    declare properties: ChartJS.Props

    constructor(attrs?: Partial<ChartJS.Attrs>) {
        super(attrs)
    }

    static override __module__ = "panel.models.chartjs"

    static {
        this.prototype.default_view = ChartJSView;

        this.define<ChartJS.Props>(({Int, String}) => ({
            object: [String, "Click Me!"],
            clicks: [Int, 0],
        }))
    }
}
