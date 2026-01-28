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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport param\n\nimport panel as pn\n\n\n\nfrom panel.custom import JSComponent\n\n\n\npn.extension()\n\n\n\nclass Canvas(JSComponent):\n\n\n\n    color = param.Color(default='#000000')\n\n\n\n    line_width = param.Number(default=1, bounds=(0.1, 10))\n\n\n\n    uri = param.String()\n\n\n\n    _esm = """\n\nexport function render({model, el}){\n\n    // Create canvas\n\n    const canvas = document.createElement('canvas');\n\n    canvas.style.border = '1px solid';\n\n    canvas.width = model.width;\n\n    canvas.height = model.height;\n\n    const ctx = canvas.getContext("2d")\n\n\n\n    // Set up drawing handlers\n\n    let start = null\n\n    canvas.addEventListener('mousedown', (event) => {\n\n      start = event\n\n      ctx.beginPath()\n\n      ctx.moveTo(start.offsetX, start.offsetY)\n\n    })\n\n    canvas.addEventListener('mousemove', (event) => {\n\n      if (start == null)\n\n        return\n\n      ctx.lineTo(event.offsetX, event.offsetY)\n\n      ctx.stroke()\n\n    })\n\n    canvas.addEventListener('mouseup', () => {\n\n      start = null\n\n    })\n\n\n\n    // Update styles\n\n    model.on(['color', 'line_width'], () => {\n\n      ctx.lineWidth = model.line_width;\n\n      ctx.strokeStyle = model.color;\n\n    })\n\n\n\n    // Create clear button\n\n    const clearButton = document.createElement('button');\n\n    clearButton.textContent = 'Clear';\n\n    clearButton.addEventListener('click', () => {\n\n      ctx.clearRect(0, 0, canvas.width, canvas.height)\n\n      model.uri = ""\n\n    })\n\n    // Create save button\n\n    const saveButton = document.createElement('button');\n\n    saveButton.textContent = 'Save';\n\n    saveButton.addEventListener('click', () => {\n\n      model.uri = canvas.toDataURL();\n\n    })\n\n    // Append elements to the parent element\n\n    el.appendChild(canvas);\n\n    el.appendChild(clearButton);\n\n    el.appendChild(saveButton);\n\n}\n\n"""\n\n\n\ncanvas = Canvas(height=400, width=400)\n\npng_view = pn.pane.HTML(\n\n    pn.rx("<img src='{uri}'></img>").format(uri=canvas.param.uri),\n\n    height=400\n\n)\n\n\n\npn.Column(\n\n    '# Drag on canvas to draw\\n To export the drawing to a png click save.',\n\n    pn.Param(\n\n        canvas.param,\n\n        default_layout=pn.Row,\n\n        parameters=['color', 'line_width'],\n\n        show_name=False\n\n    ),\n\n    pn.Row(\n\n        canvas,\n\n        png_view\n\n    ),\n\n).servable()\n\n\nawait write_doc()`)
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