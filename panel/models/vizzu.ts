import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";

import {HTMLBox, HTMLBoxView} from "./layout"

export class VizzuChartView extends HTMLBoxView {
  container: HTMLDivElement
  timeout: number
  model: VizzuChart
  vizzu_view: any
  last_updated: number

  connect_signals(): void {
    if (this.timeout)
      clearTimeout(this.timeout)
    super.connect_signals()
    this.connect(this.model.properties.config.change, () => {
      this.vizzu_view.animate({config: this.model.config}, this.model.duration+'ms')
    })
    const update = () => {
      const now = Date.now()
      const diff = now-this.last_updated
      if (diff < this.model.duration)
	setTimeout(update, diff)
      else {
	this.vizzu_view.animate({data: this.data()}, this.model.duration+'ms')
	this.last_updated = now
      }
    }
    this.connect(this.model.source.properties.data.change, update)
  }

  private data(): any {
    const series = []
    for (const column of this.model.columns)
      series.push({...column, values: [...this.model.source.data[column.name]]})
    return {series}
  }

  render(): void {
    super.render()
    this.container = div({style: "display: contents;"})
    this.shadow_el.append(this.container)
    this.vizzu_view = new (window as any).Vizzu(this.container, {
      config: this.model.config,
      data: this.data(),
      style: this.model.style
    })
  }
}

export namespace VizzuChart {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    animation: p.Property<any>
    config: p.Property<any>
    columns: p.Property<any>
    source: p.Property<ColumnDataSource>
    duration: p.Property<number>
    style: p.Property<any>
  }
}

export interface VizzuChart extends VizzuChart.Attrs {}

export class VizzuChart extends HTMLBox {
  properties: VizzuChart.Props

  constructor(attrs?: Partial<VizzuChart.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.vizzu"

  static {
    this.prototype.default_view = VizzuChartView

    this.define<VizzuChart.Props>(({Any, Array, Number, Ref}) => ({
      animation:   [ Any,                     {} ],
      config:      [ Any,                     {} ],
      columns:     [ Array(Any),              [] ],
      source:      [ Ref(ColumnDataSource),      ],
      duration:    [ Number,                 500 ],
      style:       [ Any,                     {} ],
    }))
  }
}
