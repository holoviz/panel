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
    fitAddon: any

    connect_signals(): void {
        super.connect_signals()

        this.connect(this.model.properties.output.change, this.write)
        this.connect(this.model.properties._clears.change, this.clear)

        this.connect(this.model.properties.height.change, this.fit)
        this.connect(this.model.properties.width.change, this.fit)
        this.connect(this.model.properties.height_policy.change, this.fit)
        this.connect(this.model.properties.width_policy.change, this.fit)
        this.connect(this.model.properties.sizing_mode.change, this.fit)
    }

    render(): void {
        super.render()
        const container = div({id: "terminal-container"})

        const wn = (window as any)
        this.term = new wn.Terminal();
        this.term.loadAddon(new wn.WebLinksAddon.WebLinksAddon());
        this.fitAddon = new wn.FitAddon.FitAddon()
        this.term.loadAddon(this.fitAddon);
        this.term.open(container);
        this.write()
        this.el.appendChild(container)
        this.fit()
    }

    write(): void {
        // https://stackoverflow.com/questions/65367607/how-to-handle-new-line-in-xterm-js-while-writing-data-into-the-terminal
        const cleaned = this.model.output.replace(/\r?\n/g, "\r\n")
        this.term.write(cleaned);
    }
    clear(): void {
        // https://stackoverflow.com/questions/65367607/how-to-handle-new-line-in-xterm-js-while-writing-data-into-the-terminal
        this.term.clear()
    }

    fit(): void {
        console.log("fit")
        this.fitAddon.fit()

        // .fit does not adjust the height. bug?
        // Todo: improve this calculation including finding the fontCharWidth somewhere.
        var height = this.model.height
        if (height==null || height<=0){
            height = this.el.getBoundingClientRect().height
        }
        const fontCharWidth = 16
        const rows = Math.floor(height/fontCharWidth)
        this.term.resize(this.term.cols, rows)
    }

    after_layout(): void{
        super.after_layout()
        this.fit()
    }
}

export namespace Terminal {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        output: p.Property<string>,
        input: p.Property<string>,
        _clears: p.Property<number>
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
            output: [String, ],
            input: [String, ],
            _clears: [Int, 0]
        }))
    }
}