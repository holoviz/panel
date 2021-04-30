import {linspace} from "@bokehjs/core/util/array"
import {Enum} from "@bokehjs/core/kinds"

export const ARRAY_TYPES = {
  uint8:   Uint8Array,
  int8:    Int8Array,
  uint16:  Uint16Array,
  int16:   Int16Array,
  uint32:  Uint32Array,
  int32:   Int32Array,
  float32: Float32Array,
  float64: Float64Array,
}

export type DType = keyof typeof ARRAY_TYPES

export const vtk = (window as any).vtk

export const vtkns: any = {}

if (vtk) {
  vtkns["Actor"] = vtk.Rendering.Core.vtkActor
  vtkns["AxesActor"] = vtk.Rendering.Core.vtkAxesActor
  vtkns["Base64"] = vtk.Common.Core.vtkBase64
  vtkns["BoundingBox"] = vtk.Common.DataModel.vtkBoundingBox
  vtkns["Camera"] = vtk.Rendering.Core.vtkCamera
  vtkns["ColorTransferFunction"] = vtk.Rendering.Core.vtkColorTransferFunction
  vtkns["CubeSource"] = vtk.Filters.Sources.vtkCubeSource
  vtkns["DataAccessHelper"] = vtk.IO.Core.DataAccessHelper
  vtkns["DataArray"] = vtk.Common.Core.vtkDataArray
  vtkns["Follower"] = vtk.Rendering.Core.vtkFollower
  vtkns["FullScreenRenderWindow"] = vtk.Rendering.Misc.vtkFullScreenRenderWindow
  vtkns["Glyph3DMapper"] = vtk.Rendering.Core.vtkGlyph3DMapper
  vtkns["HttpSceneLoader"] = vtk.IO.Core.vtkHttpSceneLoader
  vtkns["ImageData"] = vtk.Common.DataModel.vtkImageData
  vtkns["ImageMapper"] = vtk.Rendering.Core.vtkImageMapper
  vtkns["ImageProperty"] = vtk.Rendering.Core.vtkImageProperty
  vtkns["ImageSlice"] = vtk.Rendering.Core.vtkImageSlice
  vtkns["InteractiveOrientationWidget"] =
    vtk.Widgets.Widgets3D.vtkInteractiveOrientationWidget
  vtkns["InteractorStyleTrackballCamera"] =
    vtk.Interaction.Style.vtkInteractorStyleTrackballCamera
  vtkns["Light"] = vtk.Rendering.Core.vtkLight
  vtkns["LineSource"] = vtk.Filters.Sources.vtkLineSource
  vtkns["LookupTable"] = vtk.Common.Core.vtkLookupTable
  vtkns["macro"] = vtk.macro
  vtkns["Mapper"] = vtk.Rendering.Core.vtkMapper
  vtkns["OpenGLRenderWindow"] = vtk.Rendering.OpenGL.vtkRenderWindow
  vtkns["OrientationMarkerWidget"] =
    vtk.Interaction.Widgets.vtkOrientationMarkerWidget
  vtkns["OutlineFilter"] = vtk.Filters.General.vtkOutlineFilter
  vtkns["PiecewiseFunction"] = vtk.Common.DataModel.vtkPiecewiseFunction
  vtkns["PixelSpaceCallbackMapper"] =
    vtk.Rendering.Core.vtkPixelSpaceCallbackMapper
  vtkns["PlaneSource"] = vtk.Filters.Sources.vtkPlaneSource
  vtkns["PointSource"] = vtk.Filters.Sources.vtkPointSource
  vtkns["PolyData"] = vtk.Common.DataModel.vtkPolyData
  vtkns["Property"] = vtk.Rendering.Core.vtkProperty
  vtkns["Renderer"] = vtk.Rendering.Core.vtkRenderer
  vtkns["RenderWindow"] = vtk.Rendering.Core.vtkRenderWindow
  vtkns["RenderWindowInteractor"] = vtk.Rendering.Core.vtkRenderWindowInteractor
  vtkns["SphereMapper"] = vtk.Rendering.Core.vtkSphereMapper
  vtkns["SynchronizableRenderWindow"] =
    vtk.Rendering.Misc.vtkSynchronizableRenderWindow
  vtkns["ThirdParty"] = vtk.ThirdParty
  vtkns["Texture"] = vtk.Rendering.Core.vtkTexture
  vtkns["Volume"] = vtk.Rendering.Core.vtkVolume
  vtkns["VolumeController"] = vtk.Interaction.UI.vtkVolumeController
  vtkns["VolumeMapper"] = vtk.Rendering.Core.vtkVolumeMapper
  vtkns["VolumeProperty"] = vtk.Rendering.Core.vtkVolumeProperty
  vtkns["WidgetManager"] = vtk.Widgets.Core.vtkWidgetManager

  const {vtkObjectManager} = vtkns.SynchronizableRenderWindow

  vtkObjectManager.setTypeMapping(
    "vtkVolumeMapper",
    vtkns.VolumeMapper.newInstance,
    vtkObjectManager.oneTimeGenericUpdater
  )
  vtkObjectManager.setTypeMapping(
    "vtkSmartVolumeMapper",
    vtkns.VolumeMapper.newInstance,
    vtkObjectManager.oneTimeGenericUpdater
  )
  vtkObjectManager.setTypeMapping(
    "vtkFollower",
    vtkns.Follower.newInstance,
    vtkObjectManager.genericUpdater
  )
  vtkObjectManager.setTypeMapping(
    "vtkOpenGLGlyph3DMapper",
    vtkns.Glyph3DMapper.newInstance,
    vtkObjectManager.genericUpdater
  )
}

declare type RGBnode = {
  x: number
  r: number
  g: number
  b: number
}

export type ColorMapper = {
  palette: string[]
  low: number
  high: number
}


export const Interpolation = Enum("fast_linear", "linear", "nearest")
export type Interpolation = typeof Interpolation["__type__"]

export type Annotation = {
  id: string
  viewport: number[]
  fontSize: number
  fontFamily: string
  color: number[]
  LowerLeft?: string
  LowerRight?: string
  UpperLeft?: string
  UpperRight?: string
  LowerEdge?: string
  RightEdge?: string
  LeftEdge?: string
  UpperEdge?: string
}

export declare type CSSProperties = {[key: string]: string}

export declare type VolumeType = {
  buffer: string
  dims: number[]
  dtype: DType
  spacing: number[]
  origin: number[] | null
  extent: number[] | null
}

export function applyStyle(el: HTMLElement, style: CSSProperties) {
  Object.keys(style).forEach((key: any) => {
    el.style[key] = style[key]
  })
}

export function hexToRGB(color: string): number[] {
  return [
    parseInt(color.slice(1, 3), 16) / 255,
    parseInt(color.slice(3, 5), 16) / 255,
    parseInt(color.slice(5, 7), 16) / 255,
  ]
}

function valToHex(val: number): string {
  const hex = Math.min(Math.max(Math.round(val), 0), 255).toString(16)
  return hex.length == 2 ? hex : "0" + hex
}

export function rgbToHex(r: number, g: number, b: number): string {
  return "#" + valToHex(r) + valToHex(g) + valToHex(b)
}

export function vtkLutToMapper(vtk_lut: any): ColorMapper {
  //For the moment only linear colormapper are handle
  const {scale, nodes} = vtk_lut.get("scale", "nodes")
  if (scale !== vtkns.ColorTransferFunction.Scale.LINEAR)
    throw "Error transfer function scale not handle"
  const x = (nodes as RGBnode[]).map((a: RGBnode) => a.x)
  const low = Math.min(...x)
  const high = Math.max(...x)
  const vals = linspace(low, high, 255)
  const rgb = [0, 0, 0]
  const palette = vals.map((val) => {
    vtk_lut.getColor(val, rgb)
    return rgbToHex(rgb[0] * 255, rgb[1] * 255, rgb[2] * 255)
  })
  return {low, high, palette}
}

function utf8ToAB(utf8_str: string): ArrayBuffer {
  var buf = new ArrayBuffer(utf8_str.length) // 2 bytes for each char
  var bufView = new Uint8Array(buf)
  for (var i = 0, strLen = utf8_str.length; i < strLen; i++) {
    bufView[i] = utf8_str.charCodeAt(i)
  }
  return buf
}

export function data2VTKImageData(data: VolumeType): any {
  const source = vtkns.ImageData.newInstance({
    spacing: data.spacing,
  })
  source.setDimensions(data.dims)
  source.setOrigin(
    data.origin != null ? data.origin : data.dims.map((v: number) => v / 2)
  )
  const dataArray = vtkns.DataArray.newInstance({
    name: "scalars",
    numberOfComponents: 1,
    values: new ARRAY_TYPES[data.dtype as DType](utf8ToAB(atob(data.buffer))),
  })
  source.getPointData().setScalars(dataArray)
  return source
}

export function majorAxis(
  vec3: number[],
  idxA: number,
  idxB: number
): number[] {
  const axis = [0, 0, 0]
  const idx = Math.abs(vec3[idxA]) > Math.abs(vec3[idxB]) ? idxA : idxB
  const value = vec3[idx] > 0 ? 1 : -1
  axis[idx] = value
  return axis
}

export function cartesian_product(...arrays: any) {
  return arrays.reduce((acc: any, curr: any) =>
    acc.flatMap((c: any) => curr.map((n: any) => [].concat(c, n)))
  )
}
