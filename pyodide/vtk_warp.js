importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.4.0-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.4.0/dist/wheels/panel-1.4.0-py3-none-any.whl', 'pyodide-http==0.2.1', 'numpy', 'pyvista']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  \nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport panel as pn\nimport numpy as np\nimport pyvista as pv\n\n_pn__state._cell_outputs['376f18e7'].append((pn.extension('vtk', sizing_mode="stretch_width", template='fast')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['376f18e7'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['376f18e7'].append(_fig__out)\n\n_pn__state._cell_outputs['47f1b15f'].append("""Temporal function inspired from http://holoviews.org/user_guide/Live_Data.html""")\nalpha = 2\nxvals  = np.linspace(-4, 4,101)\nyvals  = np.linspace(-4, 4,101)\nxs, ys = np.meshgrid(xvals, yvals)\n\n#temporal function to create data on a plane\ndef time_function(time):\n    return np.sin(((ys/alpha)**alpha+time)*xs)\n\n# 3d plane to support the data\nmesh_ref = pv.ImageData(\n    dimensions=(xvals.size, yvals.size, 1), #dims\n    spacing=(xvals[1]-xvals[0],yvals[1]-yvals[0],1), #spacing\n    origin=(xvals.min(),yvals.min(),0) #origin\n)\nmesh_ref.point_data['values'] = time_function(0).flatten(order='F')  #add data for time=0\npl_ref = pv.Plotter()\npl_ref.add_mesh(mesh_ref, cmap='rainbow')\n\n_pn__state._cell_outputs['43663cbf'].append((pn.pane.VTK(pl_ref.ren_win, min_height=600)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['43663cbf'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['43663cbf'].append(_fig__out)\n\n_pn__state._cell_outputs['40c63a24'].append("""We will demonstrate how to warp the surface and plot a temporal animation""")\nmesh_warped = mesh_ref.warp_by_scalar() # warp the mesh using data at time=0\n#create the pyvista plotter\npl = pv.Plotter()\npl.add_mesh(mesh_warped, cmap='rainbow')\n\n#initialize panel and widgets\ncamera = {\n    'position': [13.443258285522461, 12.239550590515137, 12.731934547424316],\n    'focalPoint': [0, 0, 0],\n     'viewUp': [-0.41067028045654297, -0.40083757042884827, 0.8189500570297241]\n}\nvtkpan = pn.pane.VTK(pl.ren_win, orientation_widget=True, sizing_mode='stretch_both', camera=camera)\nframe = pn.widgets.Player(value=0, start=0, end=50, interval=100, loop_policy="reflect", height=100)\n\ndef update_3d_warp(event):\n    #the player value range in between 0 and 50, however we want time between 0 and 10\n    time = event.new/5\n    data = time_function(time).flatten(order='F')\n    mesh_ref.point_data['values'] = data\n    mesh_warped.point_data['values'] = data\n    mesh_warped.points = mesh_ref.warp_by_scalar(factor=0.5).points\n    vtkpan.synchronize()\n    \nframe.param.watch(update_3d_warp, 'value')\n\n_pn__state._cell_outputs['2f14c8b7'].append((pn.Column(\n    "This app demonstrates the use of Panel to animate a \`VTK\` rendering.",\n    frame,\n    vtkpan,\n    min_height=800\n).servable(title='VTK Warp')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['2f14c8b7'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['2f14c8b7'].append(_fig__out)\n\n\nawait write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.globals.set('patch', msg.patch)
    self.pyodide.runPythonAsync(`
    from panel.io.pyodide import _convert_json_patch
    state.curdoc.apply_json_patch(_convert_json_patch(patch), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.globals.set('location', msg.location)
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads(location)
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()