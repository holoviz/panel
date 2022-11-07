import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {HTMLBox, HTMLBoxView} from "./layout"

export class EChartsView extends HTMLBoxView {
  model: ECharts
  _chart: any
  _layout_wrapper: Element

  initialize(): void {
    super.initialize()
    this._layout_wrapper = div({style: "height: 100%; width: 100%;"})
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => this._plot())
    const {width, height, renderer, theme} = this.model.properties
    this.on_change([width, height], () => this._resize())
    this.on_change([theme, renderer], () => this.render())
  }

  render(): void {
    if (this._chart != null)
      (window as any).echarts.dispose(this._chart);
    super.render()
    const config = {width: this.model.width, height: this.model.height, renderer: this.model.renderer}
    this._chart = (window as any).echarts.init(
      this._layout_wrapper,
      this.model.theme,
      config
    )
    this._plot()
    this.shadow_el.append(this._layout_wrapper)
  }

  override remove(): void {
    super.remove()
    if (this._chart != null)
      (window as any).echarts.dispose(this._chart);
  }

  after_layout(): void {
    super.after_layout()
    this._chart.resize()
  }

  _plot(): void {
    if ((window as any).echarts == null)
      return
    this._chart.setOption(this.model.data);
  }

  _resize(): void {
    this._chart.resize({width: this.model.width, height: this.model.height});
  }
}

export namespace ECharts {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    renderer: p.Property<string>
    theme: p.Property<string>
  }
}

export interface ECharts extends ECharts.Attrs {}

export class ECharts extends HTMLBox {
  properties: ECharts.Props

  constructor(attrs?: Partial<ECharts.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.echarts"

  static {
    this.prototype.default_view = EChartsView

    this.define<ECharts.Props>(({Any, String}) => ({
      data:     [ Any,           {} ],
      theme:    [ String, "default" ],
      renderer: [ String,  "canvas" ]
    }))
  }
}
