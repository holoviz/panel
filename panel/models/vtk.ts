import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box";


// interface vtkPolyDataReader {
//   getOutputPort(): unknown;
//   parseAsText(data: String): void;
// }

export class VtkPlotView extends HTMLBoxView {
  model: VtkPlot
  protected _initialized: boolean
  protected _reader: any
  protected _actor: any //TODO : typed
  protected _mapper: any //TODO : typed
  protected _rendererEl: any
  protected _renderer: any
  protected _renderWindow: any
  protected _vtk: any

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
    this.el.style.setProperty('width', '500px')
    this.el.style.setProperty('height', '500px')
    this._vtk = (window as any).vtk
    this._reader = this._vtk.IO.Legacy.vtkPolyDataReader.newInstance()
    this._mapper = this._vtk.Rendering.Core.vtkMapper.newInstance()
    this._actor = this._vtk.Rendering.Core.vtkActor.newInstance()
    this._actor.setMapper(this._mapper)
    this._mapper.setInputConnection(this._reader.getOutputPort())


    this.connect(this.model.properties.poly_data.change, this._update)
    this._initialized = true
    this._update()
  }

  render(): void {
    super.render()
    if (this._initialized) {
      this._rendererEl = this._vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
        container: this.el
      });
      this._renderer = this._rendererEl.getRenderer();
      this._renderWindow = this._renderer.getRenderWindow();
      this._renderer.addActor(this._actor);
      this._renderer.resetCamera();
      this._renderWindow.render();
    }

  }

  _update(): void{
    this._reader.parseAsText(this.model.poly_data)
    this.render()
  }
}


export namespace VtkPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    poly_data: p.Property<string>
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
      poly_data: [ p.String ],
    })
  }
}
VtkPlot.initClass()
