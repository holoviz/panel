importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.5/full/pyodide.js");

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
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.7.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.7.0/dist/wheels/panel-1.7.0-py3-none-any.whl', 'pyodide-http==0.2.1']
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
  \nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport panel as pn\n\n\n\npn.extension('vega', template='bootstrap')\n\npn.pane.Markdown('\\nThis example demonstrates how to link Panel widgets to a Vega pane by editing the Vega spec using callbacks and triggering updates in the plot.\\n\\n').servable()\n\nimdb = {\n\n  "$schema": "https://vega.github.io/schema/vega-lite/v4.json",\n\n  "data": {"url": "https://raw.githubusercontent.com/vega/vega/master/docs/data/movies.json"},\n\n  "transform": [{\n\n    "filter": {"and": [\n\n      {"field": "IMDB Rating", "valid": True},\n\n      {"field": "Rotten Tomatoes Rating", "valid": True}\n\n    ]}\n\n  }],\n\n  "mark": "rect",\n\n  "width": "container",\n\n  "height": 400,\n\n  "encoding": {\n\n    "x": {\n\n      "bin": {"maxbins":60},\n\n      "field": "IMDB Rating",\n\n      "type": "quantitative"\n\n    },\n\n    "y": {\n\n      "bin": {"maxbins": 40},\n\n      "field": "Rotten Tomatoes Rating",\n\n      "type": "quantitative"\n\n    },\n\n    "color": {\n\n      "aggregate": "count",\n\n      "type": "quantitative"\n\n    }\n\n  },\n\n  "config": {\n\n    "view": {\n\n      "stroke": "transparent"\n\n    }\n\n  }\n\n}\n\n\n\nvega = pn.pane.Vega(imdb, height=425)\n\n\n\n# Declare range slider to adjust the color limits\n\ncolor_lims = pn.widgets.RangeSlider(name='Color limits', start=0, end=125, value=(0, 40), step=1)\n\ncolor_lims.jslink(vega, code={'value': """\n\ntarget.data.encoding.color.scale = {domain: source.value};\n\ntarget.properties.data.change.emit()\n\n"""});\n\n\n\n# Declare slider to control the number of bins along the x-axis\n\nimdb_bins = pn.widgets.IntSlider(name='IMDB Ratings Bins', start=0, end=125, value=60, step=25)\n\nimdb_bins.jslink(vega, code={'value': """\n\ntarget.data.encoding.x.bin.maxbins = source.value;\n\ntarget.properties.data.change.emit()\n\n"""});\n\n\n\n# Declare slider to control the number of bins along the y-axis\n\ntomato_bins = pn.widgets.IntSlider(name='Rotten Tomato Ratings Bins', start=0, end=125, value=40, step=25)\n\ntomato_bins.jslink(vega, code={'value': """\n\ntarget.data.encoding.y.bin.maxbins = source.value;\n\ntarget.properties.data.change.emit()\n\n"""});\n\n\n\npn.Row(\n\n    vega, pn.Column(color_lims, imdb_bins, tomato_bins)\n\n)\n\npn.state.template.title = 'Vega Link'\n\nawait write_doc()
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