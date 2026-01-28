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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport numpy as np\n\nimport panel as pn\n\n\n\nfrom bokeh.plotting import figure\n\nfrom bokeh.models import ColumnDataSource\n\n\n\npn.extension(template='fast')\n\npn.pane.Markdown('\\nThis example demonstrates how to use \`add_periodic_callback\` to stream data to a Bokeh plot.\\n\\n').servable()\n\np = figure(sizing_mode='stretch_width', title='Bokeh streaming example')\n\n\n\nxs = np.arange(1000)\n\nys = np.random.randn(1000).cumsum()\n\nx, y = xs[-1], ys[-1]\n\n\n\ncds = ColumnDataSource(data={'x': xs, 'y': ys})\n\n\n\np.line('x', 'y', source=cds)\n\n\n\ndef stream():\n\n    global x, y\n\n    x += 1\n\n    y += np.random.randn()\n\n    cds.stream({'x': [x], 'y': [y]})\n\n    pn.io.push_notebook(bk_pane) # Only needed when running in notebook context\n\n\n\ncb = pn.state.add_periodic_callback(stream, 100)\n\n\n\nbk_pane = pn.pane.Bokeh(p)\n\n\n\npn.Column(\n\n\tpn.Row(\n\n        cb.param.period,\n\n\t    pn.widgets.Toggle.from_param(cb.param.running, align='end')\n\n    ),\n\n\tbk_pane\n\n).servable()\n\npn.state.template.title = 'Streaming Bokeh'\n\nawait write_doc()`)
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