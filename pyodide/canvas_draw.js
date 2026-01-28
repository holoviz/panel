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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'param']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport param\n\nimport panel as pn\n\n\n\nfrom panel.reactive import ReactiveHTML\n\n\n\npn.extension(template='bootstrap')\n\npn.pane.Markdown('\\nThis example shows how to use the \`ReactiveHTML\` component to develop a **Drawable Canvas**.\\n\\n').servable()\n\nclass Canvas(ReactiveHTML):\n\n\n\n    color = param.Color(default='#000000')\n\n\n\n    line_width = param.Number(default=1, bounds=(0.1, 10))\n\n\n\n    uri = param.String()\n\n\n\n    _template = """\n\n    <canvas\n\n      id="canvas"\n\n      style="border: 1px solid"\n\n      width="${model.width}"\n\n      height="${model.height}"\n\n      onmousedown="${script('start')}"\n\n      onmousemove="${script('draw')}"\n\n      onmouseup="${script('end')}"\n\n    >\n\n    </canvas>\n\n    <button id="clear" onclick='${script("clear")}'>Clear</button>\n\n    <button id="save" onclick='${script("save")}'>Save</button>\n\n    """\n\n\n\n    _scripts = {\n\n        'render': """\n\n          state.ctx = canvas.getContext("2d")\n\n        """,\n\n        'start': """\n\n          state.start = event\n\n          state.ctx.beginPath()\n\n          state.ctx.moveTo(state.start.offsetX, state.start.offsetY)\n\n        """,\n\n        'draw': """\n\n          if (state.start == null)\n\n            return\n\n          state.ctx.lineTo(event.offsetX, event.offsetY)\n\n          state.ctx.stroke()\n\n        """,\n\n        'end': """\n\n          delete state.start\n\n        """,\n\n        'clear': """\n\n          state.ctx.clearRect(0, 0, canvas.width, canvas.height);\n\n        """,\n\n        'save': """\n\n          data.uri = canvas.toDataURL();\n\n        """,\n\n        'line_width': """\n\n          state.ctx.lineWidth = data.line_width;\n\n        """,\n\n        'color': """\n\n          state.ctx.strokeStyle = data.color;\n\n        """\n\n    }\n\n\n\ncanvas = Canvas(width=400, height=400)\n\n\n\n# We create a separate HTML element which syncs with the uri parameter of the Canvas\n\n\n\npng_view = pn.pane.HTML(height=400)\n\n\n\ncanvas.jslink(png_view, code={'uri': "target.text = \`<img src='${source.uri}'></img>\`"})\n\n\n\npn.Row(\n\n    canvas.controls(['color', 'line_width']).servable(target='sidebar'),\n\n    pn.Column(\n\n        '# Drag on canvas to draw\\n To export the drawing to a png click save.',\n\n        pn.Row(\n\n            canvas,\n\n            png_view\n\n        ),\n\n    ).servable()\n\n)\n\npn.state.template.title = 'Build a Custom Canvas Component'\n\nawait write_doc()`)
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