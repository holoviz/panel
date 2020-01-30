import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {VTKHTMLBoxView} from "./vtk_layout"
import {VolumeType, vtkns, data2VTKImageData } from "./vtk_utils"

export class VTKVolumePlotView extends VTKHTMLBoxView {
  model: VTKVolumePlot
  protected _controllerWidget: any

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => {
      this.invalidate_render()
    })
    this.connect(this.model.properties.colormap.change, () => {
      this.colormap_slector.value = this.model.colormap
      const event = new Event('change');
      this.colormap_slector.dispatchEvent(event);
    })
    this.connect(this.model.properties.shadow.change, () => {
      this.shadow_selector.value = this.model.shadow? '1': '0'
      const event = new Event('change');
      this.shadow_selector.dispatchEvent(event);
    })
    this.connect(this.model.properties.sampling.change, () => {
      this.sampling_slider.value = this.model.sampling.toFixed(2)
      const event = new Event('input');
      this.sampling_slider.dispatchEvent(event);
    })
    this.connect(this.model.properties.edge_gradient.change, () => {
      this.edge_gradient_slider.value = this.model.edge_gradient.toFixed(2)
      const event = new Event('input');
      this.edge_gradient_slider.dispatchEvent(event);
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
  }

  get volume(): any {
    return this._controllerWidget.getActor()
  }

  get shadow_selector(): HTMLSelectElement{
    return (this.el.querySelector('.js-shadow') as HTMLSelectElement)
  }

  get edge_gradient_slider(): HTMLInputElement{
    return (this.el.querySelector('.js-edge') as HTMLInputElement)
  }

  get sampling_slider(): HTMLInputElement{
    return (this.el.querySelector('.js-spacing') as HTMLInputElement)
  }

  get colormap_slector(): HTMLSelectElement{
    return (this.el.querySelector('.js-color-preset') as HTMLSelectElement)
  }

  render(): void {
    super.render()
    this._controllerWidget = vtkns.VolumeController.newInstance({
      size: [400, 150],
      rescaleColorMap: this.model.rescale,
    })
    this._controllerWidget.setContainer(this.el)
    this._vtk_renwin.getRenderWindow().getInteractor()
    this._vtk_renwin.getRenderWindow().getInteractor().setDesiredUpdateRate(45)
    this._plot()
    this.colormap_slector.addEventListener('change', () => {
      this.model.colormap = this.colormap_slector.value
    })
    if (!this.model.colormap)
      this.model.colormap = this.colormap_slector.value
    else
      this.model.properties.colormap.change.emit()
    this._vtk_renwin.getRenderer().resetCamera()
  }

  _plot(): void {
    //Create vtk volume and add it to the scene
    const source = data2VTKImageData(this.model.data)
    const actor = vtkns.Volume.newInstance()
    const mapper = vtkns.VolumeMapper.newInstance()

    actor.setMapper(mapper)
    mapper.setInputData(source)

    const dataArray = source.getPointData().getScalars() || source.getPointData().getArrays()[0]
    const dataRange = dataArray.getRange()

    const lookupTable = vtkns.ColorTransferFunction.newInstance()
    const piecewiseFunction =vtkns.PiecewiseFunction.newInstance()
    const sampleDistance = 0.7 * Math.sqrt(source.getSpacing()
                                                 .map((v: number) => v * v)
                                                 .reduce((a: number, b: number) => a + b, 0));
    mapper.setSampleDistance(sampleDistance);

    actor.getProperty().setRGBTransferFunction(0, lookupTable);
    actor.getProperty().setScalarOpacity(0, piecewiseFunction);
    actor.getProperty().setInterpolationTypeToFastLinear();
    // actor.getProperty().setInterpolationTypeToLinear();

    // For better looking volume rendering
    // - distance in world coordinates a scalar opacity of 1.0
    actor
      .getProperty()
      .setScalarOpacityUnitDistance(
        0,
        vtkns.BoundingBox.getDiagonalLength(source.getBounds()) /
          Math.max(...source.getDimensions())
      );
    // - control how we emphasize surface boundaries
    //  => max should be around the average gradient magnitude for the
    //     volume or maybe average plus one std dev of the gradient magnitude
    //     (adjusted for spacing, this is a world coordinate gradient, not a
    //     pixel gradient)
    //  => max hack: (dataRange[1] - dataRange[0]) * 0.05
    actor.getProperty().setGradientOpacityMinimumValue(0, 0);
    actor
      .getProperty()
      .setGradientOpacityMaximumValue(0, (dataRange[1] - dataRange[0]) * 0.05);
    // - Use shading based on gradient
    actor.getProperty().setShade(this.model.shadow);
    actor.getProperty().setUseGradientOpacity(0, true);
    // - generic good default
    actor.getProperty().setGradientOpacityMinimumOpacity(0, 0.0);
    actor.getProperty().setGradientOpacityMaximumOpacity(0, 1.0);
    actor.getProperty().setAmbient(this.model.ambient);
    actor.getProperty().setDiffuse(this.model.diffuse);
    actor.getProperty().setSpecular(this.model.specular);
    actor.getProperty().setSpecularPower(this.model.specular_power);

    this._vtk_renwin.getRenderer().addVolume(actor)
    this._controllerWidget.setupContent(this._vtk_renwin.getRenderWindow(), actor, true)
  }
}

export namespace VTKVolumePlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<VolumeType>,
    shadow: p.Property<boolean>,
    sampling: p.Property<number>,
    edge_gradient: p.Property<number>,
    colormap: p.Property<string>,
    rescale: p.Property<boolean>,
    ambient: p.Property<number>,
    diffuse: p.Property<number>,
    specular: p.Property<number>,
    specular_power: p.Property<number>,
  }
}

export interface VTKVolumePlot extends VTKVolumePlot.Attrs {}

export class VTKVolumePlot extends HTMLBox {
  properties: VTKVolumePlot.Props

  constructor(attrs?: Partial<VTKVolumePlot.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.vtk"

  static init_VTKVolumePlot(): void {
    this.prototype.default_view = VTKVolumePlotView

    this.define<VTKVolumePlot.Props>({
      data:             [ p.Instance       ],
      shadow:           [ p.Boolean,  true ],
      sampling:         [ p.Number,    0.4 ],
      edge_gradient:    [ p.Number,    0.2 ],
      colormap:         [ p.String         ],
      rescale:          [ p.Boolean, false ],
      ambient:          [ p.Number,    0.2 ],
      diffuse:          [ p.Number,    0.7 ],
      specular:         [ p.Number,    0.3 ],
      specular_power:   [ p.Number,    8.0 ],
    })

    this.override({
      height: 300,
      width: 300
    });
  }
}
