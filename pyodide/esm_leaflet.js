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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'numpy', 'pandas', 'param']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport param\n\nimport pandas as pd\n\nimport panel as pn\n\nimport numpy as np\n\n\n\nfrom panel.custom import JSComponent\n\n\n\nclass LeafletHeatMap(JSComponent):\n\n\n\n    attribution = param.String(doc="Tile source attribution.")\n\n\n\n    blur = param.Integer(default=18, bounds=(5, 50), doc="Amount of blur to apply to heatmap")\n\n\n\n    center = param.XYCoordinates(default=(0, 0), doc="The center of the map.")\n\n\n\n    data = param.DataFrame(doc="The heatmap data to plot, should have 'x', 'y' and 'value' columns.")\n\n\n\n    tile_url = param.String(doc="Tile source URL with {x}, {y} and {z} parameter")\n\n\n\n    min_alpha = param.Number(default=0.2, bounds=(0, 1), doc="Minimum alpha of the heatmap")\n\n\n\n    radius = param.Integer(default=25, bounds=(5, 50), doc="The radius of heatmap values on the map")\n\n\n\n    x = param.String(default='longitude', doc="Column in the data with longitude coordinates")\n\n\n\n    y = param.String(default='latitude', doc="Column in the data with latitude coordinates")\n\n\n\n    value = param.String(doc="Column in the data with the data values")\n\n\n\n    zoom = param.Integer(default=13, bounds=(0, 21), doc="The plots zoom-level")\n\n\n\n    _esm = """\n\n    import L from "https://esm.sh/leaflet@1.7.1"\n\n    import * as Lheat from "https://esm.sh/leaflet.heat@0.2.0"\n\n\n\n    function get_records(model) {\n\n      const records = []\n\n      for (let i=0; i<model.data.index.length; i++)\n\n        records.push([model.data[model.y][i], model.data[model.x][i], model.data[model.value][i]])\n\n      return records\n\n    }\n\n\n\n    export function render({ model, el }) {\n\n      const map = L.map(el).setView(model.center, model.zoom);\n\n\n\n      map.on('change:zoom', () => { model.zoom = map.getZoom() })\n\n\n\n      const tileLayer = L.tileLayer(model.tile_url, {\n\n        attribution: model.attribution,\n\n        maxZoom: 21,\n\n        tileSize: 512,\n\n        zoomOffset: -1,\n\n      }).addTo(map)\n\n\n\n      model.on("after_render", () => {\n\n        console.log(Lheat)\n\n        map.invalidateSize()\n\n        const data = get_records(model)\n\n        const heatLayer = L.heatLayer(\n\n          data, {\n\n            blur: model.blur,\n\n            radius: model.radius,\n\n            max: 10,\n\n            minOpacity: model.min_alpha\n\n        }).addTo(map)\n\n\n\n        model.on(['blur', 'min_alpha', 'radius'], () => {\n\n          heatLayer.setOptions({\n\n            blur: model.blur,\n\n            minOpacity: model.min_alpha,\n\n            radius: model.radius,\n\n          })\n\n        })\n\n        model.on('change:data', () => heatLayer.setLatLngs(get_records(model)))\n\n      })\n\n    }"""\n\n\n\n    _stylesheets = ['https://unpkg.com/leaflet@1.7.1/dist/leaflet.css']\n\npn.extension(template='bootstrap')\n\n\n\nurl = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv"\n\n\n\nearthquakes = pd.read_csv(url)\n\n\n\nheatmap = LeafletHeatMap(\n\n    attribution='Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',\n\n    data=earthquakes[['longitude', 'latitude', 'mag']],\n\n    min_height=500,\n\n    tile_url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.jpg',\n\n    radius=30,\n\n    sizing_mode='stretch_both',\n\n    value='mag',\n\n    zoom=2,\n\n)\n\n\n\ndescription=pn.pane.Markdown(f'## Earthquakes between {earthquakes.time.min()} and {earthquakes.time.max()}\\n\\n[Data Source]({url})', sizing_mode="stretch_width")\n\n\n\npn.Column(\n\n    description,\n\n    pn.Row(\n\n        heatmap.controls(['blur', 'min_alpha', 'radius', 'zoom']).servable(target='sidebar'),\n\n        heatmap.servable(),\n\n        sizing_mode='stretch_both'\n\n    ),\n\n    sizing_mode='stretch_both'\n\n)\n\npn.state.template.title = 'Build a Custom Leaflet Component'\n\nawait write_doc()`)
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