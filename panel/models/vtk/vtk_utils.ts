import {ARRAY_TYPES, DType} from "@bokehjs/core/util/serialization"


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
  vtkns['ScalarToRGBA'] = vtk.Filters.General.vtkScalarToRGBA

  const customSliceFilter = vtk.macro.newInstance((publicAPI: any, model: any, initialValues: any = {}) => {
    Object.assign(model, {sliceMode: 'i', sliceIndex: 0}, initialValues);
    vtk.macro.obj(publicAPI, model) // make it an object
    vtk.macro.algo(publicAPI, model, 1, 1) // mixin algorithm code 1 in, 1 out
    vtk.macro.setGet(publicAPI, model, ['sliceIndex', 'sliceMode', 'lookupTable', 'piecewiseFunction']);
    publicAPI.requestData = (inData: any[], outData: any[]) => {
      // implement requestData
      const input = inData[0];
      const scalars = input.getPointData().getScalars()

      const datasetDefinition = input.get('extent', 'spacing', 'origin', 'direction')
      const numberOfComponents = scalars.getNumberOfComponents()
      if (numberOfComponents != 1)
        throw('Invalid input, number of components must be 1')

      const slice = model.sliceIndex
      const {extent} = datasetDefinition
      const shape = [extent[1]-extent[0]+1, extent[3]-extent[2]+1, extent[5]-extent[4]+1]
      let sliceRawArray: number[] //Todo replace by a typed array
      if (model.sliceMode == 'i') {
        datasetDefinition.extent = [slice, slice, ...extent.slice(2,6)]
        const sliceSize = shape[1] * shape[2]
        sliceRawArray = new Array(sliceSize)
        const offset = slice
        let count = 0, index = offset
        while (count < sliceSize){
          sliceRawArray[count] = scalars.getData()[index]
          index += shape[2]
          count++
        }
      } else if (model.sliceMode == 'j') {
        datasetDefinition.extent = [...extent.slice(0,2), slice, slice, ...extent.slice(4,6)]
        const sliceSize = shape[0] * shape[2]
        sliceRawArray = new Array(sliceSize)
        const offset = slice * shape[0]
        let count = 0
        let index = offset
        while (count < sliceSize){
            for(let i=0; i<shape[0]; i++){
              sliceRawArray[count] = scalars.getData()[index + i]
              count++
            }
            index += shape[0] * shape[1]
        }
      } else {
        datasetDefinition.extent = [...extent.slice(0,4), slice, slice]
        const sliceSize = shape[0] * shape[1]
        const offset = sliceSize * slice
        sliceRawArray = scalars.getData().slice(offset, offset + sliceSize)
      }

      const rgba = [0, 0, 0, 0]
      const rgbaArray = new Uint8Array(sliceRawArray.length * 4)
      let offset = 0
      for (let idx = 0; idx < sliceRawArray.length; idx++) {
        const x = sliceRawArray[idx]
        model.lookupTable.getColor(x, rgba)
        // rgba[3] = model.piecewiseFunction.getValue(x) if we want to use transparency
        rgba[3] = 1
        rgbaArray[offset++] = 255 * rgba[0]
        rgbaArray[offset++] = 255 * rgba[1]
        rgbaArray[offset++] = 255 * rgba[2]
        rgbaArray[offset++] = 255 * rgba[3]
      }

      const colorArray = vtkns.DataArray.newInstance({
        name: 'rgba',
        numberOfComponents: 4,
        values: rgbaArray,
      })
      const output = vtkns.ImageData.newInstance(datasetDefinition)
      output.getPointData().setScalars(colorArray)
      outData[0] = output
    }
  })
  vtkns['CustomSliceFilter'] = customSliceFilter
}

export declare type VolumeType = {
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
