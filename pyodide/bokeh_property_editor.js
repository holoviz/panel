importScripts("https://cdn.jsdelivr.net/pyodide/v0.28.2/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide...");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded pyodide!");
  const data_archives = [];
  for (const archive of data_archives) {
    let zipResponse = await fetch(archive);
    let zipBinary = await zipResponse.arrayBuffer();
    self.postMessage({type: 'status', msg: `Unpacking ${archive}`})
    self.pyodide.unpackArchive(zipBinary, "zip");
  }
  await self.pyodide.loadPackage("micropip");
  self.postMessage({type: 'status', msg: `Installing environment`})
  try {
    await self.pyodide.runPythonAsync(`
      import micropip
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'numpy']);
    `);
  } catch(e) {
    console.log(e)
    self.postMessage({
      type: 'status',
      msg: `Error while installing packages`
    });
  }
  console.log("Environment loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport numpy as np\n\nimport panel as pn\n\n\n\npn.extension(template='bootstrap')\n\npn.pane.Markdown("\\nBokeh's property system defines the valid properties for all the different Bokeh models. Using \`\`jslink\`\` we can easily tie a widget value to Bokeh properties on another widget or plot. This example defines functions that generate a property editor for the most common Bokeh properties. First, we define two functions that generate a set of widgets linked to a plot:\\n\\n").servable()\n\nfrom bokeh.core.enums import LineDash, LineCap, MarkerType, NamedColor\n\nfrom bokeh.core.property.vectorization import Value\n\nfrom bokeh.models.plots import Model, _list_attr_splat\n\n\n\ndef meta_widgets(model, width=500):\n\n    tabs = pn.Tabs(width=width)\n\n    widgets = get_widgets(model, width=width-25)\n\n    if widgets:\n\n        tabs.append((type(model).__name__, widgets))\n\n    for p, v in model.properties_with_values().items():\n\n        if isinstance(v, _list_attr_splat):\n\n            v = v[0]\n\n        if isinstance(v, Model):\n\n            subtabs = meta_widgets(v)\n\n            if subtabs is not None:\n\n                tabs.append((p.title(), subtabs))\n\n\n\n    if hasattr(model, 'renderers'):\n\n        for r in model.renderers:\n\n            tabs.append((type(r).__name__, meta_widgets(r)))\n\n    if hasattr(model, 'axis') and isinstance(model.axis, list):\n\n        for pre, axis in zip('XY', model.axis):\n\n            tabs.append(('%s-Axis' % pre, meta_widgets(axis)))\n\n    if hasattr(model, 'grid'):\n\n        for pre, grid in zip('XY', model.grid):\n\n            tabs.append(('%s-Grid' % pre, meta_widgets(grid)))\n\n    if not widgets and not len(tabs) > 1:\n\n        return None\n\n    elif not len(tabs) > 1:\n\n        return tabs[0]\n\n    return tabs\n\n\n\ndef get_widgets(model, skip_none=True, **kwargs):\n\n    widgets = []\n\n    for p, v in model.properties_with_values().items():\n\n        if isinstance(v, Value):\n\n            v = v.value\n\n        if v is None and skip_none:\n\n            continue\n\n\n\n        ps = dict(name=p, value=v, **kwargs)\n\n        if 'alpha' in p:\n\n            w = pn.widgets.FloatSlider(start=0, end=1, **ps)\n\n        elif 'color' in p:\n\n            if v in list(NamedColor):\n\n                w = pn.widgets.Select(options=list(NamedColor), **ps)\n\n            else:\n\n                w = pn.widgets.ColorPicker(**ps)\n\n        elif p=="width":\n\n            w = pn.widgets.IntSlider(start=400, end=800, **ps)\n\n        elif p in ["inner_width", "outer_width"]:\n\n            w = pn.widgets.IntSlider(start=0, end=20, **ps)\n\n        elif p.endswith('width'):\n\n            w = pn.widgets.FloatSlider(start=0, end=20, **ps)\n\n        elif 'marker' in p:\n\n            w = pn.widgets.Select(options=list(MarkerType), **ps)\n\n        elif p.endswith('cap'):\n\n            w = pn.widgets.Select(options=list(LineCap), **ps)\n\n        elif p == 'size':\n\n            w = pn.widgets.FloatSlider(start=0, end=20, **ps)\n\n        elif p.endswith('text') or p.endswith('label'):\n\n            w = pn.widgets.TextInput(**ps)\n\n        elif p.endswith('dash'):\n\n            patterns = list(LineDash)\n\n            w = pn.widgets.Select(options=patterns, value=v or patterns[0], **kwargs)\n\n        else:\n\n            continue\n\n        w.jslink(model, value=p)\n\n        widgets.append(w)\n\n    return pn.Column(*sorted(widgets, key=lambda w: w.name))\n\n\n\n# Having defined these helper functions we can now declare a plot and use the \`\`meta_widgets\`\` function to generate the GUI:\n\n\n\nfrom bokeh.plotting import figure\n\n\n\np = figure(title='This is a title', x_axis_label='x-axis', y_axis_label='y-axis')\n\nxs = np.linspace(0, 10)\n\nr = p.scatter(xs, np.sin(xs))\n\n\n\neditor=pn.Row(meta_widgets(p), p)\n\n\n\neditor.servable()\n\npn.state.template.title = 'Bokeh property editor'\n\nawait write_doc()`)
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