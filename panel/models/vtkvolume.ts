
import * as p from "core/properties"
import {HTMLBox, HTMLBoxView} from "models/layouts/html_box"
import {div} from "core/dom"
const vtk = (window as any).vtk


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
  

  initialize(): void {
    super.initialize()
    this._container = div({
      style: {
        width: "100%",
        height: "100%"
      }
    });
  }


  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.data.change, () => this._plot())
  }

  render() {
    //create transfer color ui widgets
    super.render()
    this._controllerWidget = vtk.Interaction.UI.vtkVolumeController.newInstance({
      size: [400, 150],
      rescaleColorMap: true,
    })
    this._controllerWidget.setContainer(this.el)
    if (!(this._container === this.el.childNodes[1]))
      this.el.appendChild(this._container)
  }

  after_layout(): void{
    if (!this._rendererEl) {
      this._rendererEl = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
        rootContainer: this.el,
        container: this._container
      });
    }
    this._plot()
  }

  _plot(): void {
    //Read data
    const vtiReader = vtk.IO.XML.vtkXMLImageDataReader.newInstance()
    vtiReader.parseAsArrayBuffer(utf8ToAB(atob(this.model.data)))

    this._rendererEl.getRenderWindow().getInteractor().setDesiredUpdateRate(15)

    //Create vtk volume and add it to the scene
    const actor = vtk.Rendering.Core.vtkVolume.newInstance()
    const source = vtiReader.getOutputData(0)
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
    // actor.getProperty().setInterpolationTypeToFastLinear();
    actor.getProperty().setInterpolationTypeToLinear();

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
    this._rendererEl.setResizeCallback(({ width }: {width: number, height: number}) => {
      // 2px padding + 2x1px boder + 5px edge = 14
      if (width > 414) {
        this._controllerWidget.setSize(400, 150)
      } else {
        this._controllerWidget.setSize(width - 14, 150)
      }
      this._controllerWidget.render()
    })
    this._controllerWidget.setupContent(this._rendererEl.getRenderWindow(), actor, true)
    this._rendererEl.getRenderer().resetCamera()
    this._rendererEl.getRenderWindow().render()
  }
}

export namespace VTKVolumePlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<string>
  }
}

export interface VTKVolumePlot extends VTKVolumePlot.Attrs {}

export class VTKVolumePlot extends HTMLBox {
  properties: VTKVolumePlot.Props

  constructor(attrs?: Partial<VTKVolumePlot.Attrs>) {
    super(attrs)
  }

  static initClass(): void {
    this.prototype.type = "VTKVolumePlot"
    this.prototype.default_view = VTKVolumePlotView

    this.define<VTKVolumePlot.Props>({
      data:               [ p.Instance ],
    })

    this.override({
      height: 300,
      width: 300
    });
  }
}
VTKVolumePlot.initClass()
