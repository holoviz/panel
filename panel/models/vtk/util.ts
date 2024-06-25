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

export const vtkns: any = {}

export function setup_vtkns(): void {
  if (vtkns.Actor != null) {
    return
  }
  const vtk = (window as any).vtk
  Object.assign(vtkns, {
    Actor: vtk.Rendering.Core.vtkActor,
    AxesActor: vtk.Rendering.Core.vtkAxesActor,
    Base64: vtk.Common.Core.vtkBase64,
    BoundingBox: vtk.Common.DataModel.vtkBoundingBox,
    Camera: vtk.Rendering.Core.vtkCamera,
    ColorTransferFunction: vtk.Rendering.Core.vtkColorTransferFunction,
    CubeSource: vtk.Filters.Sources.vtkCubeSource,
    DataAccessHelper: vtk.IO.Core.DataAccessHelper,
    DataArray: vtk.Common.Core.vtkDataArray,
    Follower: vtk.Rendering.Core.vtkFollower,
    FullScreenRenderWindow: vtk.Rendering.Misc.vtkFullScreenRenderWindow,
    Glyph3DMapper: vtk.Rendering.Core.vtkGlyph3DMapper,
    HttpSceneLoader: vtk.IO.Core.vtkHttpSceneLoader,
    ImageData: vtk.Common.DataModel.vtkImageData,
    ImageMapper: vtk.Rendering.Core.vtkImageMapper,
    ImageProperty: vtk.Rendering.Core.vtkImageProperty,
    ImageSlice: vtk.Rendering.Core.vtkImageSlice,
    InteractiveOrientationWidget: vtk.Widgets.Widgets3D.vtkInteractiveOrientationWidget,
    InteractorStyleTrackballCamera: vtk.Interaction.Style.vtkInteractorStyleTrackballCamera,
    Light: vtk.Rendering.Core.vtkLight,
    LineSource: vtk.Filters.Sources.vtkLineSource,
    LookupTable: vtk.Common.Core.vtkLookupTable,
    macro: vtk.macro,
    Mapper: vtk.Rendering.Core.vtkMapper,
    OpenGLRenderWindow: vtk.Rendering.OpenGL.vtkRenderWindow,
    OrientationMarkerWidget: vtk.Interaction.Widgets.vtkOrientationMarkerWidget,
    OutlineFilter: vtk.Filters.General.vtkOutlineFilter,
    PiecewiseFunction: vtk.Common.DataModel.vtkPiecewiseFunction,
    PixelSpaceCallbackMapper: vtk.Rendering.Core.vtkPixelSpaceCallbackMapper,
    PlaneSource: vtk.Filters.Sources.vtkPlaneSource,
    PointSource: vtk.Filters.Sources.vtkPointSource,
    PolyData: vtk.Common.DataModel.vtkPolyData,
    Property: vtk.Rendering.Core.vtkProperty,
    Renderer: vtk.Rendering.Core.vtkRenderer,
    RenderWindow: vtk.Rendering.Core.vtkRenderWindow,
    RenderWindowInteractor: vtk.Rendering.Core.vtkRenderWindowInteractor,
    SphereMapper: vtk.Rendering.Core.vtkSphereMapper,
    SynchronizableRenderWindow: vtk.Rendering.Misc.vtkSynchronizableRenderWindow,
    Texture: vtk.Rendering.Core.vtkTexture,
    Volume: vtk.Rendering.Core.vtkVolume,
    VolumeController: vtk.Interaction.UI.vtkVolumeController,
    VolumeMapper: vtk.Rendering.Core.vtkVolumeMapper,
    VolumeProperty: vtk.Rendering.Core.vtkVolumeProperty,
    WidgetManager: vtk.Widgets.Core.vtkWidgetManager,
  })

  const {vtkObjectManager} = vtkns.SynchronizableRenderWindow

  vtkObjectManager.setTypeMapping(
    "vtkVolumeMapper",
    vtkns.VolumeMapper.newInstance,
    vtkObjectManager.oneTimeGenericUpdater,
  )
  vtkObjectManager.setTypeMapping(
    "vtkSmartVolumeMapper",
    vtkns.VolumeMapper.newInstance,
    vtkObjectManager.oneTimeGenericUpdater,
  )
  vtkObjectManager.setTypeMapping(
    "vtkFollower",
    vtkns.Follower.newInstance,
    vtkObjectManager.genericUpdater,
  )
  vtkObjectManager.setTypeMapping(
    "vtkOpenGLGlyph3DMapper",
    vtkns.Glyph3DMapper.newInstance,
    vtkObjectManager.genericUpdater,
  )
}

if ((window as any).vtk) {
  setup_vtkns()
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
  return hex.length == 2 ? hex : `0${hex}`
}

export function rgbToHex(r: number, g: number, b: number): string {
  return `#${valToHex(r)}${valToHex(g)}${valToHex(b)}`
}

export function vtkLutToMapper(vtk_lut: any): ColorMapper {
  //For the moment only linear colormapper are handle
  const {scale, nodes} = vtk_lut.get("scale", "nodes")
  if (scale !== vtkns.ColorTransferFunction.Scale.LINEAR) {
    throw new Error("Error transfer function scale not handle")
  }
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
  const buf = new ArrayBuffer(utf8_str.length) // 2 bytes for each char
  const bufView = new Uint8Array(buf)
  for (let i = 0, strLen = utf8_str.length; i < strLen; i++) {
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
    data.origin != null ? data.origin : data.dims.map((v: number) => v / 2),
  )
  const dataArray = vtkns.DataArray.newInstance({
    name: "scalars",
    numberOfComponents: 1,
    values: new ARRAY_TYPES[data.dtype](utf8ToAB(atob(data.buffer))),
  })
  source.getPointData().setScalars(dataArray)
  return source
}

export function majorAxis(
  vec3: number[],
  idxA: number,
  idxB: number,
): number[] {
  const axis = [0, 0, 0]
  const idx = Math.abs(vec3[idxA]) > Math.abs(vec3[idxB]) ? idxA : idxB
  const value = vec3[idx] > 0 ? 1 : -1
  axis[idx] = value
  return axis
}

export function cartesian_product(...arrays: any) {
  return arrays.reduce((acc: any, curr: any) => {
    return [...acc].flatMap((c: any) => curr.map((n: any) => [].concat(c, n)))
  })
}
