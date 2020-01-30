import * as p from "@bokehjs/core/properties"
import {ARRAY_TYPES, DType} from "@bokehjs/core/util/serialization"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {vtkns} from "./vtk_utils"
import {VTKHTMLBoxView} from "./vtk_layout"



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

export class VTKSlicerPlotView extends VTKHTMLBoxView {
  model: VTKSlicerPlot
  protected _imageMapperI: any
  protected _imageMapperJ: any
  protected _imageMapperK: any

  connect_signals(): void{
    super.connect_signals()
    this.connect(this.model.properties.slice_I.change, () => {
      this._imageMapperI.setISlice(this.model.slice_I)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.slice_J.change, () => {
      this._imageMapperJ.setJSlice(this.model.slice_J)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.slice_K.change, () => {
      this._imageMapperK.setKSlice(this.model.slice_K)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.color_level.change, () => {
      this.model.image_actor_I.getProperty().setColorLevel(this.model.color_level)
      this.model.image_actor_J.getProperty().setColorLevel(this.model.color_level)
      this.model.image_actor_K.getProperty().setColorLevel(this.model.color_level)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.color_window.change, () => {
      this.model.image_actor_I.getProperty().setColorWindow(this.model.color_window)
      this.model.image_actor_J.getProperty().setColorWindow(this.model.color_window)
      this.model.image_actor_K.getProperty().setColorWindow(this.model.color_window)
      this._vtk_renwin.getRenderWindow().render()
    })
    this.connect(this.model.properties.data.change, () => {
      this._plot()
      this._vtk_renwin.getRenderWindow().render()
    })
  }

  render(): void {
    super.render()
    this._imageMapperI = vtkns.ImageMapper.newInstance()
    this._imageMapperJ = vtkns.ImageMapper.newInstance()
    this._imageMapperK = vtkns.ImageMapper.newInstance()
    this._plot()
  }

  _create_source(): any{
    const data = this.model.data
    const source = vtkns.ImageData.newInstance({
      spacing: data.spacing
    })
    source.setDimensions(data.dims)
    source.setOrigin(data.origin != null ? data.origin : data.dims.map((v: number) => v/2))
    const dataArray = vtkns.DataArray.newInstance({
      name: "scalars",
      numberOfComponents: 1,
      values: new ARRAY_TYPES[data.dtype as DType](utf8ToAB(atob(data.buffer)))
    })
    source.getPointData().setScalars(dataArray)
    return source
  }

  _plot(): void {
    //Create convert data in vtkImageData and create the 3 slices
    const source = this._create_source()
    this.model.image_actor_I = vtkns.ImageSlice.newInstance()
    this.model.image_actor_J = vtkns.ImageSlice.newInstance()
    this.model.image_actor_K = vtkns.ImageSlice.newInstance()

    this._imageMapperI.setInputData(source)
    this._imageMapperI.setISlice(this.model.slice_I)
    this.model.image_actor_I.setMapper(this._imageMapperI)

    this._imageMapperJ.setInputData(source)
    this._imageMapperJ.setJSlice(this.model.slice_J)
    this.model.image_actor_J.setMapper(this._imageMapperJ)

    this._imageMapperK.setInputData(source)
    this._imageMapperK.setKSlice(this.model.slice_K)
    this.model.image_actor_K.setMapper(this._imageMapperK)

    const renderer = this._vtk_renwin.getRenderer()
    renderer.addActor(this.model.image_actor_I)
    renderer.addActor(this.model.image_actor_J)
    renderer.addActor(this.model.image_actor_K)

    // ToDo in make in params
    this.model.image_actor_I.getProperty().setColorLevel(this.model.color_level)
    this.model.image_actor_J.getProperty().setColorLevel(this.model.color_level)
    this.model.image_actor_K.getProperty().setColorLevel(this.model.color_level)

    this.model.image_actor_I.getProperty().setColorWindow(this.model.color_window)
    this.model.image_actor_J.getProperty().setColorWindow(this.model.color_window)
    this.model.image_actor_K.getProperty().setColorWindow(this.model.color_window)

    renderer.resetCamera()
  }
}

export namespace VTKSlicerPlot {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    data: p.Property<VolumeType>,
    image_actor_I: p.Property<any>,
    image_actor_J: p.Property<any>,
    image_actor_K: p.Property<any>,
    slice_I: p.Property<number>,
    slice_J: p.Property<number>,
    slice_K: p.Property<number>,
    color_window: p.Property<number>,
    color_level: p.Property<number>,
  }
}

export interface VTKSlicerPlot extends VTKSlicerPlot.Attrs {}

export class VTKSlicerPlot extends HTMLBox {
  properties: VTKSlicerPlot.Props

  constructor(attrs?: Partial<VTKSlicerPlot.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.vtk"

  static init_VTKSlicerPlot(): void {
    this.prototype.default_view = VTKSlicerPlotView

    this.define<VTKSlicerPlot.Props>({
      data:     [ p.Any ],
      image_actor_I: [ p.Any ],
      image_actor_J: [ p.Any ],
      image_actor_K: [ p.Any ],
      slice_I:  [ p.Number, 0 ],
      slice_J:  [ p.Number, 0 ],
      slice_K:  [ p.Number, 0 ],
      color_window: [ p.Number, 1 ],
      color_level: [ p.Number, 0.5 ]
    })

    this.override({
      height: 300,
      width: 300
    });
  }
}
