import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box";

export class VtkPlotView extends HTMLBoxView {
  model: VtkPlot
  protected _initialized: boolean
  protected _vtk: any
  protected _rendererEl: any

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
    this._initialized = true
    super.render()
    this.connect(this.model.properties.vtkjs.change, this._update)
  }

  render() {
    super.render()
    this._rendererEl = this._vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
      container: this.el,
    });
    this._update()
  }

  _update(): void{
    if (!this.model.append) {this._delete_all_actors()}
    if (this.model.vtkjs == null) {
      this._rendererEl.getRenderWindow().render()
      return
    }

    const dataAccessHelper = this._vtk.IO.Core.DataAccessHelper.get('zip', {
      zipContent: atob(this.model.vtkjs),
      callback: (_zip: any) => {
        const sceneImporter = this._vtk.IO.Core.vtkHttpSceneLoader.newInstance({
          renderer: this._rendererEl.getRenderer(),
          dataAccessHelper,
        })
        sceneImporter.setUrl('index.json');
        sceneImporter.onReady(() => {
          this._rendererEl.getRenderWindow().render()
        })
      }
    })
  }

  _delete_all_actors(): void{
    const renderer = this._rendererEl.getRenderer()
    renderer.getActors().map((actor: unknown) => renderer.removeActor(actor))
  }

}


export namespace VtkPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    vtkjs: p.Property<string>
    append: p.Property<boolean>
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
      vtkjs:  [p.String        ],
      append: [p.Boolean, false],
    })
  }
}
VtkPlot.initClass()
