import { HTMLBox } from "@bokehjs/models/layouts/html_box"
import * as p from "@bokehjs/core/properties"
import { div } from "@bokehjs/core/dom";

import { PanelHTMLBoxView, set_size } from "./layout"


export class TerminalView extends PanelHTMLBoxView {
  model: Terminal
  term: any // Element
  fitAddon: any
  webLinksAddon: any

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
    const container = div({class: "terminal-container"})
    set_size(container, this.model)

    this.term = this.getNewTerminal()
    this.term.onData((value: any) => {this.handleOnData(value)});

    this.webLinksAddon = this.getNewWebLinksAddon()
    this.term.loadAddon(this.webLinksAddon);

    this.fitAddon = this.getNewFitAddon()
    this.term.loadAddon(this.fitAddon);

    this.term.open(container);

    this.write()
    this.el.appendChild(container)
  }

  getNewTerminal(): any {
    const wn = (window as any)
    if (wn.Terminal)
      return new wn.Terminal(this.model.options)
    else
      return new wn.xtermjs.Terminal(this.model.options)
  }

  getNewWebLinksAddon(): any {
    const wn = (window as any)
    if (wn.WebLinksAddon)
      return new wn.WebLinksAddon.WebLinksAddon()
    else
      return new wn.xtermjsweblinks.WebLinksAddon()
  }

  getNewFitAddon(): any {
    const wn = (window as any)
    if (wn.FitAddon)
      return new wn.FitAddon.FitAddon()
    else
      return new wn.xtermjsfit.FitAddon()
  }

  handleOnData(value: string): void {
    // Hack to handle repeating keyboard inputs
    if (this.model.input === value)
      this.model._value_repeats+=1
    else
      this.model.input = value;
  }

  write(): void {
    const text = this.model.output
    if (text == null || !text.length)
      return
    // https://stackoverflow.com/questions/65367607/how-to-handle-new-line-in-xterm-js-while-writing-data-into-the-terminal
    const cleaned = text.replace(/\r?\n/g, "\r\n")
    // var text = Array.from(cleaned, (x) => x.charCodeAt(0))
    this.term.write(cleaned)
  }

  clear(): void {
    // https://stackoverflow.com/questions/65367607/how-to-handle-new-line-in-xterm-js-while-writing-data-into-the-terminal
    this.term.clear()
  }

  fit(): void {
    this.fitAddon.fit()
  }

  after_layout(): void{
    super.after_layout()
    this.fit()
  }
}

export namespace Terminal {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    options: p.Property<any>
    output: p.Property<string>
    input: p.Property<string>
    _clears: p.Property<number>
    _value_repeats: p.Property<number>
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

    this.define<Terminal.Props>(({Any, Int, String}) => ({
      options:        [Any,    {} ],
      output:         [String,    ],
      input:          [String,    ],
      _clears:        [Int,     0 ],
      _value_repeats: [Int,     0 ],
    }))
  }
}
