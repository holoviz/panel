import {PanelHTMLBoxView, set_size} from "../layout"
import {div} from "@bokehjs/core/dom"

import  {vtkns} from "./vtk_utils"

export class VTKHTMLBoxView extends PanelHTMLBoxView{
  protected _vtk_container: HTMLDivElement
  protected _vtk_renwin: any

  render(): void {
    super.render()
    this._vtk_container = div()
    set_size(this._vtk_container, this.model)
    this.el.appendChild(this._vtk_container)
    this._vtk_renwin = vtkns.FullScreenRenderWindow.newInstance({
      rootContainer: this.el,
      container: this._vtk_container
    })
    this._remove_default_key_binding()
  }

  after_layout(): void {
    super.after_layout()
    this._vtk_renwin.resize()
  }

  _remove_default_key_binding(): void {
    const interactor = this._vtk_renwin.getInteractor()
    document.querySelector('body')!.removeEventListener('keypress',interactor.handleKeyPress)
    document.querySelector('body')!.removeEventListener('keydown',interactor.handleKeyDown)
    document.querySelector('body')!.removeEventListener('keyup',interactor.handleKeyUp)
  }

}
