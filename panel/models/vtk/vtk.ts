import * as p from "@bokehjs/core/properties"

import {canvas} from "@bokehjs/core/dom"

import {VTKAxes} from "./vtkaxes"
import {AbstractVTKView, AbstractVTKPlot} from "./vtk_layout"
import {vtk, vtkns} from "./vtk_utils"

export class VTKPlotView extends AbstractVTKView {
  model: VTKPlot
  protected _axes: any
  protected _axes_initialized: boolean = false

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.axes.change, () => {
      this._delete_axes()
      if(this.model.axes)
        this._set_axes()
      this._vtk_renwin.getRenderWindow().render()
    })

    this.el.addEventListener('mouseenter', () => {
      const interactor = this._vtk_renwin.getInteractor()
      if(this.model.enable_keybindings){
        document.querySelector('body')!.addEventListener('keypress',interactor.handleKeyPress)
        document.querySelector('body')!.addEventListener('keydown',interactor.handleKeyDown)
        document.querySelector('body')!.addEventListener('keyup',interactor.handleKeyUp)
      }
    })
    this.el.addEventListener('mouseleave', () => {
      const interactor = this._vtk_renwin.getInteractor()
      document.querySelector('body')!.removeEventListener('keypress',interactor.handleKeyPress)
      document.querySelector('body')!.removeEventListener('keydown',interactor.handleKeyDown)
      document.querySelector('body')!.removeEventListener('keyup',interactor.handleKeyUp)
    })
  }

  render(): void {
    super.render()
    this._axes = null
    this._axes_initialized = false
    this._plot()
  }

  after_layout(): void {
    if (!this._axes_initialized) {
      this._render_axes_canvas()
      this._axes_initialized = true
    }
  }

  _render_axes_canvas(): void {
    const canvas_list = this._vtk_container.getElementsByTagName('canvas')
    if(canvas_list.length != 1)
      throw Error('Error at initialization of the 3D scene, container should have one and only one canvas')
    else
      canvas_list[0].classList.add('scene3d-canvas')
    const axes_canvas = canvas({
      style: {
        position: "absolute",
        top: "0",
        left: "0",
        width: "100%",
        height: "100%"
      }
    })
    axes_canvas.classList.add('axes-canvas')
    this._vtk_container.appendChild(axes_canvas)
    this._vtk_renwin.setResizeCallback(() => {
      const dims = this._vtk_container.getBoundingClientRect()
      const width = Math.floor(dims.width * window.devicePixelRatio)
      const height = Math.floor(dims.height * window.devicePixelRatio)
      axes_canvas.setAttribute('width', width.toFixed())
      axes_canvas.setAttribute('height', height.toFixed())
    })
  }

  _delete_axes(): void{
    if(this._axes == null)
      return

    Object.keys(this._axes).forEach((key) => this._vtk_renwin.getRenderer().removeActor(this._axes[key]))
    const axesCanvas = this._vtk_renwin.getContainer().getElementsByClassName('axes-canvas')[0]
    const textCtx = axesCanvas.getContext("2d");
    if (textCtx)
      textCtx.clearRect(0, 0, axesCanvas.clientWidth * window.devicePixelRatio, axesCanvas.clientHeight * window.devicePixelRatio)
    this._axes = null
  }

  _set_axes(): void{
    if (this.model.axes){
      const axesCanvas = this._vtk_renwin.getContainer().getElementsByClassName('axes-canvas')[0]
      const {psActor, axesActor, gridActor} = this.model.axes.create_axes(axesCanvas)
      this._axes = {psActor, axesActor, gridActor}
      this._vtk_renwin.getRenderer().addActor(psActor)
      this._vtk_renwin.getRenderer().addActor(axesActor)
      this._vtk_renwin.getRenderer().addActor(gridActor)
    }
  }

  _plot(): void{
    if (!this.model.data) {
      this._vtk_renwin.getRenderWindow().render()
      return
    }
    const dataAccessHelper = vtkns.DataAccessHelper.get('zip', {
      zipContent: atob((this.model.data as string)),
      callback: (_zip: unknown) => {
        const sceneImporter = vtkns.HttpSceneLoader.newInstance({
          renderer: this._vtk_renwin.getRenderer(),
          dataAccessHelper,
        })
        const fn = vtk.macro.debounce(() => {
          if (this._axes == null && this.model.axes)
            this._set_axes()
          this.model.properties.camera.change.emit()
        }, 100)
        sceneImporter.setUrl('index.json')
        sceneImporter.onReady(fn)
      }
    })
  }
}

export namespace VTKPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = AbstractVTKPlot.Props & {
    axes: p.Property<VTKAxes>
    enable_keybindings: p.Property<boolean>
  }
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
      axes:               [ p.Instance       ],
      enable_keybindings: [ p.Boolean, false ],
    })
  }
}
