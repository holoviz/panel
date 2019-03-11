import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"

export class PlotlyPlotView extends HTMLBoxView {
  model: PlotlyPlot
  protected _initialized: boolean

  initialize(options: any): void {
    super.initialize(options)
    const url = "https://cdn.plot.ly/plotly-latest.min.js"

    this._initialized = false;
    if ((window as any).Plotly) {
      this._init()
    } else if (((window as any).Jupyter !== undefined) && ((window as any).Jupyter.notebook !== undefined)) {
      (window as any).require.config({
        paths: {
          Plotly: url.slice(0, -3)
        }
      });
      (window as any).require(["Plotly"], (Plotly: any) => {
        (window as any).Plotly = Plotly
        this._init()
      })
    } else {
      const script: any = document.createElement('script')
      script.src = url
      script.async = false
      script.onreadystatechange = script.onload = () => { this._init() }
      (document.querySelector("head") as any).appendChild(script)
    }
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
    if (this.model.data == null)
      return
    for (let i = 0; i < this.model.data.data.length; i++) {
      const trace = this.model.data.data[i]
      const cds = this.model.data_sources[i]
      for (const column of cds.columns()) {
        const shape: any = cds._shapes[column]
        let array = cds.get_array(column)
        if (shape.length > 1) {
          const arrays = []
          for (let s = 0; s < shape[0]; s++) {
            arrays.push(array.slice(s*shape[1], (s+1)*shape[1]))
          }
          array = arrays
        }
        trace[column] = array
      }
    }
    (window as any).Plotly.react(this.el, this.model.data.data, this.model.data.layout)
  }
}


export namespace PlotlyPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    data_sources: p.Property<any[]> 
  }
}

export interface PlotlyPlot extends PlotlyPlot.Attrs {}

export class PlotlyPlot extends HTMLBox {
  properties: PlotlyPlot.Props

  constructor(attrs?: Partial<PlotlyPlot.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "PlotlyPlot"
    this.prototype.default_view = PlotlyPlotView

    this.define<PlotlyPlot.Props>({
      data: [ p.Any ],
      data_sources: [ p.Array ],
    })
  }
}
PlotlyPlot.initClass()
