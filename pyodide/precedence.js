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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport panel as pn\n\nimport param\n\n\n\npn.extension(template='bootstrap')\n\npn.pane.Markdown('\\nThis example demonstrates how to order and hide widgets by means of the \`\`precedence\`\` and  \`\`display_threshold\`\` attributes.\\n\\nEach \`\`Parameter\`\` object has a \`\`precedence\`\` attribute that is defined as follows  in the documentation of \`\`param\`\`:\\n\\n> \`\`precedence\`\` is a value, usually in the range 0.0 to 1.0, that allows the order of Parameters in a class to be defined (for e.g. in GUI menus).\\n> A negative precedence indicates a parameter that should be hidden in e.g. GUI menus.\\n\\nA \`Param\` pane has a \`\`display_threshold\`\` attribute defaulting to 0 and defined as follows:\\n\\n> Parameters with precedence below this value are not displayed.\\n\\nThe interactive example below helps to understand how the interplay between these two attributes affects the display of widgets.\\n\\nThe \`\`PrecedenceTutorial\`\` class emulates a dummy app whose display we want to control and that consists of three input parameters, \`\`x\`\`, \`\`y\`\` and \`\`z\`\`. These parameters will be displayed by \`panel\` with their associated default widgets. Additionally, the class declares the four parameters that will control the dummy app display: \`\`x_precedence\`\`, \`\`y_precedence\`\` and \`\`z_precedence\`\` and \`\`dummy_app_display_threshold\`\`.\\n\\n').servable()\n\nclass Precedence(param.Parameterized):\n\n\n\n    # Parameters of the dummy app.\n\n    x = param.Number(precedence=-1)\n\n    y = param.Boolean(precedence=3)\n\n    z = param.String(precedence=2)\n\n\n\n    # Parameters of the control app.\n\n    x_precedence = param.Number(default=x.precedence, bounds=(-10, 10), step=1)\n\n    y_precedence = param.Number(default=y.precedence, bounds=(-10, 10), step=1)\n\n    z_precedence = param.Number(default=z.precedence, bounds=(-10, 10), step=1)\n\n    dummy_app_display_threshold = param.Number(default=1, bounds=(-10, 10), step=1)\n\n\n\n    def __init__(self):\n\n        super().__init__()\n\n        # Building the dummy app as a Param pane in here so that its \`\`display_threshold\`\`\n\n        # parameter can be accessed and linked via @param.depends(...).\n\n        self.dummy_app = pn.Param(\n\n            self.param,\n\n            parameters=["x", "y", "z"],\n\n            widgets={\n\n                "x": {"styles": {"background": "#fac400"}},\n\n                "y": {"styles": {"background": "#07d900"}},\n\n                "z": {"styles": {"background": "#00c0d9"}},\n\n            },\n\n            show_name=False\n\n        )\n\n\n\n    # Linking the two apps here.\n\n    @param.depends("dummy_app_display_threshold", "x_precedence", "y_precedence", "z_precedence", watch=True)\n\n    def update_precedences_and_threshold(self):\n\n        self.param.x.precedence = self.x_precedence\n\n        self.param.y.precedence = self.y_precedence\n\n        self.param.z.precedence = self.z_precedence\n\n        self.dummy_app.display_threshold = self.dummy_app_display_threshold\n\n\n\nprecedence_model = Precedence()\n\n\n\n# Building the control app as a Param pane too.\n\ncontrol_app = pn.Param(\n\n    precedence_model.param,\n\n    parameters=["x_precedence", "y_precedence", "z_precedence", "dummy_app_display_threshold"],\n\n    widgets={\n\n        "x_precedence": {"styles": {"background": "#fac400"}},\n\n        "y_precedence": {"styles": {"background": "#07d900"}},\n\n        "z_precedence": {"styles": {"background": "#00c0d9"}},\n\n    },\n\n    show_name=False\n\n)\n\n\n\n# Building the complete interactive example.\n\npn.Column(\n\n    "## Precedence Example",\n\n    "Moving the sliders of the control app should update the display of the dummy app.",\n\n    pn.Row(\n\n        pn.Column("**Control app**", control_app),\n\n        pn.Column("**Dummy app**", precedence_model.dummy_app)\n\n    )\n\n).servable()\n\npn.state.template.title = 'Param Precedence'\n\nawait write_doc()`)
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