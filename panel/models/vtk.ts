import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box";

export class VtkPlotView extends HTMLBoxView {
  model: VtkPlot
  protected _initialized: boolean

  initialize(): void {
    super.initialize()
    const url = "https://unpkg.com/vtk.js@8.3.15/dist/vtk.js"

    this._initialized = false;
    if ((window as any).vtk) {
      this._init()
    } else if (((window as any).Jupyter !== undefined) && ((window as any).Jupyter.notebook !== undefined)) {
      (window as any).require.config({
        paths: {
          vtk: url.slice(0, -3)
        }
      });
      (window as any).require(["vtk"], (vtk: any) => {
        (window as any).vtk = vtk
        this._init()
      })
    } else {
      const script: any = document.createElement('script')
      script.src = url
      script.async = false
      script.onreadystatechange = script.onload = () => {this._init()}
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
    this.el.style.setProperty('width', '500px')
    this.el.style.setProperty('height', '500px')
    const vtk = (window as any).vtk
    var rendererEl = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
      container: this.el
    });
    var actor = vtk.Rendering.Core.vtkActor.newInstance();
    var mapper = vtk.Rendering.Core.vtkMapper.newInstance();
    var cone = vtk.Filters.Sources.vtkConeSource.newInstance();

    actor.setMapper(mapper);
    mapper.setInputConnection(cone.getOutputPort());

    var renderer = rendererEl.getRenderer();
    renderer.addActor(actor);
    renderer.resetCamera();

    var renderWindow = renderer.getRenderWindow();
    renderWindow.render();
  }
}


export namespace VtkPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<any>
    data_sources: p.Property<any[]>
  }
}

export interface VtkPlot extends VtkPlot.Attrs {}

export class VtkPlot extends HTMLBox {
  properties: VtkPlot.Props

  constructor(attrs?: Partial<VtkPlot.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "VtkPlot"
    this.prototype.default_view = VtkPlotView

    this.define<VtkPlot.Props>({
      data: [ p.Any ],
      data_sources: [ p.Array ],
    })
  }
}
VtkPlot.initClass()
