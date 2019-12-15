export const vtk = (window as any).vtk

export const vtkns: any = {}

if (vtk) {
  vtkns['LineSource'] = vtk.Filters.Sources.vtkLineSource
  vtkns['PlaneSource'] = vtk.Filters.Sources.vtkPlaneSource
  vtkns['PointSource'] = vtk.Filters.Sources.vtkPointSource
  vtkns['SphereMapper'] = vtk.Rendering.Core.vtkSphereMapper
  vtkns['CubeSource'] = vtk.Filters.Sources.vtkCubeSource
  vtkns['OrientationMarkerWidget'] = vtk.Interaction.Widgets.vtkOrientationMarkerWidget
  vtkns['WidgetManager'] = vtk.Widgets.Core.vtkWidgetManager
  vtkns['InteractiveOrientationWidget'] = vtk.Widgets.Widgets3D.vtkInteractiveOrientationWidget
  vtkns['OutlineFilter'] = vtk.Filters.General.vtkOutlineFilter
  vtkns['DataAccessHelper'] = vtk.IO.Core.DataAccessHelper
  vtkns['HttpSceneLoader'] = vtk.IO.Core.vtkHttpSceneLoader
  vtkns['AxesActor'] = vtk.Rendering.Core.vtkAxesActor
  vtkns['Mapper'] = vtk.Rendering.Core.vtkMapper
  vtkns['Actor'] = vtk.Rendering.Core.vtkActor
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
