import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"

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
      for (let i = 0; i < cds.data[columns[0]].length; i++) {
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
    if (this.model.data == null)
      return
    if (!('datasets' in this.model.data)) {
      const datasets = this._fetch_datasets()
      if ('data' in datasets) {
        this.model.data.data['values'] = datasets['data']
        delete datasets['data']
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

  static initClass(): void {
    this.prototype.type = "VegaPlot"
    this.prototype.default_view = VegaPlotView

    this.define<VegaPlot.Props>({
      data: [ p.Any         ],
      data_sources: [ p.Any  ],
    })
  }
}
VegaPlot.initClass()
