import * as p from "@bokehjs/core/properties"

import {div} from "@bokehjs/core/dom"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"

import {PanelHTMLBoxView, set_size} from "../layout"

import  {vtkns, VolumeType, majorAxis} from "./vtk_utils"

export abstract class AbstractVTKView extends PanelHTMLBoxView{
  model: AbstractVTKPlot
  protected _vtk_container: HTMLDivElement
  protected _vtk_renwin: any
  protected _orientationWidget: any
  protected _widgetManager: any

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => {
      this.invalidate_render()
    })
    this.connect(this.model.properties.orientation_widget.change, () => {
      this._orientation_widget_visbility(this.model.orientation_widget)
    })
  }

  _orientation_widget_visbility(visbility: boolean): void {
    this._orientationWidget.setEnabled(visbility)
    if(visbility)
      this._widgetManager.enablePicking()
    else
      this._widgetManager.disablePicking()
    this._orientationWidget.updateMarkerOrientation()
    this._vtk_renwin.getRenderWindow().render()
  }

  _create_orientation_widget(): void {
    const axes = vtkns.AxesActor.newInstance()

    // add orientation widget
    const orientationWidget = vtkns.OrientationMarkerWidget.newInstance({
      actor: axes,
      interactor: this._vtk_renwin.getInteractor(),
    })
    orientationWidget.setEnabled(true)
    orientationWidget.setViewportCorner(
      vtkns.OrientationMarkerWidget.Corners.BOTTOM_RIGHT
    )
    orientationWidget.setViewportSize(0.15)
    orientationWidget.setMinPixelSize(100)
    orientationWidget.setMaxPixelSize(300)

    this._orientationWidget = orientationWidget

    const widgetManager = vtkns.WidgetManager.newInstance()
    widgetManager.setRenderer(orientationWidget.getRenderer())

    const widget = vtkns.InteractiveOrientationWidget.newInstance()
    widget.placeWidget(axes.getBounds());
    widget.setBounds(axes.getBounds());
    widget.setPlaceFactor(1);

    const vw = widgetManager.addWidget(widget)
    this._widgetManager = widgetManager

    // Manage user interaction
    vw.onOrientationChange(({direction} : any) => {
      const camera = this._vtk_renwin.getRenderer().getActiveCamera()
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
      this._vtk_renwin.getRenderer().resetCameraClippingRange()
      this._vtk_renwin.getRenderWindow().render()
    })

    this._orientation_widget_visbility(this.model.orientation_widget)
  }

  render(): void {
    super.render()
    this._orientationWidget = null
    this._vtk_container = div()
    set_size(this._vtk_container, this.model)
    this.el.appendChild(this._vtk_container)
    this._vtk_renwin = vtkns.FullScreenRenderWindow.newInstance({
      rootContainer: this.el,
      container: this._vtk_container
    })
    this._remove_default_key_binding()
    this._create_orientation_widget()
    this.model.renderer_el = this._vtk_renwin
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

export namespace AbstractVTKPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<string|VolumeType>
    orientation_widget: p.Property<boolean>
  }
}

export interface AbstractVTKPlot extends AbstractVTKPlot.Attrs {}

export abstract class AbstractVTKPlot extends HTMLBox {
  properties: AbstractVTKPlot.Props
  renderer_el: any

  static __module__ = "panel.models.vtk"

  constructor(attrs?: Partial<AbstractVTKPlot.Attrs>) {
    super(attrs)
  }

  static init_AbstractVTKPlot(): void{
    this.define<AbstractVTKPlot.Props>({
      orientation_widget: [ p.Boolean, false ],
    })

    this.override({
      height: 300,
      width: 300
    });
  }
}

