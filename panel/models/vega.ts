import * as p from "core/properties"
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"

export class VegaPlotView extends LayoutDOMView {
  model: VegaPlot

  initialize(options): void {
    super.initialize(options)
    const vega_url = "https://cdn.jsdelivr.net/npm/vega@4.2.0"
    const vega_lite_url = "https://cdn.jsdelivr.net/npm/vega-lite@3.0.0-rc4"
    const vega_embed_url = "https://cdn.jsdelivr.net/npm/vega-embed@3.18.2"

    if (window.vega) {
      this._init()
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
    return this.model.data.config.view.width
  }

  get_height(): number {
    return this.model.data.config.view.height + 50
  }

  _init(): void {
    this._plot()
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

  _plot(): void {
    if (!('datasets' in this.model.data)) {
      this.model.data['datasets'] = this._fetch_datasets()
    }
    vegaEmbed(this.el, this.model.data);
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
