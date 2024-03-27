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
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.4.0-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.4.0/dist/wheels/panel-1.4.0-py3-none-any.whl', 'pyodide-http==0.2.1', 'pyvista']
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
  \nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport panel as pn\nimport pyvista as pv\n\nfrom pyvista import examples\n\npn.extension('vtk', design='material', sizing_mode='stretch_width', template='material')\n\n_pn__state._cell_outputs['b83d413e'].append((pn.state.template.config.raw_css.append("""\n#main {\n  padding: 0;\n}""")))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['b83d413e'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['b83d413e'].append(_fig__out)\n\n_pn__state._cell_outputs['77edbd8e'].append("""For this example we use the pyvista library to load a dataset and generate easily a VTK scene""")\nm = examples.download_st_helens().warp_by_scalar()\n\n# default camera position\ncpos = [\n    (567000.9232163235, 5119147.423216323, 6460.423216322832),\n    (562835.0, 5114981.5, 2294.5),\n    (-0.4082482904638299, -0.40824829046381844, 0.8164965809277649)\n]\n\n# pyvista plotter\npl = pv.Plotter(notebook=True);\nactor = pl.add_mesh(m, smooth_shading=True, lighting=True)\npl.camera_position = cpos #set camera position\n\n# save initial camera properties\nrenderer = list(pl.ren_win.GetRenderers())[0]\ninitial_camera = renderer.GetActiveCamera()\ninitial_camera_pos = {\n    "focalPoint": initial_camera.GetFocalPoint(),\n    "position": initial_camera.GetPosition(),\n    "viewUp": initial_camera.GetViewUp()\n}\n\n# Panel creation using the VTK Scene created by the plotter pyvista\norientation_widget = True\nenable_keybindings = True\nvtkpan = pn.pane.VTK(\n    pl.ren_win, margin=0, sizing_mode='stretch_both', orientation_widget=orientation_widget,\n    enable_keybindings=enable_keybindings, min_height=600\n)\n_pn__state._cell_outputs['185b8f4a'].append((vtkpan))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['185b8f4a'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['185b8f4a'].append(_fig__out)\n\n_pn__state._cell_outputs['235dad12'].append("""WidgetBox with colorbars and actor selection""")\n# Creation of a mapping between Custom name and the VTK object reference\nactor_ref = ["None", actor.__this__]\nactor_names = ["None", 'St Helen']\nactor_opts = {k:v for k,v in zip(actor_names, actor_ref)}\n\noptions = {}\nactor_selection = pn.widgets.Select(value=None, options=actor_opts, margin=0, name="Actor Selection")\n_pn__state._cell_outputs['07a42c96'].append((actor_selection))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['07a42c96'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['07a42c96'].append(_fig__out)\n\n_pn__state._cell_outputs['40eed0de'].append("""WidgetBoxes with general parameters of the vtk Scene (Widgets, Background, Lights,...)""")\n# Scene Layout\ncolor = ''.join(['#'] + ['{:02x}'.format(int(v*255)) for v in pl.background_color[:3]])\nbind_and_orient = pn.widgets.CheckBoxGroup(\n    value=['Orientation Widget', 'Key Bindings'], options=['Orientation Widget', 'Key Bindings']\n)\nreset_camera = pn.widgets.Button(name='Reset Camera')\nbackground_color = pn.widgets.ColorPicker(value=color, name='Background Color')\nscene_props = pn.WidgetBox(bind_and_orient, reset_camera, background_color, sizing_mode='stretch_width')\n\n# Light properties\nlight_box_title = pn.widgets.StaticText(value='Light properties')\nlight_type = pn.widgets.Select(value='HeadLight', options=['HeadLight', 'SceneLight', 'CameraLight'])\nlight_intensity = pn.widgets.FloatSlider(start=0, end=1, value=1, name="Intensity")\nlight_props = pn.WidgetBox(light_box_title, light_type, light_intensity, sizing_mode='stretch_width')\n\n_pn__state._cell_outputs['408fd1a9'].append((pn.Column(scene_props, light_props, max_width=320)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['408fd1a9'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['408fd1a9'].append(_fig__out)\n\n_pn__state._cell_outputs['d68758e6'].append("""WidgetBox with properties of the Actors""")\n#layout actor props\nopacity = pn.widgets.FloatSlider(value=1, start=0, end=1, name='Opacity', disabled=True)\nlighting = pn.widgets.Toggle(value=True, name='Lighting', disabled=True)\ninterpolation = pn.widgets.Select(value='Phong', options=['Flat','Phong'], name='Interpolation', disabled=True)\nedges = pn.widgets.Toggle(value=False, name='Show Edges', disabled=True)\nedges_color = pn.widgets.ColorPicker(value='#ffffff', name='Edges Color', disabled=True)\nrepresentation = pn.widgets.Select(value='Surface', options=['Points','Wireframe','Surface'], name='Representation', disabled=True)\nfrontface_culling = pn.widgets.Toggle(value=False, name='Frontface Culling', disabled=True)\nbackface_culling = pn.widgets.Toggle(value=False, name='Backface Culling', disabled=True)\nambient = pn.widgets.FloatSlider(value=0, start=-1, end=1, name='Ambient', disabled=True)\ndiffuse = pn.widgets.FloatSlider(value=1, start=0, end=2, name='Diffuse', disabled=True)\nspecular = pn.widgets.FloatSlider(value=0, start=0, end=10, name='Specular', disabled=True)\nspecular_power = pn.widgets.FloatSlider(value=100, start=0, end=100, name='Specular Power', disabled=True)\n\nactor_props = pn.WidgetBox(\n    opacity, lighting, interpolation, edges, edges_color,\n    representation, frontface_culling, backface_culling,\n    ambient, diffuse, specular, specular_power\n)\n\n_pn__state._cell_outputs['f98652e0'].append((actor_props))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['f98652e0'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['f98652e0'].append(_fig__out)\n\n_pn__state._cell_outputs['675406ad'].append("""Linking all widgets together using jslinks""")\n#Linking\nlight_type.jslink(vtkpan, code={'value':"""\nconst light = target.renderer_el.getRenderer().getLights()[0]\nif (source.value == 'HeadLight')\n    light.setLightTypeToHeadLight()\nelse if (source.value == 'CameraLight')\n    light.setLightTypeToCameraLight()\nelse if (source.value == 'SceneLight')\n    light.setLightTypeToSceneLight()\ntarget.renderer_el.getRenderWindow().render()\n"""})\n\nlight_intensity.jslink(vtkpan, code={'value':"""\nconst light = target.renderer_el.getRenderer().getLights()[0]\nlight.setIntensity(source.value)\ntarget.renderer_el.getRenderWindow().render()\n"""})\n\n\nbind_and_orient.jslink(vtkpan, code = {'active':"""\ntarget.orientation_widget = source.active.includes(0)\ntarget.enable_keybindings = source.active.includes(1)\n"""})\n\nreset_camera.js_on_click(args={'target': vtkpan, 'initial_camera':initial_camera_pos},\n                         code="target.camera = initial_camera");\n\nbackground_color.jslink(vtkpan, code={'value':"""\nconst hextoarr = (color) => {return [parseInt(color.slice(1,3),16)/255, parseInt(color.slice(3,5),16)/255, parseInt(color.slice(5,7),16)/255]}\ntarget.renderer_el.getRenderer().setBackground(hextoarr(source.color))\ntarget.renderer_el.getRenderWindow().render()\n"""});\n\nopacity.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setOpacity(source.value)\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nlighting.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setLighting(source.active)\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nedges.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setEdgeVisibility(source.active)\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\ninterpolation.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    if(source.value=="Flat"){\n        actor.getProperty().setInterpolationToFlat()\n    }else{\n        actor.getProperty().setInterpolationToPhong()\n    }\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nedges_color.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const hextoarr = (color) => {return [parseInt(color.slice(1,3),16)/255, parseInt(color.slice(3,5),16)/255, parseInt(color.slice(5,7),16)/255]}\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setEdgeColor(hextoarr(source.color))\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nrepresentation.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    if(source.value=="Points"){\n        actor.getProperty().setRepresentationToPoints()\n    }else if(source.value=="Wireframe"){\n        actor.getProperty().setRepresentationToWireframe()\n    }else if(source.value=="Surface"){\n        actor.getProperty().setRepresentationToSurface()\n    }\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nfrontface_culling.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setFrontfaceCulling(source.active)\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nbackface_culling.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setBackfaceCulling(source.active)\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nambient.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setAmbient(source.value)\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\ndiffuse.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setDiffuse(source.value)\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nspecular.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setSpecular(source.value)\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nspecular_power.jscallback(args={"target":vtkpan, "actor_selection":actor_selection}, value="""\nif (actor_selection.value!="None"){\n    const actor = target.getActors(actor_selection.value)[0]\n    actor.getProperty().setSpecularPower(source.value)\n    target.renderer_el.getRenderWindow().render()\n}\n""")\n\nactor_selection.jslink(target=vtkpan, code = {'value' : """\nif (source.value!="None"){\n    const actor = target.getActors(source.value)[0]\n    target.outline.setInputData(actor.getMapper().getInputData())\n    target.renderer_el.getRenderer().addActor(target.outline_actor)\n    \n    //synchronize actor props and widgets values\n    const properties = actor.getProperty()\n    opacity.setv({value: properties.getOpacity()}, {silent: true})\n    lighting.setv({active: !!properties.getLighting()}, {silent: true})\n    edges.active = !!properties.getEdgeVisibility()\n    const actor_color = "#" + properties.getEdgeColor().map((c) => ("0" + Math.round(255*c).toString(16,2)).slice(-2)).join('')\n    edges_color.setv({color: actor_color}, {silent: true})\n    const interp_string = properties.getInterpolationAsString()\n    interpolation.setv({value: interp_string[0] + interp_string.slice(1).toLocaleLowerCase()}, {silent: true})\n    const repr_string = properties.getRepresentationAsString()\n    representation.setv({value: repr_string[0] + repr_string.slice(1).toLocaleLowerCase()}, {silent: true})\n    frontface_culling.setv({active: !!properties.getFrontfaceCulling()}, {silent: true})\n    backface_culling.setv({active: !!properties.getBackfaceCulling()}, {silent: true})\n    ambient.setv({value: properties.getAmbient()}, {silent: true})\n    diffuse.setv({value: properties.getDiffuse()}, {silent: true})\n    specular.setv({value: properties.getSpecular()}, {silent: true})\n    specular_power.setv({value: properties.getSpecularPower()}, {silent: true})\n    //enable widgets modifications\n    opacity.disabled = false\n    lighting.disabled = false\n    interpolation.disabled = false\n    edges.disabled = false\n    edges_color.disabled = false\n    representation.disabled = false\n    frontface_culling.disabled = false\n    backface_culling.disabled = false\n    ambient.disabled = false\n    diffuse.disabled = false\n    specular.disabled = false\n    specular_power.disabled = false\n} else {\n    target.renderer_el.getRenderer().removeActor(target.outline_actor)\n    opacity.disabled = true\n    lighting.disabled = true\n    interpolation.disabled = true\n    edges.disabled = true\n    edges_color.disabled = true\n    representation.disabled = true\n    frontface_culling.disabled = true\n    backface_culling.disabled = true\n    ambient.disabled = true\n    diffuse.disabled = true\n    specular.disabled = true\n    specular_power.disabled = true\n}\ntarget.renderer_el.getRenderWindow().render()\n\n"""}, args={"opacity":opacity, "lighting":lighting, "interpolation": interpolation, "edges": edges, "edges_color": edges_color,\n            "representation": representation, "frontface_culling": frontface_culling, "backface_culling": backface_culling,\n            "ambient": ambient, "diffuse": diffuse, "specular": specular, "specular_power": specular_power});\n\n_pn__state._cell_outputs['012fd3ad'].append((pn.Column(\n    "This example demonstrates the use of **VTK and pyvista** to display a *scene*",\n    pn.Row(\n        vtkpan.servable(title='VTK - Mt. St Helens'),\n        pn.Column(\n            actor_selection,\n            pn.Tabs(\n                ('Scene controller', pn.Column(scene_props, light_props)),\n                ('Actor properties',actor_props)\n            )\n        ).servable(target='sidebar')\n    ), min_height=600\n)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['012fd3ad'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['012fd3ad'].append(_fig__out)\n\n\nawait write_doc()
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