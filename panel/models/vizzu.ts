import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";

import {PanelHTMLBoxView} from "./layout"

export class VizzuChartView extends PanelHTMLBoxView {
  model: VizzuChart
  vizzu_view: any

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.config.change, () => {
      this.vizzu_view.animate({config: this.model.config}, this.model.duration+'ms')
    })
    this.connect(this.model.source.properties.data.change, () => {
      console.log(this.data())
      this.vizzu_view.animate({data: this.data()}, this.model.duration+'ms')
    })
  }

  private data(): any {
    const series = []
    for (const column of this.model.columns)
      series.push({...column, values: [...this.model.source.data[column.name]]})
    return {series}
  }

  render(): void {
    super.render()
    this.vizzu_view = new (window as any).Vizzu(this.el, {
      config: this.model.config,
      data: this.data(),
      style: this.model.style
    })
  }
}

export namespace VizzuChart {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
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
      config:      [ Any,                     {} ],
      columns:     [ Array(Any),              [] ],
      source:      [ Ref(ColumnDataSource),      ],
      duration:    [ Number,                 500 ],
      style:       [ Any,                     {} ],
    }))
  }
}
