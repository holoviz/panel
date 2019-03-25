import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"

function get_file(file: string, callback: any): void {
  var xobj = new XMLHttpRequest();
  xobj.overrideMimeType("application/json");
  xobj.open('GET', file, true);
  xobj.onreadystatechange = function () {
    if (xobj.readyState == 4 && xobj.status == 200) {
      callback(xobj.responseText);
    }
  };
  xobj.send(null);
}

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

  _receive_file(data: string, format: string): void {
    const values = (format === 'json') ? JSON.parse(data): data;
    this.model.data.data = {values: values, format: {type: format}};
    this._plot();
  }

  _plot(): void {
    if (!this.model.data || !(window as any).vegaEmbed)
      return
    if (!('datasets' in this.model.data)) {
      const datasets = this._fetch_datasets()
      if ('data' in datasets) {
        this.model.data.data['values'] = datasets['data']
        delete datasets['data']
      }
      this.model.data['datasets'] = datasets
    }
    if (this.model.data.data && this.model.data.data.url) {
      const url = this.model.data.data.url;
      const url_components = url.split('.');
      const format = url_components[url_components.length-1];
      get_file(this.model.data.data.url, (result: string) => this._receive_file(result, format))
      return;
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
