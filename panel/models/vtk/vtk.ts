import * as p from "@bokehjs/core/properties"
import {clone} from "@bokehjs/core/util/object"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"
import {div, canvas} from "@bokehjs/core/dom"
import {
  majorAxis, vtkAxesActor, vtkOrientationMarkerWidget, vtkWidgetManager,
  vtkInteractiveOrientationWidget, vtkDataAccessHelper, vtkFullScreenRenderWindow,
  vtkHttpSceneLoader, vtk, vtkOutlineFilter, vtkMapper, vtkActor, create_axes
} from "./vtk_utils"



export class VTKPlotView extends HTMLBoxView {
  model: VTKPlot
  protected _container: HTMLDivElement
  protected _rendererEl: any
  protected _setting: boolean = false
  protected _orientationWidget: any
  protected _widgetManager: any
  protected _axes: any

  _create_orientation_widget(): void {
    const axes = vtkAxesActor.newInstance()

    // add orientation widget
    const orientationWidget = vtkOrientationMarkerWidget.newInstance({
      actor: axes,
      interactor: this._rendererEl.getInteractor(),
    })
    orientationWidget.setEnabled(true)
    orientationWidget.setViewportCorner(
      vtkOrientationMarkerWidget.Corners.BOTTOM_RIGHT
    )
    orientationWidget.setViewportSize(0.15)
    orientationWidget.setMinPixelSize(100)
    orientationWidget.setMaxPixelSize(300)

    this._orientationWidget = orientationWidget

    const widgetManager = vtkWidgetManager.newInstance()
    widgetManager.setRenderer(orientationWidget.getRenderer())

    const widget = vtkInteractiveOrientationWidget.newInstance()
    widget.placeWidget(axes.getBounds());
    widget.setBounds(axes.getBounds());
    widget.setPlaceFactor(1);

    const vw = widgetManager.addWidget(widget)
    this._widgetManager = widgetManager

    // Manage user interaction
    vw.onOrientationChange(({direction} : any) => {
      const camera = this._rendererEl.getRenderer().getActiveCamera()
      const focalPoint = camera.getFocalPoint()
      const position = camera.getPosition()
      const viewUp = camera.getViewUp()

      const distance = Math.sqrt(
        Math.pow(position[0]-focalPoint[0],2) +
        Math.pow(position[1]-focalPoint[1],2) +
        Math.pow(position[2]-focalPoint[2],2)
      )

      camera.setPosition(
        focalPoint[0] + direction[0] * distance,
        focalPoint[1] + direction[1] * distance,
        focalPoint[2] + direction[2] * distance
      )

      if (direction[0])
        camera.setViewUp(majorAxis(viewUp, 1, 2))
      if (direction[1])
        camera.setViewUp(majorAxis(viewUp, 0, 2))
      if (direction[2])
        camera.setViewUp(majorAxis(viewUp, 0, 1))

      this._orientationWidget.updateMarkerOrientation()
      this._rendererEl.getRenderer().resetCameraClippingRange()
      this._rendererEl.getRenderWindow().render()
    })

    this._orientation_widget_visbility(this.model.orientation_widget)
  }

  after_layout(): void {
    if (!this._rendererEl) {
      const container = div({
        style: {
          width: "100%",
          height: "100%"
        }
      })
      this.el.appendChild(container)
      this._rendererEl = vtkFullScreenRenderWindow.newInstance({
        rootContainer: this.el,
        container: container
      })
      const canvas_list = container.getElementsByTagName('canvas')
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
      container.appendChild(axes_canvas)
      this._rendererEl.setResizeCallback(() => {
        const dims = container.getBoundingClientRect()
        const width = Math.floor(dims.width * window.devicePixelRatio)
        const height = Math.floor(dims.height * window.devicePixelRatio)
        axes_canvas.setAttribute('width', width.toFixed())
        axes_canvas.setAttribute('height', height.toFixed())
      })
      this._plot()
      this._rendererEl.getRenderer().getActiveCamera().onModified(() => this._get_camera_state())
      this._remove_default_key_binding()
      this.model.renderer_el = this._rendererEl
    }
    super.after_layout()
  }

  _orientation_widget_visbility(visbility: boolean): void {
    this._orientationWidget.setEnabled(visbility)
    if(visbility)
      this._widgetManager.enablePicking()
    else
      this._widgetManager.disablePicking()
    this._orientationWidget.updateMarkerOrientation()
    this._rendererEl.getRenderWindow().render()
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => this._plot())
    this.connect(this.model.properties.camera.change, () => this._set_camera_state())
    this.connect(this.model.properties.orientation_widget.change, () => {
      this._orientation_widget_visbility(this.model.orientation_widget)
    })

    this.el.addEventListener('mouseenter', () => {
      const interactor = this._rendererEl.getInteractor()
      if(this.model.enable_keybindings){
        document.querySelector('body')!.addEventListener('keypress',interactor.handleKeyPress)
        document.querySelector('body')!.addEventListener('keydown',interactor.handleKeyDown)
        document.querySelector('body')!.addEventListener('keyup',interactor.handleKeyUp)
      }
    })
    this.el.addEventListener('mouseleave', () => {
      const interactor = this._rendererEl.getInteractor()
      document.querySelector('body')!.removeEventListener('keypress',interactor.handleKeyPress)
      document.querySelector('body')!.removeEventListener('keydown',interactor.handleKeyDown)
      document.querySelector('body')!.removeEventListener('keyup',interactor.handleKeyUp)
    })
  }

  _remove_default_key_binding(): void {
    const interactor = this._rendererEl.getInteractor()
    document.querySelector('body')!.removeEventListener('keypress',interactor.handleKeyPress)
    document.querySelector('body')!.removeEventListener('keydown',interactor.handleKeyDown)
    document.querySelector('body')!.removeEventListener('keyup',interactor.handleKeyUp)
  }

  _get_camera_state(): void {
    if (!this._setting) {
      this._setting = true;
      const state = clone(this._rendererEl.getRenderer().getActiveCamera().get());
      delete state.classHierarchy;
      delete state.vtkObject;
      delete state.vtkCamera;
      delete state.viewPlaneNormal;
      this.model.camera = state;
      this._setting = false;
    }
  }

  _set_camera_state(): void {
    if (!this._setting) {
      this._setting = true;
      try {
        this._rendererEl.getRenderer().getActiveCamera().set(this.model.camera);
      } finally {
        this._setting = false;
      }
      if (this._orientationWidget != null){
        this._orientationWidget.updateMarkerOrientation();
      }
      this._rendererEl.getRenderer().resetCameraClippingRange()
      this._rendererEl.getRenderWindow().render();
    }
  }

  
  _set_axes(): void{
    const axesCanvas = this._rendererEl.getContainer().getElementsByClassName('axes-canvas')[0]
    const {origin, xticks, yticks, zticks} = this.model.axes
    const {psActor, axesActor, gridActor} = create_axes(origin, xticks, yticks, zticks, axesCanvas)
    this._axes = {
      psActor,
      axesActor,
      gridActor
    }
    this._rendererEl.getRenderer().addActor(psActor)
    this._rendererEl.getRenderer().addActor(axesActor)
    this._rendererEl.getRenderer().addActor(gridActor)
  }

  _plot(): void{
    this._delete_all_actors()
    if (!this.model.data) {
      this._rendererEl.getRenderWindow().render()
      return
    }
    const dataAccessHelper = vtkDataAccessHelper.get('zip', {
      zipContent: atob(this.model.data),
      callback: (_zip: unknown) => {
        const sceneImporter = vtkHttpSceneLoader.newInstance({
          renderer: this._rendererEl.getRenderer(),
          dataAccessHelper,
        })
        const fn = vtk.macro.debounce(() => {
          if (this._orientationWidget == null)
            this._create_orientation_widget()
          if (this._axes == null && this.model.axes)
            this._set_axes()
            this._set_camera_state()
        }, 100)
        sceneImporter.setUrl('index.json')
        sceneImporter.onReady(fn)
      }
    })
  }

  _delete_all_actors(): void{
    this._rendererEl.getRenderer().getActors().map((actor: unknown) => this._rendererEl.getRenderer().removeActor(actor))
  }
}

export namespace VTKPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<string>
    camera: p.Property<any>
    axes: p.Property<any>
    enable_keybindings: p.Property<boolean>
    orientation_widget: p.Property<boolean>
  }
}

export interface VTKPlot extends VTKPlot.Attrs {}

export class VTKPlot extends HTMLBox {
  properties: VTKPlot.Props
  renderer_el: any
  outline: any
  outline_actor: any

  constructor(attrs?: Partial<VTKPlot.Attrs>) {
    super(attrs)
    this.renderer_el = null
    this.outline = vtkOutlineFilter.newInstance() //use to display bouding box of a selected actor
    const mapper = vtkMapper.newInstance()
    mapper.setInputConnection(this.outline.getOutputPort())
    this.outline_actor = vtkActor.newInstance()
    this.outline_actor.setMapper(mapper)
  }

  getActors() : [any] {
    return this.renderer_el.getRenderer().getActors()
  }

  static __module__ = "panel.models.vtk"

  static init_VTKPlot(): void {
    this.prototype.default_view = VTKPlotView

    this.define<VTKPlot.Props>({
      data:               [ p.String         ],
      camera:             [ p.Any            ],
      axes:               [ p.Any            ],
      enable_keybindings: [ p.Boolean, false ],
      orientation_widget: [ p.Boolean, false ],
    })

    this.override({
      height: 300,
      width: 300
    });
  }
}
