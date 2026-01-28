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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport param\n\nimport panel as pn\n\n\n\nfrom panel.reactive import ReactiveHTML\n\n\n\nclass MaterialBase(ReactiveHTML):\n\n\n\n    __javascript__ = ['https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js']\n\n\n\n    __css__ = ['https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css']\n\n\n\n    _extension_name = 'material_ui'\n\n\n\npn.extension('material_ui', template='material')\n\npn.pane.Markdown('\\nThis example demonstrates how to wrap Material UI components using \`ReactiveHTML\`.\\n\\n').servable()\n\nclass MaterialTextField(MaterialBase):\n\n\n\n    value = param.String(default='')\n\n\n\n    _template = """\n\n    <label id="text-field" class="mdc-text-field mdc-text-field--filled">\n\n      <span class="mdc-text-field__ripple"></span>\n\n      <span class="mdc-floating-label">Label</span>\n\n      <input id="text-input" type="text" class="mdc-text-field__input" aria-labelledby="my-label" value="${value}"></input>\n\n      <span class="mdc-line-ripple"></span>\n\n    </label>\n\n    """\n\n\n\n    _dom_events = {'text-input': ['change']}\n\n\n\n    _scripts = {\n\n        'render': "mdc.textField.MDCTextField.attachTo(text_field);"\n\n    }\n\n\n\nclass MaterialSlider(MaterialBase):\n\n\n\n    end = param.Number(default=100)\n\n\n\n    start = param.Number(default=0)\n\n\n\n    value = param.Number(default=50)\n\n\n\n    _template = """\n\n    <div id="mdc-slider" class="mdc-slider" style="width: ${model.width}px">\n\n      <input id="slider-input" class="mdc-slider__input" min="${start}" max="${end}" value="${value}">\n\n      </input>\n\n      <div class="mdc-slider__track">\n\n        <div class="mdc-slider__track--inactive"></div>\n\n        <div class="mdc-slider__track--active">\n\n          <div class="mdc-slider__track--active_fill"></div>\n\n        </div>\n\n      </div>\n\n      <div class="mdc-slider__thumb">\n\n        <div class="mdc-slider__thumb-knob"></div>\n\n      </div>\n\n    </div>\n\n    """\n\n\n\n    _scripts = {\n\n        'render': """\n\n            slider_input.setAttribute('value', data.value)\n\n            state.slider = mdc.slider.MDCSlider.attachTo(mdc_slider)\n\n        """,\n\n        'value': """\n\n            state.slider.setValue(data.value)\n\n        """\n\n    }\n\n\n\nslider     = MaterialSlider(value=5, start=0, end=100, width=200)\n\ntext_field = MaterialTextField()\n\n\n\npn.Row(\n\n    pn.Column(\n\n        slider.controls(['value']),\n\n        slider\n\n    ),\n\n    pn.Column(\n\n        text_field.controls(['value']),\n\n        text_field\n\n    ),\n\n).servable()\n\npn.state.template.title = 'Wrapping Material UI components'\n\nawait write_doc()`)
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