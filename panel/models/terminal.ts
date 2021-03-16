// See https://docs.bokeh.org/en/latest/docs/reference/models/layouts.html
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

// See https://docs.bokeh.org/en/latest/docs/reference/core/properties.html
import * as p from "@bokehjs/core/properties"
import { div } from "@bokeh/bokehjs/build/js/types/core/dom"

// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class TerminalView extends HTMLBoxView {
    model: Terminal
    terminal: any // Element

    connect_signals(): void {
        super.connect_signals()

        this.connect(this.model.properties.object.change, () => {
            this.render();
        })
    }

    render(): void {
        super.render()
        const container = div({id: "terminal-container"})

        const wn = (window as any)
        wn.Terminal.applyAddon(wn.fullscreen)
        wn.Terminal.applyAddon(wn.fit)
        wn.Terminal.applyAddon(wn.webLinks)
        wn.Terminal.applyAddon(wn.search)
        const term = new wn.Terminal({
                cursorBlink: true,
                macOptionIsMeta: true,
                scrollback: true,
            });
        term.open(container);
        term.fit()
        term.resize(15, 50)
        console.log(`size: ${term.cols} columns, ${term.rows} rows`)
        // term.toggleFullScreen(true)
        term.fit()
        term.write("Welcome to pyxterm.js!\nhttps://github.com/cs01/pyxterm.js\n")
        // term.on('key', (key, ev) => {
        //     console.log("pressed key", key)
        //     console.log("event", ev)
        //     socket.emit("pty-input", {"input": key})
        // });

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