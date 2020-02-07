import {ARRAY_TYPES, DType} from "@bokehjs/core/util/serialization"
import {linspace} from "@bokehjs/core/util/array"

export const vtk = (window as any).vtk

export const vtkns: any = {}

if (vtk) {
  vtkns['DataArray'] = vtk.Common.Core.vtkDataArray
  vtkns['ImageData'] = vtk.Common.DataModel.vtkImageData
  vtkns['OutlineFilter'] = vtk.Filters.General.vtkOutlineFilter
  vtkns['CubeSource'] = vtk.Filters.Sources.vtkCubeSource
  vtkns['LineSource'] = vtk.Filters.Sources.vtkLineSource
  vtkns['PlaneSource'] = vtk.Filters.Sources.vtkPlaneSource
  vtkns['PointSource'] = vtk.Filters.Sources.vtkPointSource
  vtkns['OrientationMarkerWidget'] = vtk.Interaction.Widgets.vtkOrientationMarkerWidget
  vtkns['DataAccessHelper'] = vtk.IO.Core.DataAccessHelper
  vtkns['HttpSceneLoader'] = vtk.IO.Core.vtkHttpSceneLoader
  vtkns['ImageSlice'] = vtk.Rendering.Core.vtkImageSlice
  vtkns['Actor'] = vtk.Rendering.Core.vtkActor
  vtkns['AxesActor'] = vtk.Rendering.Core.vtkAxesActor
  vtkns['Mapper'] = vtk.Rendering.Core.vtkMapper
  vtkns['ImageMapper'] = vtk.Rendering.Core.vtkImageMapper
  vtkns['SphereMapper'] = vtk.Rendering.Core.vtkSphereMapper
  vtkns['WidgetManager'] = vtk.Widgets.Core.vtkWidgetManager
  vtkns['InteractiveOrientationWidget'] = vtk.Widgets.Widgets3D.vtkInteractiveOrientationWidget
  vtkns['PixelSpaceCallbackMapper'] = vtk.Rendering.Core.vtkPixelSpaceCallbackMapper
  vtkns['FullScreenRenderWindow'] = vtk.Rendering.Misc.vtkFullScreenRenderWindow
  vtkns['VolumeController'] = vtk.Interaction.UI.vtkVolumeController
  vtkns['Volume'] = vtk.Rendering.Core.vtkVolume
  vtkns['VolumeMapper'] = vtk.Rendering.Core.vtkVolumeMapper
  vtkns['ColorTransferFunction'] = vtk.Rendering.Core.vtkColorTransferFunction
  vtkns['PiecewiseFunction'] = vtk.Common.DataModel.vtkPiecewiseFunction
  vtkns['BoundingBox'] = vtk.Common.DataModel.vtkBoundingBox
}

export type VolumeType = {
  buffer: string
  dims: number[]
  dtype: DType
  spacing: number[]
  origin: number[] | null
  extent: number[] | null
}

export function hexToRGB(color: string): number[] {
  return [parseInt(color.slice(1,3),16)/255,
          parseInt(color.slice(3,5),16)/255,
          parseInt(color.slice(5,7),16)/255]
}

function valToHex(val: number): string {
  const hex = Math.min(Math.max(Math.round(val),0),255).toString(16)
  return hex.length == 2 ? hex : "0" + hex
}

export function rgbToHex(r: number, g: number, b:number): string {
  return '#' + valToHex(r) + valToHex(g) + valToHex(b)
}

declare type node = {
  x: number,
  r: number,
  g: number,
  b: number
}

export declare type Mapper = {
  palette: string[],
  low: number,
  high: number,
}

export function vtkLutToMapper(vtk_lut: any):  Mapper {
  //For the moment only linear colormapper are handle
  const {scale, nodes} = vtk_lut.get('scale', 'nodes')
  if (scale !== vtkns.ColorTransferFunction.Scale.LINEAR)
    throw ('Error transfer function scale not handle')
  const n_nodes = nodes.length
  const x = (nodes as node[]).map((a: node) => a.x)
  const low = Math.min(...x)
  const high = Math.max(...x)
  const vals = linspace(low, high, n_nodes)
  const rgb = [0, 0, 0]
  const palette = (vals).map((val) => {
    vtk_lut.getColor(val, rgb)
    return rgbToHex((rgb[0]*255), (rgb[1]*255), (rgb[2]*255))
  })
  return {low, high, palette}
}


function utf8ToAB(utf8_str: string): ArrayBuffer {
  var buf = new ArrayBuffer(utf8_str.length) // 2 bytes for each char
  var bufView = new Uint8Array(buf)
  for (var i=0, strLen=utf8_str.length; i<strLen; i++) {
    bufView[i] = utf8_str.charCodeAt(i)
  }
  return buf
}

export function data2VTKImageData(data: VolumeType): any{
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


export function majorAxis(vec3: number[], idxA: number, idxB: number): number[] {
  const axis = [0, 0, 0]
  const idx = Math.abs(vec3[idxA]) > Math.abs(vec3[idxB]) ? idxA : idxB
  const value = vec3[idx] > 0 ? 1 : -1
  axis[idx] = value
  return axis
}

export function cartesian_product(...arrays: any){
  return arrays.reduce((acc: any, curr: any) =>
  acc.flatMap((c: any) => curr.map((n: any) => [].concat(c, n)))
  );
}
