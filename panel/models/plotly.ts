import * as p from "core/properties"
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"

export class PlotlyPlotView extends LayoutDOMView {
  model: PlotlyPlot
  protected _initialized: boolean

  initialize(options): void {
    super.initialize(options)
    const url = "https://cdn.plot.ly/plotly-latest.min.js"

    this._initialized = false;
    if (window.Plotly) {
      this._init()
    } else if ((window.Jupyter !== undefined) && (window.Jupyter.notebook !== undefined)) {
      window.require.config({
        paths: {
          Plotly: url.slice(0, -3)
        }
      });
      var that = this
      window.require(["Plotly"], function(Plotly) {
        window.Plotly = Plotly
        that._init()
      })
    } else {
      const script = document.createElement('script')
      script.src = url
      script.async = false
      script.onreadystatechange = script.onload = () => { this._init() }
      document.querySelector("head").appendChild(script)
    }
  }

  get_width(): number {
    return this.model.data.layout.width
  }

  get_height(): number {
    return this.model.data.layout.height
  }

  _init(): void {
    this._plot()
    this._initialized = true
    this.connect(this.model.properties.data.change, this._plot)
  }

  render(): void {
    super.render()
    if (this._initialized)
      this._plot()
  }

  _plot(): void {
    for (const i = 0; i < this.model.data.data.length; i++) {
      const trace = this.model.data.data[i]
      const cds = this.model.data_sources[i]
      for (const column of cds.columns()) {
        const shape = cds._shapes[column]
        let array = cds.get_array(column)
        if (shape.length > 1) {
          const arrays = []
          for (const s = 0; s < shape[0]; s++) {
            arrays.push(array.slice(s*shape[1], (s+1)*shape[1]))
          }
          array = arrays
        }
        trace[column] = array
      }
    }
    Plotly.react(this.el, this.model.data.data, this.model.data.layout)
  }
}


export namespace PlotlyPlot {
  export interface Attrs extends LayoutDOM.Attrs {}
  export interface Props extends LayoutDOM.Props {}
}

export interface PlotlyPlot extends PlotlyPlot.Attrs {}

export class PlotlyPlot extends LayoutDOM {
  properties: PlotlyPlot.Props

  constructor(attrs?: Partial<PlotlyPlot.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "PlotlyPlot"
    this.prototype.default_view = PlotlyPlotView

    this.define({
      data: [ p.Any         ],
      data_sources: [ p.Array  ],
    })
  }
}
PlotlyPlot.initClass()
