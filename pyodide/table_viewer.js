importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js");

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
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.7.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.6.3/dist/wheels/panel-1.6.3-py3-none-any.whl', 'pyodide-http==0.2.1', 'param', 'pandas']
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
  \nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport param\n\nimport panel as pn\n\n\n\nfrom bokeh.sampledata.iris import flowers\n\nfrom bokeh.sampledata.autompg import autompg_clean\n\nfrom bokeh.sampledata.population import data\n\nfrom panel.viewable import Viewer\n\n\n\npn.extension(template='fast')\n\npn.pane.Markdown("\\nThis example demonstrates Panel's reactive programming paradigm using the Param library to express parameters, plus methods with computation depending on those parameters. This pattern can be used to update the displayed views whenever a parameter value changes, without re-running computation unnecessarily.\\n\\n").servable()\n\nclass ReactiveTables(Viewer):\n\n\n\n    dataset = param.Selector(default='iris', objects=['iris', 'autompg', 'population'])\n\n\n\n    rows = param.Integer(default=10, bounds=(0, 19))\n\n\n\n    @param.depends('dataset')\n\n    def data(self):\n\n        if self.dataset == 'iris':\n\n            return flowers\n\n        elif self.dataset == 'autompg':\n\n            return autompg_clean\n\n        else:\n\n            return data\n\n\n\n    @param.depends('data')\n\n    def summary(self):\n\n        return self.data().describe()\n\n\n\n    @param.depends('data', 'rows')\n\n    def table(self):\n\n        return self.data().iloc[:self.rows]\n\n\n\n    def __panel__(self):\n\n        return pn.Row(\n\n            pn.Param(self, name="Settings", width=300),\n\n\t\t\tpn.Spacer(width=10),\n\n            pn.Column(\n\n\t\t\t    "## Description",\n\n\t\t\t\tpn.pane.DataFrame(self.summary, sizing_mode='stretch_width'),\n\n\t\t\t\t"## Table",\n\n\t\t\t\tpn.pane.DataFrame(self.table, sizing_mode='stretch_width'),\n\n\t\t\t)\n\n        )\n\n\n\nReactiveTables().servable()\n\npn.state.template.title = 'Reactive Tables'\n\nawait write_doc()
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