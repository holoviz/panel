import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"

export class VegaPlotView extends HTMLBoxView {
  model: VegaPlot
  protected _initialized: boolean

  initialize(options: any): void {
    super.initialize(options)
    const vega_url = "https://cdn.jsdelivr.net/npm/vega@4.2.0?noext"
    const vega_lite_url = "https://cdn.jsdelivr.net/npm/vega-lite@3.0.0-rc4?noext"
    const vega_embed_url = "https://cdn.jsdelivr.net/npm/vega-embed@3.18.2?noext"

    this._initialized = false;
    if ((window as any).vega) {
      this._init()
    } else if (((window as any).Jupyter !== undefined) && ((window as any).Jupyter.notebook !== undefined)) {
      (window as any).requirejs.config({
        paths: {
          "vega-embed":  vega_embed_url,
          "vega-lib": "https://cdn.jsdelivr.net/npm/vega-lib?noext",
          "vega-lite": vega_lite_url,
          "vega": vega_url
        }
      });
      (window as any).require(["vega-embed", "vega", "vega-lite"], (vegaEmbed: any, vega: any, vegaLite: any) => {
        (window as any).vega = vega
        (window as any).vl = vegaLite
        (window as any).vegaEmbed = vegaEmbed
        this._init()
      })
    } else {
      const init = () => { this._init() }
      const load_vega_embed = () => { this._add_script(vega_embed_url, init) }
      const load_vega_lite = () => { this._add_script(vega_lite_url, load_vega_embed) }
      this._add_script(vega_url, load_vega_lite)
    }
  }

  _add_script(url: string, callback: any): void {
    const script: any = document.createElement('script')
    script.src = url
    script.async = false
    script.onreadystatechange = script.onload = callback;
    (document.querySelector("head") as any).appendChild(script)
  }

  _init(): void {
    this._plot()
    this._initialized = true
    this.connect(this.model.properties.data.change, this._plot)
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
	if (this._initialized)
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
