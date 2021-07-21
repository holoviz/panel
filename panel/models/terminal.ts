import { HTMLBox } from "@bokehjs/models/layouts/html_box"
import * as p from "@bokehjs/core/properties"
import { div } from "@bokehjs/core/dom";

import { PanelHTMLBoxView, set_size } from "./layout"


export class TerminalView extends PanelHTMLBoxView {
  model: Terminal
  term: any // Element
  fitAddon: any
  webLinksAddon: any
  container: HTMLDivElement
  _rendered: boolean

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.output.change, this.write)
    this.connect(this.model.properties._clears.change, this.clear)
  }

  render(): void {
    super.render()
    this.container = div({class: "terminal-container"})
    set_size(this.container, this.model)

    this.term = this.getNewTerminal()
    this.term.onData((value: any) => {
      this.handleOnData(value)
    });

    this.webLinksAddon = this.getNewWebLinksAddon()
    this.term.loadAddon(this.webLinksAddon);

    this.term.open(this.container)

    this.term.onRender(() => {
      if (!this._rendered) {
	this.fit()
      }
    })

    this.write()

    this.el.appendChild(this.container)
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
    return new wn.WebLinksAddon.WebLinksAddon()
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
    const width = this.layout.inner_bbox.width
    const height = this.layout.inner_bbox.height
    const renderer = this.term._core._renderService
    const cell_width = renderer.dimensions.actualCellWidth
    const cell_height = renderer.dimensions.actualCellHeight
    if (cell_width === 0 || cell_height === 0)
      return
    const cols = Math.max(2, Math.floor(width / cell_width))
    const rows = Math.max(1, Math.floor(height / cell_height))
    if (this.term.rows !== rows || this.term.cols !== cols) {
      renderer.clear();
      this.term.resize(cols, rows)
    }
    this._rendered = true
  }

  after_layout(): void {
    super.after_layout()
    this.fit()
  }

  resize_layout(): void {
    super.resize_layout()
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
