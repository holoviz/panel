import type * as p from "@bokehjs/core/properties"

import {AbstractVTKView, AbstractVTKPlot} from "./vtklayout"
import {vtkns} from "./util"

export class VTKJSPlotView extends AbstractVTKView {
  declare model: VTKJSPlot

  override connect_signals(): void {
    super.connect_signals()
    const {data} = this.model.properties
    this.on_change(data, () => {
      this.invalidate_render()
    })
  }

  override render(): void {
    super.render()
    this._create_orientation_widget()
    this._set_axes()
  }

  override invalidate_render(): void {
    this._vtk_renwin = null
    super.invalidate_render()
  }

  init_vtk_renwin(): void {
    this._vtk_renwin = vtkns.FullScreenRenderWindow.newInstance({
      rootContainer: this._vtk_container,
      container: this._vtk_container,
    })
  }

  plot(): void {
    if (this.model.data == null && this.model.data_url == null) {
      this._vtk_renwin.getRenderWindow().render()
      return
    }
    let bytes_promise: any
    if (this.model.data_url) {
      bytes_promise = vtkns.DataAccessHelper.get("http").fetchBinary(this.model.data_url)
    } else {
      bytes_promise = async () => { this.model.data }
    }
    bytes_promise.then((zipContent: ArrayBuffer) => {
      const dataAccessHelper = vtkns.DataAccessHelper.get("zip", {
        zipContent,
        callback: (_zip: unknown) => {
          const sceneImporter = vtkns.HttpSceneLoader.newInstance({
            renderer: this._vtk_renwin.getRenderer(),
            dataAccessHelper,
          })
          const fn = (window as any).vtk.macro.debounce(
            () => {
              setTimeout(() => {
                if (this._axes == null && this.model.axes) {
                  this._set_axes()
                }
                this._set_camera_state()
                this._get_camera_state()
                this._vtk_renwin.getRenderWindow().render()
              }, 100)
            }, 100,
          )
          sceneImporter.setUrl("index.json")
          sceneImporter.onReady(fn)
        },
      })
    })
  }
}

export namespace VTKJSPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = AbstractVTKPlot.Props & {
    data_url: p.Property<string | null>
  }
}

export interface VTKJSPlot extends VTKJSPlot.Attrs {}

export class VTKJSPlot extends AbstractVTKPlot {
  declare properties: VTKJSPlot.Props

  static {
    this.prototype.default_view = VTKJSPlotView

    this.define<VTKJSPlot.Props>(({Boolean, Bytes, Nullable, String}) => ({
      data:               [ Nullable(Bytes),   null ],
      data_url:           [ Nullable(String), null ],
      enable_keybindings: [ Boolean, false    ],
    }))
  }
}
