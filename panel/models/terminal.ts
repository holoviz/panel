// See https://docs.bokeh.org/en/latest/docs/reference/models/layouts.html
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

// See https://docs.bokeh.org/en/latest/docs/reference/core/properties.html
import * as p from "@bokehjs/core/properties"
import { div } from "@bokehjs/core/dom";

// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class TerminalView extends HTMLBoxView {
    model: Terminal
    term: any // Element

    connect_signals(): void {
        super.connect_signals()

        this.connect(this.model.properties.object.change, () => {
            this.term.write(this.model.object);
        })
    }

    render(): void {
        super.render()
        const container = div({id: "terminal-container"})

        const wn = (window as any)
        this.term = new wn.Terminal();
        this.term.open(container);
        this.term.write(this.model.object);
        this.el.appendChild(container)
    }
}

export namespace Terminal {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        object: p.Property<string>,
        out: p.Property<string>,
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

        this.define<Terminal.Props>(({String}) => ({
            object: [String, ],
            out: [String, ],
        }))
    }
}