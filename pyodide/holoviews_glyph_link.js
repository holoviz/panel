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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport numpy as np\n\nimport panel as pn\n\n\n\nimport holoviews as hv\n\nimport holoviews.plotting.bokeh\n\n\n\npn.extension()\n\npn.pane.Markdown('\\nHoloViews-generated Bokeh plots can be statically linked to widgets that control their properties, allowing you to export static HTML files that allow end-user customization of appearance.\\n\\n').servable()\n\nfrom bokeh.core.enums import MarkerType\n\n\n\ncolors = ["black", "red", "blue", "green", "gray"]\n\nmarkers = list(MarkerType)\n\n\n\n# Define widget for properties we want to change\n\nalpha_widget = pn.widgets.FloatSlider(value=0.5, start=0, end=1, name='Alpha')\n\nsize_widget = pn.widgets.FloatSlider(value=12, start=3, end=20, name='Size')\n\ncolor_widget = pn.widgets.ColorPicker(value='#f80000', name='Color')\n\nmarker_widget = pn.widgets.Select(options=markers, value='circle', name='Marker')\n\n\n\n# Declare a Points object and apply some options\n\npoints = hv.Points(np.random.randn(200, 2)).options(\n\n    padding=0.1, height=500, line_color='black', responsive=True)\n\n\n\n# Link the widget value parameter to the property on the glyph\n\nalpha_widget.jslink(points, value='glyph.fill_alpha')\n\nsize_widget.jslink(points, value='glyph.size')\n\ncolor_widget.jslink(points, value='glyph.fill_color')\n\nmarker_widget.jslink(points, value='glyph.marker')\n\n\n\npn.Row(pn.Column(alpha_widget, color_widget, marker_widget, size_widget), points).servable()\n\n\nawait write_doc()`)
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