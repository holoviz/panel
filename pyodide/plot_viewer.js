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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'hvplot']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport param\n\nimport panel as pn\n\n\n\nfrom bokeh.sampledata.iris import flowers\n\nfrom panel.viewable import Viewer\n\n\n\npn.extension(template='fast')\n\nimport hvplot.pandas\n\npn.pane.Markdown('\\nThis example demonstrates the use of a \`Viewer\` class to build a reactive app. It uses the [iris dataset](https://en.wikipedia.org/wiki/Iris_flower_data_set) which is a standard example used to illustrate machine-learning and visualization techniques.\\n\\nWe will start by using the dataframe with these five features and then create a \`Selector\` parameter to develop menu options for different input features. Later we will define the core plotting function in a \`plot\` method and define the layout in the \`__panel__\` method of the \`IrisDashboard\` class.\\n\\nThe \`plot\` method watches the \`X_variable\` and \`Y_variable\` using the \`param.depends\` [decorator](https://www.google.com/search?q=python+decorator). The \`plot\` method plots the features selected for \`X_variable\` and \`Y_variable\` and colors them using the \`species\` column.\\n\\n').servable()\n\ninputs = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']\n\n\n\nclass IrisDashboard(Viewer):\n\n    X_variable = param.Selector(objects=inputs, default=inputs[0])\n\n    Y_variable = param.Selector(objects=inputs, default=inputs[1])\n\n\n\n    @param.depends('X_variable', 'Y_variable')\n\n    def plot(self):\n\n        return flowers.hvplot.scatter(x=self.X_variable, y=self.Y_variable, by='species').opts(height=600)\n\n\n\n    def __panel__(self):\n\n        return pn.Row(\n\n            pn.Param(self, width=300, name="Plot Settings"),\n\n            self.plot\n\n        )\n\n\n\nIrisDashboard(name='Iris_Dashboard').servable()\n\npn.state.template.title = 'Plot Viewer'\n\nawait write_doc()`)
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