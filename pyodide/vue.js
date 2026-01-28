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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'param', 'requests']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport panel as pn\n\nimport param\n\nimport requests\n\n\n\nclass BasicVueComponent(pn.reactive.ReactiveHTML):\n\n\n\n    _template = """\n\n    <div id="container" style="height:100%; width:100%; background:#0072B5; border-radius:4px; padding:6px; color:white">\n\n      <vue-component></vue-component>\n\n    </div>\n\n    """\n\n\n\n    _scripts = {\n\n        "render": """\n\n    const template = "<div>Hello Panel + Vue.js World!</div>"\n\n    const vue_component = {template: template}\n\n    el=new Vue({\n\n        el: container,\n\n        components: {\n\n            'vue-component' : vue_component\n\n        }\n\n    })\n\n    """\n\n    }\n\n\n\n    _extension_name = 'vue'\n\n\n\n    __javascript__ = [\n\n        "https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js"\n\n    ]\n\n\n\nclass BootstrapVueComponent(BasicVueComponent):\n\n\n\n    __javascript__= [\n\n        "https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js",\n\n        "https://unpkg.com/bootstrap-vue@latest/dist/bootstrap-vue.min.js",\n\n    ]\n\n    __css__=[\n\n        "https://unpkg.com/bootstrap/dist/css/bootstrap.min.css",\n\n        "https://unpkg.com/bootstrap-vue@latest/dist/bootstrap-vue.min.css",\n\n    ]\n\n\n\npn.extension('vue', sizing_mode="stretch_width", template="bootstrap")\n\npn.pane.Markdown('\\nIn this example we are building a Vue.js component containing an input field and a button that will update the \`value\` parameter of the \`PDBInput\` component:\\n\\n').servable()\n\n\n\nclass PDBInput(BootstrapVueComponent):\n\n\n\n    value = param.String()\n\n\n\n    _template = """\n\n    <div id="container" style="height:100%; width:100%">\n\n      <vue-component></vue-component>\n\n    </div>\n\n    """\n\n\n\n    _scripts = {\n\n        "render": """\n\n    const template = \`\n\n    <div>\n\n      <b-form v-on:keydown.enter.prevent>\n\n        <b-form-input v-model="pdb_id" placeholder="Enter PDB ID" required></b-form-input>\n\n        <b-button variant="secondary" size="sm" v-on:click="setPDBId" style="margin-top:10px;width:100%">\n\n            Retrieve PDB metadata\n\n        </b-button>\n\n      </b-form>\n\n    </div>\`\n\n    const vue_component = {\n\n      template: template,\n\n      delimiters: ['[[', ']]'],\n\n      data: function () {\n\n        return {\n\n          pdb_id: data.value,\n\n        }\n\n      },\n\n      methods: {\n\n        setPDBId() {\n\n          data.value = this.pdb_id\n\n        }\n\n      }\n\n    }\n\n    const el = new Vue({\n\n        el: container,\n\n        components: {\n\n            'vue-component': vue_component\n\n        }\n\n    })\n\n    """\n\n    }\n\npn.pane.Markdown('\\n## Featurize Protein Structure\\n\\nUse the Vue component below to retrieve PDB metadata from [KLIFS](https://klifs.net/). For example for *\`2xyu\`* or *\`4WSQ\`*:\\n\\n').servable()\n\nURL = "https://klifs.net/api/structures_pdb_list"\n\n\n\ndef get_pdb_data_from_klifs(pdb_id):\n\n    if not pdb_id:\n\n        return "Please specify a PDB ID."\n\n\n\n    params = {'pdb-codes': pdb_id}\n\n    res = requests.get(url = URL, params = params)\n\n    data = res.json()\n\n\n\n    if res.status_code == 400:\n\n        return f"Error 400, Could not get PDB {pdb_id}", data[1]\n\n\n\n    return data[0]\n\n\n\npdb_input = PDBInput(height=90, max_width=800)\n\n\n\niget_klifs_data = pn.bind(get_pdb_data_from_klifs, pdb_id=pdb_input.param.value)\n\n\n\npn.Column(\n\n    pdb_input,\n\n    pn.pane.JSON(iget_klifs_data, theme="light")\n\n).servable()\n\npn.state.template.title = 'Wrap a Vue component'\n\nawait write_doc()`)
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