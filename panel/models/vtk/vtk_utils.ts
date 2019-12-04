import {mat4, vec3} from 'gl-matrix'

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

function cartesian_product(...arrays: any){
  return arrays.reduce((acc: any, curr: any) =>
  acc.flatMap((c: any) => curr.map((n: any) => [].concat(c, n)))
  );
}

function _make_grid_lines(n: number, m: number, offset: number){
  const out = []
  for (let i = 0; i < n-1;  i++) {
    for (let j = 0; j < m-1;  j++) {
      const v0 = i*m + j + offset
      const v1 = i*m + j + 1 + offset
      const v2 = (i + 1) * m + j + 1 + offset
      const v3 = (i + 1) * m + j + offset
      const line = [5, v0, v1, v2, v3, v0];
      out.push(line)
    }
  }
  return out
}

function _create_grid_axes(origin: number[], xticks: number[], yticks: number[], zticks: number[]){
  const pts = []
  pts.push(cartesian_product(xticks, yticks, [origin[2]])) //xy
  pts.push(cartesian_product([origin[0]], yticks, zticks)) //yz
  pts.push(cartesian_product(xticks, [origin[1]], zticks)) //xz
  
  const polys = []
  let offset = 0
  polys.push(_make_grid_lines(xticks.length, yticks.length, offset)) //xy
  offset += xticks.length * yticks.length
  polys.push(_make_grid_lines(yticks.length, zticks.length, offset)) //yz
  offset += yticks.length * zticks.length
  polys.push(_make_grid_lines(zticks.length, xticks.length, offset)) //zx
  const gridPolyData = vtk({
    vtkClass: 'vtkPolyData',
    points: {
      vtkClass: 'vtkPoints',
      dataType: 'Float32Array',
      numberOfComponents: 3,
      values: (pts as any).flat(2),
    },
    lines: {
      vtkClass: 'vtkCellArray',
      dataType: 'Uint32Array',
      values: (polys as any).flat(2)
    }
  });
  
  const gridMapper = vtkMapper.newInstance();
  const gridActor = vtkActor.newInstance();
  gridMapper.setInputData(gridPolyData);
  gridActor.setMapper(gridMapper);
  gridActor.getProperty().setOpacity(0.1);
  
  return gridActor;
}


export function create_axes(origin: number[], xticks: number[], yticks: number[], zticks: number[], canvas: HTMLCanvasElement){
  const xlen = xticks.length;
  const ylen = yticks.length;
  const zlen = zticks.length;
  const points = ([xticks, yticks, zticks].map((arr, axis) => {
    let coords = null
    switch (axis) {
      case 0:
      coords = cartesian_product(arr, [origin[1]], [origin[2]]);
      break;
      case 1:
      coords = cartesian_product([origin[0]], arr, [origin[2]]);
      break;
      case 2:
      coords = cartesian_product([origin[0]], [origin[1]], arr);
      break;
    }
    return coords
  }) as any).flat(2);
  const axesPolyData = vtk({
    vtkClass: 'vtkPolyData',
    points: {
      vtkClass: 'vtkPoints',
      dataType: 'Float32Array',
      numberOfComponents: 3,
      values: points,
    },
    lines: {
      vtkClass: 'vtkCellArray',
      dataType: 'Uint32Array',
      values: [2, 0, xlen-1, 2, xlen, xlen+ylen-1, 2, xlen+ylen, xlen+ylen+zlen-1]
    }
  });
  const psMapper = vtkPixelSpaceCallbackMapper.newInstance();
  psMapper.setInputData(axesPolyData);
  psMapper.setUseZValues(true);
  psMapper.setCallback((coordsList: number[][], camera: any, aspect: any) => {
    const textCtx = canvas.getContext("2d");
    if (textCtx) {
      const dims = {
        height: canvas.clientHeight * window.devicePixelRatio,
        width: canvas.clientWidth * window.devicePixelRatio
      };
      const dataPoints = psMapper.getInputData().getPoints();
      const viewMatrix = camera.getViewMatrix();
      mat4.transpose(viewMatrix, viewMatrix);
      const projMatrix = camera.getProjectionMatrix(aspect, -1, 1);
      mat4.transpose(projMatrix, projMatrix);
      textCtx.clearRect(0, 0, dims.width, dims.height);
      coordsList.forEach((xy, idx) => {
        const pdPoint = dataPoints.getPoint(idx);
        const vc = vec3.fromValues(pdPoint[0], pdPoint[1], pdPoint[2]);
        vec3.transformMat4(vc, vc, viewMatrix);
        vc[2] += 0.05; // sensibility
        vec3.transformMat4(vc, vc, projMatrix);
        if (vc[2] - 0.001 < xy[3]) {
          textCtx.font = '30px serif';
          textCtx.textAlign = 'center';
          textCtx.textBaseline = 'alphabetic';
          textCtx.fillText(`.`, xy[0], dims.height - xy[1]+2);
          textCtx.font = `${12*window.devicePixelRatio}px serif`;
          textCtx.textAlign = 'right';
          textCtx.textBaseline = 'top';
          let label
          if(idx<xlen)
            label = xticks[idx]
          else if(idx>=xlen && idx<xlen+ylen)
            label = yticks[idx-xlen]
          else
            label = zticks[idx-(xlen+ylen)]
          textCtx.fillText(`${label.toFixed(1)}`, xy[0], dims.height - xy[1]);
        }
      });
    }
  });
  const psActor = vtkActor.newInstance();
  psActor.setMapper(psMapper);
  
  const axesMapper = vtkMapper.newInstance();
  axesMapper.setInputData(axesPolyData)
  const axesActor = vtkActor.newInstance();
  axesActor.setMapper(axesMapper)
  
  const gridActor = _create_grid_axes(origin, xticks, yticks, zticks)
  
  return {psActor, axesActor, gridActor}
}


/*
function flatten(array: number[][]): number[]{
  return [].concat.apply([], array)
}

function cartesian_product(...a: number[][]) { // a = array of array
  let i, j, l, m, a1, o = []
  if (!a || a.length == 0) return a
  
  a1 = a.splice(0, 1)[0]; // the first array of a
  a = cartesian_product(...a)
  for (i = 0, l = a1.length; i < l; i++) {
    if (a && a.length) for (j = 0, m = a.length; j < m; j++)
    o.push([a1[i]].concat(a[j]))
    else
    o.push([a1[i]])
  }
  return o
}

function _make_grid_lines(n: number, m: number, offset: number): number[]{
  const out: number[][] = []
  for (let i = 0; i < n-1;  i++) {
    for (let j = 0; j < m-1;  j++) {
      const v0 = i*m + j + offset
      const v1 = i*m + j + 1 + offset
      const v2 = (i + 1) *m + j + 1 + offset
      const v3 = (i + 1) *m + j + offset
      const line = [5, v0, v1, v2, v3, v0]
      out.push(line)
    }
  }
  return flatten(out)
}

function _create_grid_axes(origin: number[], xticks: number[], yticks: number[], zticks: number[]){
  const pts: number[][] = []
  pts.push(flatten(cartesian_product(xticks, yticks, [origin[2]]))) //xy
  pts.push(flatten(cartesian_product([origin[0]], yticks, zticks))) //yz
  pts.push(flatten(cartesian_product(xticks, [origin[1]], zticks))) //xz
  
  const lines: number[][] = []
  lines.push(_make_grid_lines(xticks.length, yticks.length, lines.length)) //xy
  lines.push(_make_grid_lines(xticks.length, yticks.length, lines.length)) //xy
  lines.push(_make_grid_lines(xticks.length, yticks.length, lines.length)) //xy
  const gridPolyData = vtk({
    vtkClass: 'vtkPolyData',
    points: {
      vtkClass: 'vtkPoints',
      dataType: 'Float32Array',
      numberOfComponents: 3,
      values: flatten(pts),
    },
    lines: {
      vtkClass: 'vtkCellArray',
      dataType: 'Uint32Array',
      values:flatten(lines)
    }
  });
  
  const gridMapper = vtkMapper.newInstance();
  const gridActor = vtkActor.newInstance();
  gridMapper.setInputData(gridPolyData);
  gridActor.setMapper(gridMapper);
  gridActor.getProperty().setOpacity(0.1);
  
  return gridActor;
}


export function create_axes(origin: number[], xticks: number[], yticks: number[], zticks: number[], canvas: HTMLCanvasElement){
  const xlen = xticks.length
  const ylen = yticks.length
  const zlen = zticks.length
  const points = flatten([xticks, yticks, zticks].map((arr, axis) => {
    let coords = null
    if (axis==0)
    coords = flatten(cartesian_product(arr, [origin[1]], [origin[2]]))
    else if (axis==1)
    coords = flatten(cartesian_product([origin[0]], arr, [origin[2]]))
    else
    coords = flatten(cartesian_product([origin[0]], [origin[1]], arr))
    return coords
  }))
  const axesPolyData = vtk({
    vtkClass: 'vtkPolyData',
    points: {
      vtkClass: 'vtkPoints',
      dataType: 'Float32Array',
      numberOfComponents: 3,
      values: points,
    },
    lines: {
      vtkClass: 'vtkCellArray',
      dataType: 'Uint32Array',
      values: [2, 0, xlen-1, 2, xlen, xlen+ylen-1, 2, xlen+ylen, xlen+ylen+zlen-1]
    }
  });
  const psMapper = vtkPixelSpaceCallbackMapper.newInstance();
  psMapper.setInputData(axesPolyData);
  psMapper.setUseZValues(true);
  const textCtx = canvas.getContext("2d");
  psMapper.setCallback((coordsList: any, camera: any, aspect: any, _depthBuffer: any) => {
    if (textCtx) {
      const dims = {
        height: canvas.clientHeight,// * devicePixelRatio,
        width: canvas.clientWidth// * devicePixelRatio
      }
      const dataPoints = psMapper.getInputData().getPoints();
      const viewMatrix = camera.getViewMatrix();
      mat4.transpose(viewMatrix, viewMatrix);
      const projMatrix = camera.getProjectionMatrix(aspect, -1, 1);
      mat4.transpose(projMatrix, projMatrix);
      textCtx.clearRect(0, 0, dims.width, dims.height);
      coordsList.forEach((xy: any, idx: any) => {
        const pdPoint = dataPoints.getPoint(idx);
        const vc = vec3.fromValues(pdPoint[0], pdPoint[1], pdPoint[2]);
        vec3.transformMat4(vc, vc, viewMatrix);
        vc[2] += 0.01; // sensibility
        vec3.transformMat4(vc, vc, projMatrix);
        if (vc[2] - 0.001 < xy[3]) {
          textCtx.font = '30px serif';
          textCtx.textAlign = 'center';
          textCtx.textBaseline = 'middle';
          textCtx.fillText("\u00B7", xy[0], textCtx.canvas.height - xy[1]+2);
          textCtx.font = '16px serif';
          textCtx.textAlign = 'right';
          textCtx.textBaseline = 'top';
          let label
          if(idx<xlen)
          label = xticks[idx]
          else if(idx>=xlen && idx<xlen+ylen)
          label = yticks[idx-xlen]
          else
          label = zticks[idx-(xlen+ylen)]
          textCtx.fillText(`${label}`, xy[0], textCtx.canvas.height - xy[1]);
        }
      });
    }
  });
  const psActor = vtkActor.newInstance();
  psActor.setMapper(psMapper);
  
  const axesMapper = vtkMapper.newInstance();
  axesMapper.setInputData(axesPolyData)
  const axesActor = vtkActor.newInstance();
  axesActor.setMapper(axesMapper)
  
  const gridActor = _create_grid_axes(origin, xticks, yticks, zticks)
  
  return {psActor, axesActor, gridActor}
}
*/
