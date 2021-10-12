import * as p from "@bokehjs/core/properties"

import {AbstractVTKView, AbstractVTKPlot} from "./vtklayout"
import {vtkns} from "./util"

export class VTKJSPlotView extends AbstractVTKView {
  model: VTKJSPlot

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => {
      this.invalidate_render()
    })
  }

  render(): void {
    super.render()
    this._create_orientation_widget()
    this._set_axes()
  }

  invalidate_render(): void {
    this._vtk_renwin = null
    super.invalidate_render()
  }

  init_vtk_renwin(): void {
    this._vtk_renwin = vtkns.FullScreenRenderWindow.newInstance({
      rootContainer: this.el,
      container: this._vtk_container,
    })
  }

  plot(): void {
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
        const fn = (window as any).vtk.macro.debounce(
          () =>
            setTimeout(() => {
              if (this._axes == null && this.model.axes) this._set_axes()
              this._set_camera_state()
              this._get_camera_state()
            }, 100),
          100
        )
        sceneImporter.setUrl("index.json")
        sceneImporter.onReady(fn)
      },
    })
  }
}

export namespace VTKJSPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = AbstractVTKPlot.Props
}

export interface VTKJSPlot extends VTKJSPlot.Attrs {}

export class VTKJSPlot extends AbstractVTKPlot {
  properties: VTKJSPlot.Props

  static init_VTKJSPlot(): void {
    this.prototype.default_view = VTKJSPlotView

    this.define<VTKJSPlot.Props>(({Boolean, Nullable, String}) => ({
      data:               [ Nullable(String)  ],
      enable_keybindings: [ Boolean, false    ],
    }))
  }
}
