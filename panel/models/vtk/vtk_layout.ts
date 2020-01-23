import  {vtkns} from "./vtk_utils"
import {PanelHTMLBoxView, set_size} from "../layout"
import {div} from "@bokehjs/core/dom"

export class VTKHTMLBoxView extends PanelHTMLBoxView{
  protected _vtk_container: HTMLDivElement
  protected _vtk_renwin: any
  protected _initialized: boolean = false

  render(): void{
    super.render()
    this._vtk_container = div()
    this.el.appendChild(this._vtk_container)
    set_size(this._vtk_container, this.model)
    this._vtk_renwin = vtkns.FullScreenRenderWindow.newInstance({
      rootContainer: this.el,
      container: this._vtk_container
    })
    this._initialized = false
  }
}
