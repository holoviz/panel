import { HTMLBox } from "@bokehjs/models/layouts/html_box"
import * as p from "@bokehjs/core/properties"
import { div } from "@bokehjs/core/dom"
import {ModelEvent, JSON} from "@bokehjs/core/bokeh_events"

import { PanelHTMLBoxView, set_size } from "./layout"


export class KeystrokeEvent extends ModelEvent {
  event_name: string = "keystroke"

  constructor(readonly key: string) {
    super()
  }

  protected _to_json(): JSON {
    return {model: this.origin, key: this.key}
  }
}

export class TerminalView extends PanelHTMLBoxView {
  model: Terminal
  term: any // Element
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
    this.term.loadAddon(this.webLinksAddon)

    this.term.open(this.container)

    this.term.onRender(() => {
      if (!this._rendered)
	this.fit()
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
    this.model.trigger_event(new KeystrokeEvent(value))
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
    this.term.clear()
  }

  fit(): void {
    const sizing = this.box_sizing()
    const vert_margin = sizing.margin == null ? 0 : sizing.margin.top + sizing.margin.bottom
    const horz_margin = sizing.margin == null ? 0 : sizing.margin.left + sizing.margin.right
    const width = (this.layout.inner_bbox.width || this.model.width || 0) - horz_margin
    const height = (this.layout.inner_bbox.height || this.model.height || 0) - vert_margin
    const renderer = this.term._core._renderService
    const cell_width = renderer.dimensions.actualCellWidth || 9
    const cell_height = renderer.dimensions.actualCellHeight || 18
    if (width == null || height == null || width <= 0 || height <= 0)
      return
    const cols = Math.max(2, Math.floor(width / cell_width))
    const rows = Math.max(1, Math.floor(height / cell_height))
    if (this.term.rows !== rows || this.term.cols !== cols)
      this.term.resize(cols, rows)
    this.model.ncols = cols
    this.model.nrows = rows
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
    ncols: p.Property<number>
    nrows: p.Property<number>
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

    this.define<Terminal.Props>(({Any, Int, String}) => ({
      _clears:        [ Int,     0 ],
      options:        [ Any,    {} ],
      output:         [ String,    ],
      ncols:          [ Int        ],
      nrows:          [ Int        ],
    }))
  }
}
