import * as p from "@bokehjs/core/properties"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"

export class EChartsView extends HTMLBoxView {
  model: ECharts
  _chart: any

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => this._plot())
    this.connect(this.model.properties.theme.change, () => this._retheme())
	const {width, height} = this.model.properties
    this.on_change([width, height], () => this._resize())

  }

  render(): void {
    super.render()
	this._chart = (window as any).echarts.init(this.el, this.model.theme, {width: this.model.width, height: this.model.height});
    this._plot()
  }

  _plot(): void {
    if ((window as any).echarts == null)
      return
	this._chart.setOption(this.model.data);
  }

  _retheme(): void {
    (window as any).echarts.dispose(this._chart);
	this.render();
  }

  _resize(): void {
	this._chart.resize({width: this.model.width, height: this.model.height});
  }
}

export namespace ECharts {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
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

  static init_ECharts(): void {
    this.prototype.default_view = EChartsView

    this.define<ECharts.Props>({
      data:  [ p.Any               ],
      theme: [ p.String, "default" ]
    })
  }
}
