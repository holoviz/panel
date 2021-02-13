import * as p from "@bokehjs/core/properties"
import {isArray} from "@bokehjs/core/util/types"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"

export class VegaPlotView extends HTMLBoxView {
  model: VegaPlot
  _connected: string[]

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, this._plot)
    this.connect(this.model.properties.data_sources.change, () => this._connect_sources())
    this._connected = []
    this._connect_sources()
  }

  _connect_sources(): void {
    for (const ds in this.model.data_sources) {
      const cds = this.model.data_sources[ds]
      if (this._connected.indexOf(ds) < 0) {
        this.connect(cds.properties.data.change, this._plot)
        this._connected.push(ds)
      }
    }
  }

  _fetch_datasets() {
    const datasets: any = {}
    for (const ds in this.model.data_sources) {
      const cds = this.model.data_sources[ds];
      const data: any = []
      const columns = cds.columns()
      for (let i = 0; i < cds.get_length(); i++) {
        const item: any = {}
        for (const column of columns) {
          item[column] = cds.data[column][i]
        }
        data.push(item)
      }
      datasets[ds] = data;
    }
    return datasets
  }

  render(): void {
    super.render()
    this._plot()
  }

  _plot(): void {
    const data = this.model.data
    if ((data == null) || !(window as any).vegaEmbed)
      return
    if (this.model.data_sources && (Object.keys(this.model.data_sources).length > 0)) {
      const datasets = this._fetch_datasets()
      if ('data' in datasets) {
        data.data['values'] = datasets['data']
        delete datasets['data']
      }
      if (data.data != null) {
        const data_objs = isArray(data.data) ? data.data : [data.data]
        for (const d of data_objs) {
          if (d.name in datasets) {
            d['values'] = datasets[d.name]
            delete datasets[d.name]
          }
        }
      }
      this.model.data['datasets'] = datasets
    }
    (window as any).vegaEmbed(this.el, this.model.data, {actions: false})
  }
}

export namespace VegaPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    data_sources: p.Property<any>
  }
}

export interface VegaPlot extends VegaPlot.Attrs {}

export class VegaPlot extends HTMLBox {
  properties: VegaPlot.Props

  constructor(attrs?: Partial<VegaPlot.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.vega"

  static init_VegaPlot(): void {
    this.prototype.default_view = VegaPlotView

    this.define<VegaPlot.Props>(({Any}) => ({
      data:         [ Any, {} ],
      data_sources: [ Any, {} ],
    }))
  }
}
