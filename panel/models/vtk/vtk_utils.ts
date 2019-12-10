export const vtk = (window as any).vtk
export const vtkLineSource = vtk.Filters.Sources.vtkLineSource
export const vtkPlaneSource = vtk.Filters.Sources.vtkPlaneSource
export const vtkPointSource = vtk.Filters.Sources.vtkPointSource
export const vtkSphereMapper = vtk.Rendering.Core.vtkSphereMapper
export const vtkCubeSource = vtk.Filters.Sources.vtkCubeSource
export const vtkOrientationMarkerWidget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget
export const vtkWidgetManager = vtk.Widgets.Core.vtkWidgetManager
export const vtkInteractiveOrientationWidget = vtk.Widgets.Widgets3D.vtkInteractiveOrientationWidget
export const vtkOutlineFilter = vtk.Filters.General.vtkOutlineFilter
export const vtkDataAccessHelper = vtk.IO.Core.DataAccessHelper
export const vtkHttpSceneLoader = vtk.IO.Core.vtkHttpSceneLoader
export const vtkAxesActor = vtk.Rendering.Core.vtkAxesActor
export const vtkMapper = vtk.Rendering.Core.vtkMapper
export const vtkActor = vtk.Rendering.Core.vtkActor
export const vtkPixelSpaceCallbackMapper = vtk.Rendering.Core.vtkPixelSpaceCallbackMapper
export const vtkFullScreenRenderWindow =vtk.Rendering.Misc.vtkFullScreenRenderWindow

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
