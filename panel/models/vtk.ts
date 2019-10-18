import * as p from "@bokehjs/core/properties"
import {clone} from "@bokehjs/core/util/object"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"
import {div} from "@bokehjs/core/dom"

const vtk = (window as any).vtk

function majorAxis(vec3: number[], idxA: number, idxB: number): number[] {
  const axis = [0, 0, 0]
  const idx = Math.abs(vec3[idxA]) > Math.abs(vec3[idxB]) ? idxA : idxB
  const value = vec3[idx] > 0 ? 1 : -1
  axis[idx] = value
  return axis
}



export class VTKPlotView extends HTMLBoxView {
  model: VTKPlot
  protected _container: HTMLDivElement
  protected _rendererEl: any
  protected _renderer: any
  protected _camera: any
  protected _interactor: any
  protected _setting: boolean = false
  protected _orientationWidget: any
  protected _widgetManager: any

  initialize(): void {
    this._container = div({
      style: {
        width: "100%",
        height: "100%"
      }
    })
    super.initialize()
  }

  _create_orientation_widget(): void {
    const axes = vtk.Rendering.Core.vtkAxesActor.newInstance()

    // add orientation widget
    const orientationWidget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget.newInstance({
      actor: axes,
      interactor: this._interactor,
    })
    orientationWidget.setEnabled(true)
    orientationWidget.setViewportCorner(
      vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_RIGHT
    )
    orientationWidget.setViewportSize(0.15)
    orientationWidget.setMinPixelSize(100)
    orientationWidget.setMaxPixelSize(300)

    this._orientationWidget = orientationWidget

    const widgetManager = vtk.Widgets.Core.vtkWidgetManager.newInstance()
    widgetManager.setRenderer(orientationWidget.getRenderer())

    const widget = vtk.Widgets.Widgets3D.vtkInteractiveOrientationWidget.newInstance()
    widget.placeWidget(axes.getBounds());
    widget.setBounds(axes.getBounds());
    widget.setPlaceFactor(1);

    const vw = widgetManager.addWidget(widget)
    this._widgetManager = widgetManager

    // Manage user interaction
    vw.onOrientationChange((inputs : any) => {
      const direction = inputs.direction
      const focalPoint = this._camera.getFocalPoint()
      const position = this._camera.getPosition()
      const viewUp = this._camera.getViewUp()

      const distance = Math.sqrt(
        Math.pow(position[0]-focalPoint[0],2) +
        Math.pow(position[1]-focalPoint[1],2) +
        Math.pow(position[2]-focalPoint[2],2)
      )

      this._camera.setPosition(
        focalPoint[0] + direction[0] * distance,
        focalPoint[1] + direction[1] * distance,
        focalPoint[2] + direction[2] * distance
      )

      if (direction[0]) {
        this._camera.setViewUp(majorAxis(viewUp, 1, 2))
      }
      if (direction[1]) {
        this._camera.setViewUp(majorAxis(viewUp, 0, 2))
      }
      if (direction[2]) {
        this._camera.setViewUp(majorAxis(viewUp, 0, 1))
      }

      this._orientationWidget.updateMarkerOrientation()
      this._renderer.resetCameraClippingRange()
      this._rendererEl.getRenderWindow().render()
    })

    this._orientation_widget_visbility(this.model.orientation_widget)
  }

  after_layout(): void {
    if (!this._rendererEl) {
      this.el.appendChild(this._container)
      this._rendererEl = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
        rootContainer: this.el,
        container: this._container
      });
      this._renderer = this._rendererEl.getRenderer()
      this._interactor = this._rendererEl.getInteractor()
      this._camera = this._renderer.getActiveCamera()

      this._plot()
      this._camera.onModified(() => this._get_camera_state())
      this._remove_default_key_binding()
      this.model.renderer_el = this._rendererEl
      // this._interactor.onRightButtonPress((_callData: any) => {
      //   console.log('Not Implemented')
      // })
    }
    super.after_layout()
  }

  _orientation_widget_visbility(visbility: boolean): void {
    this._orientationWidget.setEnabled(visbility)
    if(visbility){
      this._widgetManager.enablePicking()
    }else{
      this._widgetManager.disablePicking()
    }
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

    this._container.addEventListener('mouseenter', () => {
      if(this.model.enable_keybindings){
        document.querySelector('body')!.addEventListener('keypress',this._interactor.handleKeyPress)
        document.querySelector('body')!.addEventListener('keydown',this._interactor.handleKeyDown)
        document.querySelector('body')!.addEventListener('keyup',this._interactor.handleKeyUp)
      }
    })
    this._container.addEventListener('mouseleave', () => {
      document.querySelector('body')!.removeEventListener('keypress',this._interactor.handleKeyPress)
      document.querySelector('body')!.removeEventListener('keydown',this._interactor.handleKeyDown)
      document.querySelector('body')!.removeEventListener('keyup',this._interactor.handleKeyUp)
    })
  }

  _remove_default_key_binding(): void {
    document.querySelector('body')!.removeEventListener('keypress',this._interactor.handleKeyPress)
    document.querySelector('body')!.removeEventListener('keydown',this._interactor.handleKeyDown)
    document.querySelector('body')!.removeEventListener('keyup',this._interactor.handleKeyUp)
  }

  _get_camera_state(): void {
    if (!this._setting) {
      this._setting = true;
      const state = clone(this._camera.get());
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
        this._camera.set(this.model.camera);
      } finally {
        this._setting = false;
      }
      if (this._orientationWidget != null){
        this._orientationWidget.updateMarkerOrientation();
      }
      this._renderer.resetCameraClippingRange()
      this._rendererEl.getRenderWindow().render();
    }
  }

  _plot(): void{
    this._delete_all_actors()
    if (!this.model.data) {
      this._rendererEl.getRenderWindow().render()
      return
    }
    const dataAccessHelper = vtk.IO.Core.DataAccessHelper.get('zip', {
      zipContent: atob(this.model.data),
      callback: (_zip: unknown) => {
        const sceneImporter = vtk.IO.Core.vtkHttpSceneLoader.newInstance({
          renderer: this._rendererEl.getRenderer(),
          dataAccessHelper,
        })
        const fn = vtk.macro.debounce(() => {
          if (this._orientationWidget == null)
            this._create_orientation_widget()
          this._set_camera_state()
        }, 100)
        sceneImporter.setUrl('index.json')
        sceneImporter.onReady(fn)
      }
    })
  }

  _delete_all_actors(): void{
    this._renderer.getActors().map((actor: unknown) => this._renderer.removeActor(actor))
  }
}

export namespace VTKPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<string>
    camera: p.Property<any>
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
    this.outline = vtk.Filters.General.vtkOutlineFilter.newInstance() //use to display bouding box of a selected actor
    const mapper = vtk.Rendering.Core.vtkMapper.newInstance()
    mapper.setInputConnection(this.outline.getOutputPort())
    this.outline_actor = vtk.Rendering.Core.vtkActor.newInstance()
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
      enable_keybindings: [ p.Boolean, false ],
      orientation_widget: [ p.Boolean, false ],
    })

    this.override({
      height: 300,
      width: 300
    });
  }
}
