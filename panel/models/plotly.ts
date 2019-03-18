import * as p from "core/properties"
import {clone} from "core/util/object"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"

export class PlotlyPlotView extends HTMLBoxView {
  model: PlotlyPlot
  _connected: string[]

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, this.render)
    this.connect(this.model.properties.layout.change, this._relayout)
    this.connect(this.model.properties.data_sources.change, () => this._connect_sources())
    this._connected = []
    this._connect_sources()
  }

  _connect_sources(): void {
    for (let i = 0; i < this.model.data.length; i++) {
      const cds = this.model.data_sources[i]
      if (this._connected.indexOf(cds.id) < 0) {
        this.connect(cds.properties.data.change, () => this._restyle(i))
        this._connected.push(cds.id)
      }
    }
  }

  render(): void {
    super.render()
    if (!(window as any).Plotly) { return }
    if (!this.model.data.length && !Object.keys(this.model.layout).length) {
      (window as any).Plotly.purge(this.el);
    }
    const data = [];
    for (let i = 0; i < this.model.data.length; i++) {
      data.push(this._get_trace(i, false));
    }
    (window as any).Plotly.react(this.el, data, this.model.layout);
  }

  _get_trace(index: number, update: boolean): any {
    const trace = clone(this.model.data[index]);
    const cds = this.model.data_sources[index];
    for (const column of cds.columns()) {
      const shape: number[] = cds._shapes[column][0];
      let array = cds.get_array(column)[0];
      if (shape.length > 1) {
        const arrays = [];
        for (let s = 0; s < shape[0]; s++) {
          arrays.push(array.slice(s*shape[1], (s+1)*shape[1]));
        }
        array = arrays;
      }
      if (update) {
        trace[column] = [array];
      } else {
        trace[column] = array;
      }
    }
    return trace;
  }

  _restyle(index: number): void {
    if (!(window as any).Plotly) { return }
    const trace = this._get_trace(index, true);
    (window as any).Plotly.restyle(this.el, trace, index)
  }

  _relayout(): void {
    if (!(window as any).Plotly) { return }
    (window as any).Plotly.relayout(this.el, this.model.layout)
  }
}

export namespace PlotlyPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any[]>
    layout: p.Property<any>
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
      data: [ p.Array, [] ],
      layout: [ p.Any, {} ],
      data_sources: [ p.Array, [] ],
    })
  }
}
PlotlyPlot.initClass()
