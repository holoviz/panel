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
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.4.0-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.4.0/dist/wheels/panel-1.4.0-py3-none-any.whl', 'pyodide-http==0.2.1', 'holoviews', 'numpy', 'param', 'pyvista', 'scipy']
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
  \nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nfrom functools import partial\n\nimport holoviews as hv\nimport numpy as np\nimport panel as pn\nimport param\n\nfrom holoviews.operation.datashader import rasterize\nfrom bokeh.util.serialization import make_globally_unique_id\nfrom pyvista import examples\nfrom scipy.ndimage import zoom\n\nimport pyvista as pv # Import after datashader to avoid segfault on some systems\n\njs_files = {'jquery': 'https://code.jquery.com/jquery-1.11.1.min.js',\n            'goldenlayout': 'https://golden-layout.com/files/latest/js/goldenlayout.min.js'}\ncss_files = ['https://golden-layout.com/files/latest/css/goldenlayout-base.css',\n             'https://golden-layout.com/files/latest/css/goldenlayout-dark-theme.css']\n\npn.extension('vtk', js_files=js_files, css_files=css_files, design='material', theme='dark', sizing_mode="stretch_width")\n\nhv.renderer('bokeh').theme = 'dark_minimal'\n_pn__state._cell_outputs['880b26c4'].append((hv.opts.defaults(hv.opts.Image(responsive=True, tools=['hover']))))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['880b26c4'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['880b26c4'].append(_fig__out)\n\n_pn__state._cell_outputs['a34b6d04'].append("""## Declare callbacks""")\nclass ImageSmoother(param.Parameterized):\n    \n    smooth_fun = param.Parameter(default=None)\n    smooth_level = param.Integer(default=5, bounds=(1,10))\n    order = param.Selector(default=1, objects=[1,2,3])\n    \n    def __init__(self, **params):\n        super(ImageSmoother, self).__init__(**params)\n        self._update_fun()\n\n    @param.depends('order', 'smooth_level', watch=True)\n    def _update_fun(self):\n        self.smooth_fun = lambda x: zoom(x, zoom=self.smooth_level, order=self.order)\n\ndef update_camera_projection(*evts):\n    volume.camera['parallelProjection'] = evts[0].new\n    volume.param.trigger('camera')\n\ndef hook_reset_range(plot, elem, lbrt):\n    bkplot = plot.handles['plot']\n    x_range = lbrt[0], lbrt[2]\n    y_range = lbrt[1], lbrt[3]\n    old_x_range_reset = bkplot.x_range.reset_start, bkplot.x_range.reset_end\n    old_y_range_reset = bkplot.y_range.reset_start, bkplot.y_range.reset_end  \n    if x_range != old_x_range_reset or y_range != old_y_range_reset:\n        bkplot.x_range.reset_start, bkplot.x_range.reset_end = x_range\n        bkplot.x_range.start, bkplot.x_range.end = x_range\n        bkplot.y_range.reset_start, bkplot.y_range.reset_end = y_range\n        bkplot.y_range.start, bkplot.y_range.end = y_range\n    \ndef image_slice(dims, array, lbrt, mapper, smooth_fun):\n    array = np.asarray(array)\n    low = mapper['low'] if mapper else array.min()\n    high = mapper['high'] if mapper else array.max()\n    cmap = mapper['palette'] if mapper else 'fire'\n    img = hv.Image(smooth_fun(array), bounds=lbrt, kdims=dims, vdims='Intensity')\n    reset_fun = partial(hook_reset_range, lbrt=lbrt)\n    return img.opts(clim=(low, high), cmap=cmap, hooks=[reset_fun])\n_pn__state._cell_outputs['8d632283'].append("""## Declare Panel""")\n# Download datasets\nhead = examples.download_head()\nbrain = examples.download_brain()\n\ndataset_selection = pn.widgets.Select(name='Dataset', value=head, options={'Head': head, 'Brain': brain})\n\nvolume = pn.pane.VTKVolume(\n    dataset_selection.value, sizing_mode='stretch_both', min_height=400, \n    display_slices=True, orientation_widget=True, render_background="#222222",\n    colormap='Rainbow Desaturated'\n)\n\n@pn.depends(dataset_selection, watch=True)\ndef update_volume_object(value):\n    controller.loading=True\n    volume.object = value\n    controller.loading=False\n\nvolume_controls = volume.controls(jslink=False, parameters=[\n    'render_background', 'display_volume', 'display_slices',\n    'slice_i', 'slice_j', 'slice_k', 'rescale'\n])\n\ntoggle_parallel_proj = pn.widgets.Toggle(name='Parallel Projection', value=False)\n\ntoggle_parallel_proj.param.watch(update_camera_projection, ['value'], onlychanged=True)\n\nsmoother = ImageSmoother()\n\ndef image_slice_i(si, mapper, smooth_fun, vol):\n    arr = vol.active_scalars.reshape(vol.dimensions, order='F')\n    lbrt = vol.bounds[2], vol.bounds[4], vol.bounds[3], vol.bounds[5]\n    return image_slice(['y','z'], arr[si,:,::-1].T, lbrt, mapper, smooth_fun)\n\ndef image_slice_j(sj, mapper, smooth_fun, vol):\n    arr = vol.active_scalars.reshape(vol.dimensions, order='F')\n    lbrt = vol.bounds[0], vol.bounds[4], vol.bounds[1], vol.bounds[5]\n    return image_slice(['x','z'], arr[:,sj,::-1].T, lbrt, mapper, smooth_fun)\n\ndef image_slice_k(sk, mapper, smooth_fun, vol):\n    arr = vol.active_scalars.reshape(vol.dimensions, order='F')\n    lbrt = vol.bounds[0], vol.bounds[2], vol.bounds[1], vol.bounds[3]\n    return image_slice(['x', 'y'], arr[:,::-1,sk].T, lbrt, mapper, smooth_fun)\n\ncommon = dict(\n    mapper=volume.param.mapper,\n    smooth_fun=smoother.param.smooth_fun,\n    vol=volume.param.object,\n)\n\ndmap_i = rasterize(hv.DynamicMap(pn.bind(image_slice_i, si=volume.param.slice_i, **common)))\ndmap_j = rasterize(hv.DynamicMap(pn.bind(image_slice_j, sj=volume.param.slice_j, **common)))\ndmap_k = rasterize(hv.DynamicMap(pn.bind(image_slice_k, sk=volume.param.slice_k, **common)))\n\ncontroller = pn.Column(\n    pn.Column(dataset_selection, toggle_parallel_proj, *volume_controls[1:]),\n    pn.Param(smoother, parameters=['smooth_level', 'order']),\n    pn.panel("This app demos **advanced 3D visualisation** using [Panel](https://panel.holoviz.org/) and [PyVista](https://docs.pyvista.org/).", margin=(5,15)),\n    pn.layout.VSpacer(),\n)\n_pn__state._cell_outputs['ee1f9fbb'].append("""## Set up template""")\ntemplate = """\n{%% extends base %%}\n<!-- goes in body -->\n{%% block contents %%}\n{%% set context = '%s' %%}\n{%% if context == 'notebook' %%}\n    {%% set slicer_id = get_id() %%}\n    <div id='{{slicer_id}}'></div>\n{%% endif %%}\n<style>\n:host {\n    width: auto;\n}\n</style>\n\n<script>\nvar config = {\n    settings: {\n        hasHeaders: true,\n        constrainDragToContainer: true,\n        reorderEnabled: true,\n        selectionEnabled: false,\n        popoutWholeStack: false,\n        blockedPopoutsThrowError: true,\n        closePopoutsOnUnload: true,\n        showPopoutIcon: false,\n        showMaximiseIcon: true,\n        showCloseIcon: false\n    },\n    content: [{\n        type: 'row',\n        content:[\n            {\n                type: 'component',\n                componentName: 'view',\n                componentState: { model: '{{ embed(roots.controller) }}',\n                                  title: 'Controls',\n                                  width: 350,\n                                  css_classes:['scrollable']},\n                isClosable: false,\n            },\n            {\n                type: 'column',\n                content: [\n                    {\n                        type: 'row',\n                        content:[\n                            {\n                                type: 'component',\n                                componentName: 'view',\n                                componentState: { model: '{{ embed(roots.scene3d) }}', title: '3D View'},\n                                isClosable: false,\n                            },\n                            {\n                                type: 'component',\n                                componentName: 'view',\n                                componentState: { model: '{{ embed(roots.slice_i) }}', title: 'Slice I'},\n                                isClosable: false,\n                            }\n                        ]\n                    },\n                    {\n                        type: 'row',\n                        content:[\n                            {\n                                type: 'component',\n                                componentName: 'view',\n                                componentState: { model: '{{ embed(roots.slice_j) }}', title: 'Slice J'},\n                                isClosable: false,\n                            },\n                            {\n                                type: 'component',\n                                componentName: 'view',\n                                componentState: { model: '{{ embed(roots.slice_k) }}', title: 'Slice K'},\n                                isClosable: false,\n                            }\n                        ]\n                    }\n                ]\n            }\n        ]\n    }]\n};\n\n{%% if context == 'notebook' %%}\n    var myLayout = new GoldenLayout( config, '#' + '{{slicer_id}}' );\n    $('#' + '{{slicer_id}}').css({width: '100%%', height: '800px', margin: '0px'})\n{%% else %%}\n    var myLayout = new GoldenLayout( config );\n{%% endif %%}\n\nmyLayout.registerComponent('view', function( container, componentState ){\n    const {width, css_classes} = componentState\n    if(width)\n      container.on('open', () => container.setSize(width, container.height))\n    if (css_classes)\n      css_classes.map((item) => container.getElement().addClass(item))\n    container.setTitle(componentState.title)\n    container.getElement().html(componentState.model);\n    container.on('resize', () => window.dispatchEvent(new Event('resize')))\n});\n\nmyLayout.init();\n</script>\n{%% endblock %%}\n"""\n\n\ntmpl = pn.Template(template=(template % 'server'), nb_template=(template % 'notebook'))\ntmpl.nb_template.globals['get_id'] = make_globally_unique_id\n\ntmpl.add_panel('controller', controller)\ntmpl.add_panel('scene3d', volume)\ntmpl.add_panel('slice_i', pn.panel(dmap_i, sizing_mode='stretch_both'))\ntmpl.add_panel('slice_j', pn.panel(dmap_j, sizing_mode='stretch_both'))\ntmpl.add_panel('slice_k', pn.panel(dmap_k, sizing_mode='stretch_both'))\n\n_pn__state._cell_outputs['46e91487'].append((tmpl.servable(title='VTKSlicer')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['46e91487'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['46e91487'].append(_fig__out)\n\n\nawait write_doc()
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