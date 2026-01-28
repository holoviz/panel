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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport param\n\nimport panel as pn\n\n\n\nfrom panel.custom import ReactComponent\n\n\n\nclass MaterialComponent(ReactComponent):\n\n\n\n    _importmap = {\n\n        "imports": {\n\n            "@mui/material/": "https://esm.sh/@mui/material@5.16.7/",\n\n        }\n\n    }\n\n\n\npn.extension(template='material')\n\npn.pane.Markdown('\\nThis example demonstrates how to wrap Material UI components using \`ReactComponent\`.\\n\\n').servable()\n\n\n\nclass Button(MaterialComponent):\n\n\n\n    disabled = param.Boolean(default=False)\n\n\n\n    label = param.String(default='')\n\n\n\n    variant = param.Selector(objects=["contained", "outlined", "text"])\n\n\n\n    _esm = """\n\n    import Button from '@mui/material/Button';\n\n\n\n    export function render({ model }) {\n\n      const [label] = model.useState("label")\n\n      const [variant] = model.useState("variant")\n\n      const [disabled] = model.useState("disabled")\n\n      return (\n\n        <Button disabled={disabled} variant={variant}>{label || 'Click me!'}</Button>\n\n      )\n\n    }\n\n    """\n\n\n\nclass Rating(MaterialComponent):\n\n\n\n    value = param.Number(default=0, bounds=(0, 5))\n\n\n\n    _esm = """\n\n    import Rating from '@mui/material/Rating'\n\n\n\n    export function render({model}) {\n\n      const [value, setValue] = model.useState("value")\n\n      return (\n\n        <Rating\n\n          value={value}\n\n          onChange={(event, newValue) => setValue(newValue) }\n\n        />\n\n      )\n\n    }\n\n    """\n\n\n\nclass DiscreteSlider(MaterialComponent):\n\n\n\n    marks = param.List(default=[\n\n        {'value': 0, 'label': '0\xb0C'},\n\n        {'value': 20, 'label': '20\xb0C'},\n\n        {'value': 37, 'label': '37\xb0C'},\n\n        {'value': 100, 'label': '100\xb0C'},\n\n    ])\n\n\n\n    value = param.Number(default=20)\n\n\n\n    _esm = """\n\n    import Box from '@mui/material/Box';\n\n    import Slider from '@mui/material/Slider';\n\n\n\n    export function render({ model }) {\n\n      const [value, setValue] = model.useState("value")\n\n      const [marks] = model.useState("marks")\n\n      return (\n\n        <Box sx={{ width: 300 }}>\n\n          <Slider\n\n            aria-label="Restricted values"\n\n            defaultValue={value}\n\n            marks={marks}\n\n            onChange={(e) => setValue(e.target.value)}\n\n            step={null}\n\n            valueLabelDisplay="auto"\n\n          />\n\n        </Box>\n\n      );\n\n    }\n\n    """\n\n\n\nbutton = Button()\n\nrating = Rating(value=3)\n\nslider = DiscreteSlider()\n\n\n\npn.Row(\n\n    pn.Column(button.controls(['disabled', 'label', 'variant']), button),\n\n    pn.Column(rating.controls(['value']), rating),\n\n    pn.Column(slider.controls(['value']), slider),\n\n).servable()\n\npn.state.template.title = 'Wrapping Material UI components'\n\nawait write_doc()`)
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