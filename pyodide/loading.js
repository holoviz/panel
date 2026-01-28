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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'holoviews']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport time\n\nimport panel as pn\n\nimport holoviews as hv\n\nimport numpy as np\n\nimport holoviews.plotting.bokeh\n\n\n\npn.extension(loading_spinner='dots', loading_color='#00aa41', template='bootstrap')\n\nhv.extension('bokeh')\n\npn.pane.Markdown('\\nEvery pane, widget and layout provides the **\`loading\` parameter**. When set to \`True\` a spinner will overlay the panel and indicate that the panel is currently loading. When you set \`loading\` to false the spinner is removed.\\n\\nUsing the \`pn.extension\` or by setting the equivalent parameters on \`pn.config\` we can select between different visual styles and colors for the loading indicator.\\n\\n').servable()\n\npn.extension(loading_spinner='dots', loading_color='#00aa41')\n\npn.pane.Markdown('\\nWe can enable the loading indicator for reactive functions annotated with \`depends\` or \`bind\` globally using:\\n\\n').servable()\n\npn.param.ParamMethod.loading_indicator = True\n\npn.pane.Markdown('\\nAlternatively we can enable it for a specific function by passing the \`loading_indicator=True\` argument to \`pn.panel\` or directly to the underlying  \`ParamMethod\`/\`ParamFunction\` object:\\n\\n').servable()\n\nbutton = pn.widgets.Button(name="UPDATE", button_type="primary", sizing_mode='stretch_width')\n\n\n\ndef random_plot(event):\n\n    if event: time.sleep(5)\n\n    return hv.Points(np.random.rand(100, 2)).opts(\n\n        responsive=True, height=400, size=8, color="green")\n\n\n\npn.Column(\n\n    button,\n\n    pn.param.ParamFunction(pn.bind(random_plot, button), loading_indicator=True)\n\n).servable()\n\npn.state.template.title = 'Loading Indicator'\n\nawait write_doc()`)
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