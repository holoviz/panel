import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"

export class PlotlyPlotView extends HTMLBoxView {
  model: PlotlyPlot

  initialize(options: any): void {
    super.initialize(options)
    this._plot()
    this.connect(this.model.properties.data.change, this._plot)
  }

  render(): void {
    super.render()
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
