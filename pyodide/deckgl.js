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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport json\n\nimport panel as pn\n\n\n\npn.extension('codeeditor', 'deckgl', template='bootstrap')\n\npn.pane.Markdown('\\nThis example demonstrates how to \`jslink\` a JSON editor to a DeckGL pane to enable super fast, live editing of a plot:\\n\\n').servable()\n\nMAPBOX_KEY = "pk.eyJ1IjoicGFuZWxvcmciLCJhIjoiY2s1enA3ejhyMWhmZjNobjM1NXhtbWRrMyJ9.B_frQsAVepGIe-HiOJeqvQ"\n\n\n\njson_spec = {\n\n    "initialViewState": {\n\n        "bearing": -27.36,\n\n        "latitude": 52.2323,\n\n        "longitude": -1.415,\n\n        "maxZoom": 15,\n\n        "minZoom": 5,\n\n        "pitch": 40.5,\n\n        "zoom": 6\n\n    },\n\n    "layers": [{\n\n        "@@type": "HexagonLayer",\n\n        "autoHighlight": True,\n\n        "coverage": 1,\n\n        "data": "https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv",\n\n        "elevationRange": [0, 3000],\n\n        "elevationScale": 50,\n\n        "extruded": True,\n\n        "getPosition": "@@=[lng, lat]",\n\n        "id": "8a553b25-ef3a-489c-bbe2-e102d18a3211", "pickable": True\n\n    }],\n\n    "mapStyle": "mapbox://styles/mapbox/dark-v9",\n\n    "views": [{"@@type": "MapView", "controller": True}]\n\n}\n\n\n\n\n\nview_editor = pn.widgets.CodeEditor(\n\n    value=json.dumps(json_spec['initialViewState'], indent=4),\n\n    theme= 'monokai', width=500, height=225\n\n)\n\nlayer_editor = pn.widgets.CodeEditor(\n\n    value=json.dumps(json_spec['layers'][0], indent=4),\n\n    theme= 'monokai', width=500, height=365\n\n)\n\n\n\ndeck_gl = pn.pane.DeckGL(json_spec, mapbox_api_key=MAPBOX_KEY, sizing_mode='stretch_width', height=600)\n\n\n\nview_editor.jscallback(args={'deck_gl': deck_gl}, value="deck_gl.initialViewState = JSON.parse(cb_obj.code)")\n\nlayer_editor.jscallback(args={'deck_gl': deck_gl}, value="deck_gl.layers = [JSON.parse(cb_obj.code)]")\n\n\n\npn.Row(pn.Column(view_editor, layer_editor), deck_gl).servable()\n\npn.state.template.title = 'Deck.gl JSON Editor'\n\nawait write_doc()`)
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