import {PanelHTMLBoxView, set_size} from "../layout"
import {div} from "@bokehjs/core/dom"

import  {vtkns} from "./vtk_utils"

export class VTKHTMLBoxView extends PanelHTMLBoxView{
  protected _vtk_container: HTMLDivElement
  protected _vtk_renwin: any
  protected _initialized: boolean = false

  render(): void{
    super.render()
    this._vtk_container = div()
    set_size(this._vtk_container, this.model)
    this.el.appendChild(this._vtk_container)
    this._vtk_renwin = vtkns.FullScreenRenderWindow.newInstance({
      rootContainer: this.el,
      container: this._vtk_container
    })
    this._initialized = false
  }
}
