import {HTMLBox, HTMLBoxView} from "./layout"
import {build_view} from "@bokehjs/core/build_views"
import {Plot} from "@bokehjs/models/plots"
import {Line, Step, VArea, VBar} from "@bokehjs/models/glyphs"
import type * as p from "@bokehjs/core/properties"
import {div} from "@bokehjs/core/dom"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source"
import {BasicTickFormatter, NumeralTickFormatter, TickFormatter} from "@bokehjs/models/formatters"

const red: string = "#d9534f"
const green: string = "#5cb85c"
const blue: string = "#428bca"

export class TrendIndicatorView extends HTMLBoxView {
  declare model: TrendIndicator

  containerDiv: HTMLDivElement
  textDiv: HTMLDivElement
  titleDiv: HTMLDivElement
  valueDiv: HTMLDivElement
  value2Div: HTMLDivElement
  changeDiv: HTMLElement
  plotDiv: HTMLDivElement
  plot: Plot
  _value_format: string
  _value_change_format: string

  override initialize(): void {
    super.initialize()
    this.containerDiv = div({style: {height: "100%", width: "100%"}})
    this.titleDiv = div({style: {font_size: "1em", word_wrap: "break-word"}})
    this.valueDiv = div({style: {font_size: "2em"}})
    this.value2Div = div({style: {font_size: "1em", opacity: "0.5", display: "inline"}})
    this.changeDiv = div({style: {font_size: "1em", opacity: "0.5", display: "inline"}})
    this.textDiv = div({}, this.titleDiv, this.valueDiv, div({}, this.changeDiv, this.value2Div))

    this.updateTitle()
    this.updateValue()
    this.updateValue2()
    this.updateValueChange()
    this.updateTextFontSize()

    this.plotDiv = div({})
    this.containerDiv = div({style: {height: "100%", width: "100%"}}, this.textDiv, this.plotDiv)
    this.updateLayout()
  }

  override connect_signals(): void {
    super.connect_signals()

    const {
      pos_color, neg_color, plot_color, plot_type, width,
      height, sizing_mode, title, value, value_change, layout,
    } = this.model.properties

    this.on_change([pos_color, neg_color], () => this.updateValueChange())
    this.on_change([plot_color, plot_type, width, height, sizing_mode], () => this.rerender_())
    this.on_change(title, () => this.updateTitle(true))
    this.on_change(value, () => this.updateValue(true))
    this.on_change(value_change, () => this.updateValue2(true))
    this.on_change(layout, () => this.updateLayout())
  }

  override async render(): Promise<void> {
    super.render()
    this.shadow_el.appendChild(this.containerDiv)
    await this.setPlot()
  }

  private async setPlot() {
    this.plot = new Plot({
      background_fill_color: null,
      border_fill_color: null,
      outline_line_color: null,
      min_border: 0,
      sizing_mode: "stretch_both",
      toolbar_location: null,
    })

    const source = this.model.source
    if (this.model.plot_type === "line") {
      const line = new Line({
        x: {field: this.model.plot_x},
        y: {field: this.model.plot_y},
        line_width: 4,
        line_color: this.model.plot_color,
      })
      this.plot.add_glyph(line, source)
    } else if (this.model.plot_type === "step") {
      const step = new Step({
        x: {field: this.model.plot_x},
        y: {field: this.model.plot_y},
        line_width: 3,
        line_color: this.model.plot_color,
      })
      this.plot.add_glyph(step, source)
    } else if (this.model.plot_type === "area") {
      const varea = new VArea({
        x: {field: this.model.plot_x},
        y1: {field: this.model.plot_y},
        y2: 0,
        fill_color: this.model.plot_color,
        fill_alpha: 0.5,
      })
      this.plot.add_glyph(varea, source)
      const line = new Line({
        x: {field: this.model.plot_x},
        y: {field: this.model.plot_y},
        line_width: 3,
        line_color: this.model.plot_color,
      })
      this.plot.add_glyph(line, source)
    } else {
      const vbar = new VBar({
        x: {field: this.model.plot_x},
        top: {field: this.model.plot_y},
        width: 0.9,
        line_color: null,
        fill_color: this.model.plot_color,
      })
      this.plot.add_glyph(vbar, source)
    }

    const view = await build_view(this.plot)
    this.plotDiv.innerHTML = ""
    view.render_to(this.plotDiv)
  }

  override after_layout(): void {
    super.after_layout()
    this.updateTextFontSize()
  }

  updateTextFontSize(): void {
    this.updateTextFontSizeColumn()
  }

  updateTextFontSizeColumn(): void {
    let elWidth = this.containerDiv.clientWidth
    let elHeight = this.containerDiv.clientHeight
    if (this.model.layout === "column") {
      elHeight = Math.round(elHeight/2)
    } else {
      elWidth = Math.round(elWidth/2)
    }

    const widthTitle = this.model.title.length
    const widthValue = 2*this._value_format.length
    const widthValue2 = this._value_change_format.length+1

    const widthConstraint1 = elWidth/widthTitle*2.0
    const widthConstraint2 = elWidth/widthValue*1.8
    const widthConstraint3 = elWidth/widthValue2*2.0
    const heightConstraint = elHeight/6

    const fontSize = Math.min(widthConstraint1, widthConstraint2, widthConstraint3, heightConstraint)
    this.textDiv.style.fontSize = `${Math.trunc(fontSize)  }px`
    this.textDiv.style.lineHeight = "1.3"
  }

  updateTitle(update_fontsize: boolean = false): void {
    this.titleDiv.innerText = this.model.title
    if (update_fontsize) {
      this.updateTextFontSize()
    }
  }

  updateValue(update_fontsize: boolean = false): void {
    this._value_format = this.model.formatter.doFormat([this.model.value], {loc: 0})[0]
    this.valueDiv.innerText = this._value_format
    if (update_fontsize) {
      this.updateTextFontSize()
    }
  }

  updateValue2(update_fontsize: boolean = false): void {
    this._value_change_format = this.model.change_formatter.doFormat([this.model.value_change], {loc: 0})[0]
    this.value2Div.innerText = this._value_change_format
    this.updateValueChange()
    if (update_fontsize) {
      this.updateTextFontSize()
    }
  }

  updateValueChange(): void {
    if (this.model.value_change > 0) {
      this.changeDiv.innerHTML = "&#9650;"
      this.changeDiv.style.color = this.model.pos_color
    } else if (this.model.value_change < 0) {
      this.changeDiv.innerHTML = "&#9660;"
      this.changeDiv.style.color = this.model.neg_color
    } else {
      this.changeDiv.innerHTML = "&nbsp;"
      this.changeDiv.style.color = "inherit"
    }
  }

  updateLayout(): void {
    if (this.model.layout === "column") {
      this.containerDiv.style.display = "block"
      this.textDiv.style.height = "50%"
      this.textDiv.style.width = "100%"
      this.plotDiv.style.height = "50%"
      this.plotDiv.style.width = "100%"
    } else {
      this.containerDiv.style.display = "flex"
      this.textDiv.style.height = "100%"
      this.textDiv.style.width = ""
      this.plotDiv.style.height = "100%"
      this.plotDiv.style.width = ""
      this.textDiv.style.flex = "1"
      this.plotDiv.style.flex = "1"
    }
    if (this._has_finished) {
      this.invalidate_layout()
    }
  }
}

export namespace TrendIndicator {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    change_formatter: p.Property<TickFormatter>
    description: p.Property<string>
    formatter: p.Property<TickFormatter>
    layout: p.Property<string>
    source: p.Property<any>
    plot_x: p.Property<string>
    plot_y: p.Property<string>
    plot_color: p.Property<string>
    plot_type: p.Property<string>
    pos_color: p.Property<string>
    neg_color: p.Property<string>
    title: p.Property<string>
    value: p.Property<number>
    value_change: p.Property<number>
  }
}

export interface TrendIndicator extends TrendIndicator.Attrs { }

export class TrendIndicator extends HTMLBox {
  declare properties: TrendIndicator.Props

  constructor(attrs?: Partial<TrendIndicator.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.trend"

  static {
    this.prototype.default_view = TrendIndicatorView

    this.define<TrendIndicator.Props>(({Float, Str, Ref}) => ({
      description:  [ Str,              "" ],
      formatter:        [ Ref(TickFormatter), () => new BasicTickFormatter() ],
      change_formatter: [ Ref(TickFormatter), () => new NumeralTickFormatter() ],
      layout:       [ Str,        "column" ],
      source:       [ Ref(ColumnDataSource)   ],
      plot_x:       [ Str,             "x" ],
      plot_y:       [ Str,             "y" ],
      plot_color:   [ Str,            blue ],
      plot_type:    [ Str,           "bar" ],
      pos_color:    [ Str,           green ],
      neg_color:    [ Str,             red ],
      title:        [ Str,              "" ],
      value:        [ Float,               0 ],
      value_change: [ Float,               0 ],
    }))
  }
}
