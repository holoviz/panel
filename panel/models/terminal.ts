// See https://docs.bokeh.org/en/latest/docs/reference/models/layouts.html
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

// See https://docs.bokeh.org/en/latest/docs/reference/core/properties.html
import * as p from "@bokehjs/core/properties"

// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class TerminalView extends HTMLBoxView {
    model: Terminal
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

export namespace Terminal {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        object: p.Property<string>,
        clicks: p.Property<number>,
    }
}

export interface Terminal extends Terminal.Attrs { }

// The Bokeh .ts model corresponding to the Bokeh .py model
export class Terminal extends HTMLBox {
    properties: Terminal.Props

    constructor(attrs?: Partial<Terminal.Attrs>) {
        super(attrs)
    }

    static __module__ = "panel.models.terminal"

    static init_Terminal(): void {
        this.prototype.default_view = TerminalView;

        this.define<Terminal.Props>(({Int, String}) => ({
            object: [String, "Click Me!"],
            clicks: [Int, 0],
        }))
    }
}