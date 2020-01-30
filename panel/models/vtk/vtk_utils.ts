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
