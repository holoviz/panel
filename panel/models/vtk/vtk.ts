import * as p from "@bokehjs/core/properties"

import {AbstractVTKView, AbstractVTKPlot} from "./vtk_layout"
import {vtk, vtkns} from "./vtk_utils"

export class VTKPlotView extends AbstractVTKView {
  model: VTKPlot

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => {
      this.invalidate_render()
    })
  }

  render(): void {
    this._axes = null
    super.render()
    this._plot()
    this._bind_key_events()
  }

  _plot(): void {
    if (!this.model.data) {
      this._vtk_renwin.getRenderWindow().render()
      return
    }
    const dataAccessHelper = vtkns.DataAccessHelper.get("zip", {
      zipContent: atob(this.model.data as string),
      callback: (_zip: unknown) => {
        const sceneImporter = vtkns.HttpSceneLoader.newInstance({
          renderer: this._vtk_renwin.getRenderer(),
          dataAccessHelper,
        })
        const fn = vtk.macro.debounce(
          () =>
            setTimeout(() => {
              if (this._axes == null && this.model.axes) this._set_axes()
          this.model.properties.camera.change.emit()
            }, 100),
          100
        )
        sceneImporter.setUrl("index.json")
        sceneImporter.onReady(fn)
      },
    })
  }
}

export namespace VTKPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = AbstractVTKPlot.Props
}

export interface VTKPlot extends VTKPlot.Attrs {}

export class VTKPlot extends AbstractVTKPlot {
  properties: VTKPlot.Props
  renderer_el: any
  outline: any
  outline_actor: any

  constructor(attrs?: Partial<VTKPlot.Attrs>) {
    super(attrs)
    this.outline = vtkns.OutlineFilter.newInstance() //use to display bouding box of a selected actor
    const mapper = vtkns.Mapper.newInstance()
    mapper.setInputConnection(this.outline.getOutputPort())
    this.outline_actor = vtkns.Actor.newInstance()
    this.outline_actor.setMapper(mapper)
  }

  static init_VTKPlot(): void {
    this.prototype.default_view = VTKPlotView

    this.define<VTKPlot.Props>({
      data:               [ p.String         ],
      enable_keybindings: [ p.Boolean, false ],
    })
  }
}
