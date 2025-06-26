importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.5/full/pyodide.js");

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
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.7.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.7.2/dist/wheels/panel-1.7.2-py3-none-any.whl', 'pyodide-http==0.2.1', 'numpy']
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
  \nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport numpy as np\n\nimport panel as pn\n\n\n\npn.extension('plotly', template='bootstrap')\n\npn.pane.Markdown('\\nSince Plotly plots are represented as simple JavaScript objects, we can easily define a JS callback to modify the data and trigger an update in a plot:\\n\\n').servable()\n\nxs, ys = np.mgrid[-3:3:0.2, -3:3:0.2]\n\ncontour = dict(ncontours=4, type='contour', z=np.sin(xs**2*ys**2))\n\nlayout = {'width': 600, 'height': 500, 'margin': {'l': 8, 'b': 8, 'r': 8, 't': 8}}\n\nfig = dict(data=contour, layout=layout)\n\nplotly_pane = pn.pane.Plotly(fig, width=600, height=500)\n\n\n\nbuttons = pn.widgets.RadioButtonGroup(value='Medium', options=['Low', 'Medium', 'High'], button_type="success")\n\n\n\nrange_callback = """\n\nvar ncontours = [2, 5, 10]\n\ntarget.data[0].ncontours = ncontours[source.active]\n\ntarget.properties.data.change.emit()\n\n"""\n\n\n\nbuttons.jslink(plotly_pane, code={'active': range_callback})\n\n\n\npn.Column(buttons, plotly_pane).servable()\n\npn.state.template.title = 'Plotly Link'\n\nawait write_doc()
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