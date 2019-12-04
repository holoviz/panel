
import * as p from "@bokehjs/core/properties"
import {ARRAY_TYPES, DType} from "@bokehjs/core/util/serialization"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"
import {div} from "@bokehjs/core/dom"

const vtk = (window as any).vtk

type VolumeType = {
  buffer: string
  dims: number[]
  dtype: DType
  spacing: number[]
  origin: number[] | null
  extent: number[] | null
}

function utf8ToAB(utf8_str: string): ArrayBuffer {
  var buf = new ArrayBuffer(utf8_str.length) // 2 bytes for each char
  var bufView = new Uint8Array(buf)
  for (var i=0, strLen=utf8_str.length; i<strLen; i++) {
    bufView[i] = utf8_str.charCodeAt(i)
  }
  return buf
}

export class VTKVolumePlotView extends HTMLBoxView {
  model: VTKVolumePlot
  protected _container: HTMLDivElement
  protected _rendererEl: any
  protected _controllerWidget: any

  after_layout(): void{
    if (!this._rendererEl) {
      this._controllerWidget = vtk.Interaction.UI.vtkVolumeController.newInstance({
        size: [400, 150],
        rescaleColorMap: false,
      })
      this._controllerWidget.setContainer(this.el)
      this._container = div({
        style: {
          width: "100%",
          height: "100%"
        }
      })
      this.el.appendChild(this._container)
      this._rendererEl = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
        rootContainer: this.el,
        container: this._container
      });
      this._rendererEl.getRenderWindow().getInteractor()
      this._rendererEl.getRenderWindow().getInteractor().setDesiredUpdateRate(45)
      this._plot()
      this._rendererEl.getRenderer().resetCamera()
      this._rendererEl.getRenderWindow().render()
    }
    super.after_layout()
  }

  _create_source(): any{
    const data = this.model.data
    const source = vtk.Common.DataModel.vtkImageData.newInstance({
      spacing: data.spacing
    })
    source.setDimensions(data.dims)
    source.setOrigin(data.origin != null ? data.origin : data.dims.map((v: number) => v/2))
    const dataArray = vtk.Common.Core.vtkDataArray.newInstance({
      name: "scalars",
      numberOfComponents: 1,
      values: new ARRAY_TYPES[data.dtype as DType](utf8ToAB(atob(data.buffer)))
    })
    source.getPointData().setScalars(dataArray)
    return source
  }

  _plot(): void {


    //Create vtk volume and add it to the scene
    const source = this._create_source()
    const actor = vtk.Rendering.Core.vtkVolume.newInstance()
    const mapper = vtk.Rendering.Core.vtkVolumeMapper.newInstance()


    actor.setMapper(mapper)
    mapper.setInputData(source)

    const dataArray = source.getPointData().getScalars() || source.getPointData().getArrays()[0]
    const dataRange = dataArray.getRange()

    const lookupTable = vtk.Rendering.Core.vtkColorTransferFunction.newInstance()
    const piecewiseFunction = vtk.Common.DataModel.vtkPiecewiseFunction.newInstance()
    const sampleDistance = 0.7 * Math.sqrt(source.getSpacing()
                                                  .map((v: number) => v * v)
                                                  .reduce((a: number, b: number) => a + b, 0));
    mapper.setSampleDistance(sampleDistance);

    actor.getProperty().setRGBTransferFunction(0, lookupTable);
    actor.getProperty().setScalarOpacity(0, piecewiseFunction);
    actor.getProperty().setInterpolationTypeToFastLinear();
    //actor.getProperty().setInterpolationTypeToLinear();

    // For better looking volume rendering
    // - distance in world coordinates a scalar opacity of 1.0
    actor
      .getProperty()
      .setScalarOpacityUnitDistance(
        0,
        vtk.Common.DataModel.vtkBoundingBox.getDiagonalLength(source.getBounds()) /
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
    actor.getProperty().setShade(true);
    actor.getProperty().setUseGradientOpacity(0, true);
    // - generic good default
    actor.getProperty().setGradientOpacityMinimumOpacity(0, 0.0);
    actor.getProperty().setGradientOpacityMaximumOpacity(0, 1.0);
    actor.getProperty().setAmbient(0.2);
    actor.getProperty().setDiffuse(0.7);
    actor.getProperty().setSpecular(0.3);
    actor.getProperty().setSpecularPower(8.0);

    this._rendererEl.getRenderer().addVolume(actor)
    this._controllerWidget.setupContent(this._rendererEl.getRenderWindow(), actor, true)
  }
}

export namespace VTKVolumePlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<VolumeType>,
    actor: p.Property<any>
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
      data:     [ p.Any ],
      actor:    [ p.Any ],
    })

    this.override({
      height: 300,
      width: 300
    });
  }
}
