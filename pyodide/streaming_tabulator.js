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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'numpy', 'pandas']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport numpy as np\n\nimport pandas as pd\n\nimport panel as pn\n\n\n\npn.extension('tabulator', template='fast', sizing_mode="stretch_width")\n\npn.pane.Markdown('\\nThis example demonstrates how to use \`add_periodic_callback\` to stream data to a \`Tabulator\` pane.\\n\\n').servable()\n\ndf = pd.DataFrame(np.random.randn(10, 4), columns=list('ABCD')).cumsum()\n\n\n\nrollover = pn.widgets.IntInput(name='Rollover', value=15)\n\nfollow = pn.widgets.Checkbox(name='Follow', value=True, align='end')\n\n\n\ntabulator = pn.widgets.Tabulator(df, height=450)\n\n\n\ndef color_negative_red(val):\n\n    """\n\n    Takes a scalar and returns a string with\n\n    the css property \`'color: red'\` for negative\n\n    strings, black otherwise.\n\n    """\n\n    color = 'red' if val < 0 else 'green'\n\n    return 'color: %s' % color\n\n\n\ntabulator.style.map(color_negative_red)\n\n\n\ndef stream():\n\n    data = df.iloc[-1] + np.random.randn(4)\n\n    tabulator.stream(data, rollover=rollover.value, follow=follow.value)\n\n\n\ncb = pn.state.add_periodic_callback(stream, 200)\n\n\n\npn.Column(\n\n    pn.Row(cb.param.period, rollover, follow, width=400),\n\n    tabulator\n\n).servable()\n\npn.state.template.title = 'Streaming Tabulator'\n\nawait write_doc()`)
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