import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box";
import {div} from "core/dom";

export class VTKPlotView extends HTMLBoxView {
  model: VTKPlot
  protected _vtk: any
  protected _rendererEl: any
  protected _container: HTMLDivElement

  initialize(): void {
    super.initialize()
    const width = this.model.width ? "100%" : "300px"
    const height = this.model.height ? "100%" : "300px"
    this._vtk = (window as any).vtk
    this._container = div({
      style: {
        width,
        height
      }
    })
  }


  after_layout() {
    super.after_layout()
    this._rendererEl = this._vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
      rootContainer: this.el,
      container: this._container
    });
    this._plot()
  }

  render() {
    super.render()
    this.el.appendChild(this._container)
  }


  connect_signals(): void{
    this.connect(this.model.properties.vtkjs.change, this._plot)
  }

  _plot(): void{
    if (!this.model.append) {
      this._delete_all_actors()
    }
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


export namespace VTKPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    vtkjs: p.Property<string>
    append: p.Property<boolean>
  }
}

export interface VTKPlot extends VTKPlot.Attrs {}

export class VTKPlot extends HTMLBox {
  properties: VTKPlot.Props

  constructor(attrs?: Partial<VTKPlot.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "VTKPlot"
    this.prototype.default_view = VTKPlotView

    this.define<VTKPlot.Props>({
      vtkjs:         [p.String        ],
      append:        [p.Boolean, false],
    })
  }
}
VTKPlot.initClass()
