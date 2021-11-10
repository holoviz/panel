import * as p from "@bokehjs/core/properties"

import {AbstractVTKPlot, AbstractVTKView} from "./vtklayout"
import {
  ColorMapper,
  Interpolation,
  VolumeType,
  vtkns,
  data2VTKImageData,
  hexToRGB,
  vtkLutToMapper,
} from "./util"


export class VTKVolumePlotView extends AbstractVTKView {
  model: VTKVolumePlot
  protected _controllerWidget: any
  protected _vtk_image_data: any

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => {
      this._vtk_image_data = data2VTKImageData(this.model.data as VolumeType)
      this.invalidate_render()
    })
    this.connect(this.model.properties.colormap.change, () => {
      this.colormap_selector.value = this.model.colormap
      const event = new Event("change")
      this.colormap_selector.dispatchEvent(event)
    })
    this.connect(this.model.properties.shadow.change, () => {
      this.shadow_selector.value = this.model.shadow ? "1" : "0"
      const event = new Event("change")
      this.shadow_selector.dispatchEvent(event)
    })
    this.connect(this.model.properties.sampling.change, () => {
      this.sampling_slider.value = this.model.sampling.toFixed(2)
      const event = new Event("input")
      this.sampling_slider.dispatchEvent(event)
    })
    this.connect(this.model.properties.edge_gradient.change, () => {
      this.edge_gradient_slider.value = this.model.edge_gradient.toFixed(2)
      const event = new Event("input")
      this.edge_gradient_slider.dispatchEvent(event)
    })
    this.connect(this.model.properties.rescale.change, () => {
      this._controllerWidget.setRescaleColorMap(this.model.rescale)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.ambient.change, () => {
      this.volume.getProperty().setAmbient(this.model.ambient)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.diffuse.change, () => {
      this.volume.getProperty().setDiffuse(this.model.diffuse)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.specular.change, () => {
      this.volume.getProperty().setSpecular(this.model.specular)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.specular_power.change, () => {
      this.volume.getProperty().setSpecularPower(this.model.specular_power)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.display_volume.change, () => {
      this._set_volume_visibility(this.model.display_volume)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.display_slices.change, () => {
      this._set_slices_visibility(this.model.display_slices)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.slice_i.change, () => {
      if (this.image_actor_i !== undefined) {
        this.image_actor_i.getMapper().setISlice(this.model.slice_i)
        this._vtk_renwin.getRenderWindow().render()
      }
    })
    this.connect(this.model.properties.slice_j.change, () => {
      if (this.image_actor_j !== undefined) {
        this.image_actor_j.getMapper().setJSlice(this.model.slice_j)
        this._vtk_renwin.getRenderWindow().render()
      }
    })
    this.connect(this.model.properties.slice_k.change, () => {
      if (this.image_actor_k !== undefined) {
        this.image_actor_k.getMapper().setKSlice(this.model.slice_k)
        this._vtk_renwin.getRenderWindow().render()
      }
    })
    this.connect(this.model.properties.render_background.change, () => {
      this._vtk_renwin
        .getRenderer()
        .setBackground(...hexToRGB(this.model.render_background))
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.interpolation.change, () => {
      this._set_interpolation(this.model.interpolation)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.controller_expanded.change, () => {
      if (this._controllerWidget != null)
        this._controllerWidget.setExpanded(this.model.controller_expanded)
    })
    this.connect(this.model.properties.nan_opacity.change, () => {
      const scalar_opacity = this.image_actor_i.getProperty().getScalarOpacity()
      scalar_opacity.get(["nodes"]).nodes[0].y = this.model.nan_opacity
      scalar_opacity.modified()
      this._vtk_renwin.getRenderWindow().render()
    })
  }

  render(): void {
    this._vtk_renwin = null
    this._orientationWidget = null
    this._axes = null
    super.render()
    this._create_orientation_widget()
    this._set_axes()
    if (!this.model.camera)
      this._vtk_renwin.getRenderer().resetCamera()
    else
      this._set_camera_state()
    this._get_camera_state()
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
    this._controllerWidget = vtkns.VolumeController.newInstance({
      size: [400, 150],
      rescaleColorMap: this.model.rescale,
    })
    this._plot_volume()
    this._plot_slices()
    this._controllerWidget.setupContent(
      this._vtk_renwin.getRenderWindow(),
      this.volume,
      true
    )
    this._controllerWidget.setContainer(this.el)
    this._controllerWidget.setExpanded(this.model.controller_expanded)
    this._connect_js_controls()
    this._vtk_renwin.getRenderWindow().getInteractor()
    this._vtk_renwin.getRenderWindow().getInteractor().setDesiredUpdateRate(45)
    this._set_volume_visibility(this.model.display_volume)
    this._set_slices_visibility(this.model.display_slices)
    this._vtk_renwin
      .getRenderer()
      .setBackground(...hexToRGB(this.model.render_background))
    this._set_interpolation(this.model.interpolation)
    this._set_camera_state()
  }

  get vtk_image_data(): any {
    if (!this._vtk_image_data)
      this._vtk_image_data = data2VTKImageData(this.model.data as VolumeType)
    return this._vtk_image_data
  }
  get volume(): any {
    return this._vtk_renwin.getRenderer().getVolumes()[0]
  }

  get image_actor_i(): any {
    return this._vtk_renwin.getRenderer().getActors()[0]
  }

  get image_actor_j(): any {
    return this._vtk_renwin.getRenderer().getActors()[1]
  }

  get image_actor_k(): any {
    return this._vtk_renwin.getRenderer().getActors()[2]
  }

  get shadow_selector(): HTMLSelectElement {
    return this.el.querySelector(".js-shadow") as HTMLSelectElement
  }

  get edge_gradient_slider(): HTMLInputElement {
    return this.el.querySelector(".js-edge") as HTMLInputElement
  }

  get sampling_slider(): HTMLInputElement {
    return this.el.querySelector(".js-spacing") as HTMLInputElement
  }

  get colormap_selector(): HTMLSelectElement {
    return this.el.querySelector(".js-color-preset") as HTMLSelectElement
  }

  _connect_js_controls(): void {
    const {el: controller_el} = this._controllerWidget.get('el')
    if(controller_el !== undefined) {
      const controller_button = (controller_el as HTMLElement).querySelector('.js-button')
      controller_button!.addEventListener('click', () => this.model.controller_expanded = this._controllerWidget.getExpanded())
    }
    // Colormap selector
    this.colormap_selector.addEventListener("change", () => {
      this.model.colormap = this.colormap_selector.value
    })
    if (!this.model.colormap) this.model.colormap = this.colormap_selector.value
    else this.model.properties.colormap.change.emit()

    // Shadow selector
    this.shadow_selector.addEventListener("change", () => {
      this.model.shadow = !!Number(this.shadow_selector.value)
    })
    if ((this.model.shadow = !!Number(this.shadow_selector.value)))
      this.model.properties.shadow.change.emit()

    // Sampling slider
    this.sampling_slider.addEventListener("input", () => {
      const js_sampling_value = Number(this.sampling_slider.value)
      if (Math.abs(this.model.sampling - js_sampling_value) >= 5e-3)
        this.model.sampling = js_sampling_value
    })
    if (
      Math.abs(this.model.sampling - Number(this.shadow_selector.value)) >= 5e-3
    )
      this.model.properties.sampling.change.emit()

    // Edge Gradient slider
    this.edge_gradient_slider.addEventListener("input", () => {
      const js_edge_gradient_value = Number(this.edge_gradient_slider.value)
      if (Math.abs(this.model.edge_gradient - js_edge_gradient_value) >= 5e-3)
        this.model.edge_gradient = js_edge_gradient_value
    })
    if (
      Math.abs(
        this.model.edge_gradient - Number(this.edge_gradient_slider.value)
      ) >= 5e-3
    )
      this.model.properties.edge_gradient.change.emit()
  }

  _plot_slices(): void {
    const source = this._vtk_image_data
    const image_actor_i = vtkns.ImageSlice.newInstance()
    const image_actor_j = vtkns.ImageSlice.newInstance()
    const image_actor_k = vtkns.ImageSlice.newInstance()

    const image_mapper_i = vtkns.ImageMapper.newInstance()
    const image_mapper_j = vtkns.ImageMapper.newInstance()
    const image_mapper_k = vtkns.ImageMapper.newInstance()

    image_mapper_i.setInputData(source)
    image_mapper_i.setISlice(this.model.slice_i)
    image_actor_i.setMapper(image_mapper_i)

    image_mapper_j.setInputData(source)
    image_mapper_j.setJSlice(this.model.slice_j)
    image_actor_j.setMapper(image_mapper_j)

    image_mapper_k.setInputData(source)
    image_mapper_k.setKSlice(this.model.slice_k)
    image_actor_k.setMapper(image_mapper_k)

    // set_color and opacity
    const piecewiseFunction = vtkns.PiecewiseFunction.newInstance()
    const lookupTable = this.volume.getProperty().getRGBTransferFunction(0)
    const range = this.volume.getMapper().getInputData().getPointData().getScalars().getRange()
    piecewiseFunction.removeAllPoints()
    piecewiseFunction.addPoint(range[0]-1, this.model.nan_opacity)
    piecewiseFunction.addPoint(range[0], 1)
    piecewiseFunction.addPoint(range[1], 1)

    const property = image_actor_i.getProperty()
    image_actor_j.setProperty(property)
    image_actor_k.setProperty(property)

    property.setRGBTransferFunction(lookupTable)
    property.setScalarOpacity(piecewiseFunction)

    const renderer = this._vtk_renwin.getRenderer()
    renderer.addActor(image_actor_i)
    renderer.addActor(image_actor_j)
    renderer.addActor(image_actor_k)
  }

  _plot_volume(): void {
    //Create vtk volume and add it to the scene
    const source = this.vtk_image_data
    const actor = vtkns.Volume.newInstance()
    const mapper = vtkns.VolumeMapper.newInstance()

    actor.setMapper(mapper)
    mapper.setInputData(source)

    const dataArray =
      source.getPointData().getScalars() || source.getPointData().getArrays()[0]
    const dataRange = dataArray.getRange()

    const lookupTable = vtkns.ColorTransferFunction.newInstance()
    lookupTable.onModified(
      () => (this.model.mapper = vtkLutToMapper(lookupTable))
    )
    const piecewiseFunction = vtkns.PiecewiseFunction.newInstance()
    const sampleDistance =
      0.7 *
      Math.sqrt(
        source
          .getSpacing()
          .map((v: number) => v * v)
          .reduce((a: number, b: number) => a + b, 0)
      )
    mapper.setSampleDistance(sampleDistance)

    actor.getProperty().setRGBTransferFunction(0, lookupTable)
    actor.getProperty().setScalarOpacity(0, piecewiseFunction)
    actor.getProperty().setInterpolationTypeToFastLinear()
    // actor.getProperty().setInterpolationTypeToLinear();

    // For better looking volume rendering
    // - distance in world coordinates a scalar opacity of 1.0
    actor
      .getProperty()
      .setScalarOpacityUnitDistance(
        0,
        vtkns.BoundingBox.getDiagonalLength(source.getBounds()) /
          Math.max(...source.getDimensions())
      )
    // - control how we emphasize surface boundaries
    //  => max should be around the average gradient magnitude for the
    //     volume or maybe average plus one std dev of the gradient magnitude
    //     (adjusted for spacing, this is a world coordinate gradient, not a
    //     pixel gradient)
    //  => max hack: (dataRange[1] - dataRange[0]) * 0.05
    actor.getProperty().setGradientOpacityMinimumValue(0, 0)
    actor
      .getProperty()
      .setGradientOpacityMaximumValue(0, (dataRange[1] - dataRange[0]) * 0.05)
    // - Use shading based on gradient
    actor.getProperty().setShade(this.model.shadow)
    actor.getProperty().setUseGradientOpacity(0, true)
    // - generic good default
    actor.getProperty().setGradientOpacityMinimumOpacity(0, 0.0)
    actor.getProperty().setGradientOpacityMaximumOpacity(0, 1.0)
    actor.getProperty().setAmbient(this.model.ambient)
    actor.getProperty().setDiffuse(this.model.diffuse)
    actor.getProperty().setSpecular(this.model.specular)
    actor.getProperty().setSpecularPower(this.model.specular_power)

    this._vtk_renwin.getRenderer().addVolume(actor)
  }

  _set_interpolation(interpolation: Interpolation): void {
    if (interpolation == "fast_linear") {
      this.volume.getProperty().setInterpolationTypeToFastLinear()
      this.image_actor_i.getProperty().setInterpolationTypeToLinear()
    } else if (interpolation == "linear") {
      this.volume.getProperty().setInterpolationTypeToLinear()
      this.image_actor_i.getProperty().setInterpolationTypeToLinear()
    } else {
      //nearest
      this.volume.getProperty().setInterpolationTypeToNearest()
      this.image_actor_i.getProperty().setInterpolationTypeToNearest()
    }
  }

  _set_slices_visibility(visibility: boolean): void {
    this.image_actor_i.setVisibility(visibility)
    this.image_actor_j.setVisibility(visibility)
    this.image_actor_k.setVisibility(visibility)
  }

  _set_volume_visibility(visibility: boolean): void {
    this.volume.setVisibility(visibility)
  }
}

export namespace VTKVolumePlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = AbstractVTKPlot.Props & {
    ambient: p.Property<number>
    colormap: p.Property<string>
    diffuse: p.Property<number>
    display_slices: p.Property<boolean>
    display_volume: p.Property<boolean>
    edge_gradient: p.Property<number>
    interpolation: p.Property<Interpolation>
    mapper: p.Property<ColorMapper>
    nan_opacity: p.Property<number>
    render_background: p.Property<string>
    rescale: p.Property<boolean>
    sampling: p.Property<number>
    shadow: p.Property<boolean>
    slice_i: p.Property<number>
    slice_j: p.Property<number>
    slice_k: p.Property<number>
    specular: p.Property<number>
    specular_power: p.Property<number>
    controller_expanded: p.Property<boolean>
  }
}

export interface VTKVolumePlot extends VTKVolumePlot.Attrs {}

export class VTKVolumePlot extends AbstractVTKPlot {
  properties: VTKVolumePlot.Props

  constructor(attrs?: Partial<VTKVolumePlot.Attrs>) {
    super(attrs)
  }

  static init_VTKVolumePlot(): void {
    this.prototype.default_view = VTKVolumePlotView

    this.define<VTKVolumePlot.Props>(({Any, Array, Boolean, Int, Number, String, Struct}) => ({
      ambient:              [ Number,            0.2 ],
      colormap:             [ String                 ],
      data:                 [ Any                    ],
      diffuse:              [ Number,            0.7 ],
      display_slices:       [ Boolean,         false ],
      display_volume:       [ Boolean,          true ],
      edge_gradient:        [ Number,            0.2 ],
      interpolation:        [ Interpolation, 'fast_linear'],
      mapper:               [ Struct({palette: Array(String), low: Number, high: Number}) ],
      nan_opacity:          [ Number,              1 ],
      render_background:    [ String,      '#52576e' ],
      rescale:              [ Boolean,         false ],
      sampling:             [ Number,            0.4 ],
      shadow:               [ Boolean,          true ],
      slice_i:              [ Int,               0   ],
      slice_j:              [ Int,               0   ],
      slice_k:              [ Int,               0   ],
      specular:             [ Number,            0.3 ],
      specular_power:       [ Number,            8.0 ],
      controller_expanded:  [ Boolean,          true ],
    }))
  }
}
