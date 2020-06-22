import { vec3, mat4 } from 'gl-matrix'


export let Follower: any

const vtk = (window as any).vtk

if(vtk) {
  const macro = vtk.macro
  const vtkActor = vtk.Rendering.Core.vtkActor

  function vtkFollower(publicAPI: any, model: any) {
    console.log("Hello")
    // Set our className
    model.classHierarchy.push('vtkFollower')

    // Capture 'parentClass' api for internal use
    const superClass = { ...publicAPI }

    publicAPI.getMTime = () => {
      let mt = superClass.getMTime()
      if (model.camera !== null) {
        const time = model.camera.getMTime()
        mt = time > mt ? time : mt
      }

      return mt;
    };

    publicAPI.computeMatrix = () => {
      // check whether or not need to rebuild the matrix
      if (publicAPI.getMTime() > model.matrixMTime.getMTime()) {
        mat4.identity(model.matrix)
        if (model.userMatrix) {
          mat4.multiply(model.matrix, model.matrix, model.userMatrix)
        }
        mat4.translate(model.matrix, model.matrix, model.origin)
        mat4.translate(model.matrix, model.matrix, model.position)
        mat4.multiply(model.matrix, model.matrix, model.rotation)
        mat4.scale(model.matrix, model.matrix, model.scale)

        if (model.camera) {
          // first compute our target viewUp
          const vup = vec3.fromValues(model.viewUp[0], model.viewUp[1], model.viewUp[2])
          if (!model.useViewUp) {
            const cvup = model.camera.getViewUp()
            vec3.set(vup, cvup[0], cvup[1], cvup[2])
          }

          // compute a vpn
          const vpn = vec3.create();
          if (model.camera.getParallelProjection()) {
            const cvpn = model.camera.getViewPlaneNormal()
            vec3.set(vpn, cvpn[0], cvpn[1], cvpn[2])
          } else {
            vec3.set(vpn, model.position[0], model.position[1], model.position[2])
            const cpos = model.camera.getPosition()
            const tmpv3 = vec3.fromValues(cpos[0], cpos[1], cpos[2])
            vec3.subtract(vpn, tmpv3, vpn)
            vec3.normalize(vpn, vpn)
          }

          // compute vright
          const vright = vec3.create();
          vec3.cross(vright, vup, vpn)
          vec3.normalize(vright, vright)

          // now recompute the vpn so that it is orthogonal to vup
          vec3.cross(vpn, vright, vup)
          vec3.normalize(vpn, vpn)

          model.followerMatrix[0] = vright[0]
          model.followerMatrix[1] = vright[1]
          model.followerMatrix[2] = vright[2]

          model.followerMatrix[4] = vup[0]
          model.followerMatrix[5] = vup[1]
          model.followerMatrix[6] = vup[2]

          model.followerMatrix[8] = vpn[0]
          model.followerMatrix[9] = vpn[1]
          model.followerMatrix[10] = vpn[2]

          mat4.multiply(model.matrix, model.followerMatrix, model.matrix);
        }

        mat4.translate(model.matrix, model.matrix, [
          -model.origin[0],
          -model.origin[1],
          -model.origin[2],
        ]);
        mat4.transpose(model.matrix, model.matrix);

        // check for identity
        model.isIdentity = false;
        model.matrixMTime.modified();
      }
    }
  }

  // ----------------------------------------------------------------------------
  // Object factory
  // ----------------------------------------------------------------------------

  const DEFAULT_VALUES = {
    viewUp: [0, 1, 0],
    useViewUp: false,
    camera: null,
  }

  // ----------------------------------------------------------------------------

  Follower = {
    newInstance: macro.newInstance((publicAPI: any, model: any, initialValues = {}) => {
      Object.assign(model, DEFAULT_VALUES, initialValues)
  
      // Inheritance
      vtkActor.extend(publicAPI, model, initialValues)
  
      model.followerMatrix = mat4.create()
      model.camera = vtk.Rendering.Core.vtkCamera.newInstance()
      mat4.identity(model.followerMatrix)
  
      // Build VTK API
      macro.setGet(publicAPI, model, ['useViewUp', 'camera'])
  
      macro.setGetArray(publicAPI, model, ['viewUp'], 3)
  
      // Object methods
      vtkFollower(publicAPI, model);
    }, 'vtkFollower')
  }

}