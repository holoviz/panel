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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'pandas', 'param']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport param\n\nimport panel as pn\n\nimport pandas as pd\n\nfrom panel.viewable import Viewer\n\n\n\npn.extension(template='fast')\n\n\n\nDATASETS = {\n\n    'Penguins': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv',\n\n    'Diamonds': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv',\n\n    'Titanic': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv',\n\n    'MPG': 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv'\n\n}\n\npn.pane.Markdown('\\n### Step 2: Define the Viewer Class\\n\\nCreate a class \`ReactiveTables\` that inherits from \`Viewer\`. This class will manage the dataset selection and row display:\\n\\n').servable()\n\nclass ReactiveTables(Viewer):\n\n    dataset = param.Selector(objects=DATASETS)\n\n    rows = param.Integer(default=10, bounds=(0, 19))\n\n\n\n    @pn.cache(max_items=3)\n\n    @param.depends("dataset")\n\n    def data(self):\n\n        # Each dataset will only be read once across all user session\n\n        return pd.read_csv(self.dataset)\n\n\n\n    @param.depends("data")\n\n    def summary(self):\n\n        return self.data().describe()\n\n\n\n    @param.depends("data", "rows")\n\n    def table(self):\n\n        return self.data().iloc[: self.rows]\n\n\n\n    def __panel__(self):\n\n        return pn.Row(\n\n            pn.Param(self, name="Settings", width=300),\n\n            pn.Spacer(width=10),\n\n            pn.Column(\n\n                "## Description",\n\n                pn.pane.DataFrame(self.summary, sizing_mode="stretch_width"),\n\n                "## Table",\n\n                pn.pane.DataFrame(self.table, sizing_mode="stretch_width"),\n\n            ),\n\n        )\n\npn.pane.Markdown('\\n### Step 3: Serve the Application\\n\\nFinally, make the \`ReactiveTables\` class servable:\\n\\n').servable()\n\nReactiveTables().servable()\n\npn.pane.Markdown("\\n## Conclusion\\n\\nBy following this guide, you've created a reactive table viewer using Panel. This application allows users to interactively select datasets and control the number of rows displayed, with efficient updates based on parameter changes.\\n\\nFeel free to experiment with different datasets and parameters to further explore Panel's capabilities.\\n\\n## Additional Notes\\n\\n- The \`max_items=3\` argument in \`@pn.cache\` is an example. You can adjust this value or explore other supported arguments to suit your needs.\\n").servable()\n\npn.state.template.title = 'How to Create Reactive Tables with Panel'\n\nawait write_doc()`)
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