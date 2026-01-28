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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'hvplot', 'scipy']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport io\nimport panel as pn\nimport pandas as pd\nimport hvplot.pandas\n\npn.extension(template='fast')\n\npn.state.template.title = 'hvPlot Explorer'\n_pn__state._cell_outputs['f3d89bef-89d2-42fd-ab00-5f0d8f800a27'].append("""This example demonstrates how to leverage the hvPlot explorer functionality when combined with a FileInput widget to allow users to explore their own data. When a user uploads their own data it gets added to the list of datasets the user can select from.""")\nupload = pn.widgets.FileInput(name='Upload file', height=50)\nselect = pn.widgets.Select(options={\n    'Penguins': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv',\n    'Diamonds': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv',\n    'Titanic': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv',\n    'MPG': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv'\n})\n\ndef add_data(event):\n    b = io.BytesIO()\n    upload.save(b)\n    b.seek(0)\n    name = '.'.join(upload.filename.split('.')[:-1])\n    select.options[name] = b\n    select.param.trigger('options')\n    select.value = b\n    \nupload.param.watch(add_data, 'filename')\n\ndef explore(csv):\n    df = pd.read_csv(csv)\n    explorer = hvplot.explorer(df)\n    def plot_code(**kwargs):\n        code = f'\`\`\`python\\n{explorer.plot_code()}\\n\`\`\`'\n        return pn.pane.Markdown(code, sizing_mode='stretch_width')\n    return pn.Column(\n        explorer,\n        '**Code**:',\n        pn.bind(plot_code, **explorer.param.objects())\n    )\n\nwidgets = pn.Column(\n    "Select an existing dataset or upload one of your own CSV files and start exploring your data.",\n    pn.Row(\n        select,\n        upload,\n    )\n).servable()  \n\noutput = pn.panel(pn.bind(explore, select)).servable()\n\n_pn__state._cell_outputs['732b5d4a-6181-4194-8c5f-6f989dabbb3a'].append((pn.Column(widgets, output)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['732b5d4a-6181-4194-8c5f-6f989dabbb3a'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['732b5d4a-6181-4194-8c5f-6f989dabbb3a'].append(_fig__out)\n\n\nawait write_doc()`)
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