import * as p from "core/properties"
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"

export class VegaPlotView extends LayoutDOMView {
  model: VegaPlot
  protected _initialized: boolean

  initialize(options): void {
    super.initialize(options)
    const vega_url = "https://cdn.jsdelivr.net/npm/vega@4.2.0?noext"
    const vega_lite_url = "https://cdn.jsdelivr.net/npm/vega-lite@3.0.0-rc4?noext"
    const vega_embed_url = "https://cdn.jsdelivr.net/npm/vega-embed@3.18.2?noext"

    this._initialized = false;
    if (window.vega) {
      this._init()
    } else if ((window.Jupyter !== undefined) && (window.Jupyter.notebook !== undefined)) {
      window.requirejs.config({
        paths: {
          "vega-embed":  vega_embed_url,
          "vega-lib": "https://cdn.jsdelivr.net/npm/vega-lib?noext",
          "vega-lite": vega_lite_url,
          "vega": vega_url
        }
      });
      var that = this
      window.require(["vega-embed", "vega", "vega-lite"], function(vegaEmbed, vega, vegaLite) {
        window.vega = vega
        window.vl = vegaLite
        window.vegaEmbed = vegaEmbed
        that._init()
      })
    } else {
      const init = () => { this._init() }
      const load_vega_embed = () => { this._add_script(vega_embed_url, init) }
      const load_vega_lite = () => { this._add_script(vega_lite_url, load_vega_embed) }
      this._add_script(vega_url, load_vega_lite)
    }
  }

  _add_script(url: string, callback): void {
    const script = document.createElement('script')
    script.src = url
    script.async = false
    script.onreadystatechange = script.onload = callback
    document.querySelector("head").appendChild(script)
  }

  get_width(): number {
    return undefined;
  }

  get_height(): number {
    return undefined;
  }

  _init(): void {
    this._plot()
    this._initialized = true
    this.connect(this.model.properties.data.change, this._plot)
  }

  _fetch_datasets() {
    const datasets = {}
    for (const ds in this.model.data_sources) {
      const cds = this.model.data_sources[ds];
      const data = []
      const columns = cds.columns()
      for (const i = 0; i < cds.data[columns[0]].length; i++) {
        const item = {}
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
  }

  _plot(): void {
    if (!('datasets' in this.model.data)) {
      const datasets = this._fetch_datasets()
      if ('data' in datasets) {
        this.model.data.data['values'] = datasets['data']
         delete datasets['data']
      }
      this.model.data['datasets'] = datasets
    }
    vegaEmbed(this.el, this.model.data, {actions: false})
  }
}


export namespace VegaPlot {
  export interface Attrs extends LayoutDOM.Attrs {}
  export interface Props extends LayoutDOM.Props {}
}

export interface VegaPlot extends VegaPlot.Attrs {}

export class VegaPlot extends LayoutDOM {
  properties: VegaPlot.Props

  constructor(attrs?: Partial<VegaPlot.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "VegaPlot"
    this.prototype.default_view = VegaPlotView

    this.define({
      data: [ p.Any         ],
      data_sources: [ p.Any  ],
    })
  }
}
VegaPlot.initClass()
