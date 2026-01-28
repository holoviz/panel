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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'numpy', 'param']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport panel as pn\n\nimport param\n\nimport numpy as np\n\n\n\npn.extension(template='bootstrap')\n\npn.pane.Markdown("\\nThis example demonstrates how to use the Param library to express nested hierarchies of classes whose parameters can be edited in a GUI, without tying those classes to Panel or any other GUI framework.\\n\\nFor this purpose we create a hierarchy of three classes that draw Bokeh plots. At the top level there is a \`\`ShapeViewer\`\` that allows selecting between different \`\`Shape\`\` classes. The Shape classes include a subobject controlling the \`\`Style\`\` (i.e. the \`color\` and \`line_width\`) of the drawn shapes.\\n\\nIn each case, \`param.depends\` is used to indicate which parameter that computation depends on, either a parameter of this object (as for  \`radius\` below) or a parameter of a subobject (i.e., a parameter of one of this object's parameters, as for \`style.color\` below).\\n\\n").servable()\n\nfrom bokeh.plotting import figure\n\n\n\nclass Style(param.Parameterized):\n\n\n\n    color = param.Color(default='#0f6f0f')\n\n\n\n    line_width = param.Number(default=2, bounds=(0, 10))\n\n\n\n\n\nclass Shape(param.Parameterized):\n\n\n\n    radius = param.Number(default=1, bounds=(0, 1))\n\n\n\n    style = param.Parameter(precedence=3)\n\n\n\n    def __init__(self, **params):\n\n        if 'style' not in params:\n\n            params['style'] = Style(name='Style')\n\n        super(Shape, self).__init__(**params)\n\n        self.figure = figure(x_range=(-1, 1), y_range=(-1, 1), sizing_mode="stretch_width", height=400)\n\n        self.renderer = self.figure.line(*self._get_coords())\n\n        self._update_style()\n\n\n\n    @param.depends('style.color', 'style.line_width', watch=True)\n\n    def _update_style(self):\n\n        self.renderer.glyph.line_color = self.style.color\n\n        self.renderer.glyph.line_width = self.style.line_width\n\n\n\n    def _get_coords(self):\n\n        return [], []\n\n\n\n    def view(self):\n\n        return self.figure\n\n\n\n\n\nclass Circle(Shape):\n\n\n\n    n = param.Integer(default=100, precedence=-1)\n\n\n\n    def _get_coords(self):\n\n        angles = np.linspace(0, 2*np.pi, self.n+1)\n\n        return (self.radius*np.sin(angles),\n\n                self.radius*np.cos(angles))\n\n\n\n    @param.depends('radius', watch=True)\n\n    def update(self):\n\n        xs, ys = self._get_coords()\n\n        self.renderer.data_source.data.update({'x': xs, 'y': ys})\n\n\n\nclass NGon(Circle):\n\n\n\n    n = param.Integer(default=3, bounds=(3, 10), precedence=1)\n\n\n\n    @param.depends('radius', 'n', watch=True)\n\n    def update(self):\n\n        xs, ys = self._get_coords()\n\n        self.renderer.data_source.data.update({'x': xs, 'y': ys})\n\n\n\n\n\nshapes = [NGon(name='NGon'), Circle(name='Circle')]\n\npn.pane.Markdown("\\nHaving defined our basic domain model (of shapes in this case), we can now make a generic viewer using Panel without requiring or encoding information about the underlying domain objects.  Here, we define a \`view\` method that will be called whenever any of the possible parameters that a shape might have changes, without necessarily knowing what those are (as for \`shape.param\` below). That way, if someone adds a \`Line\` shape that has no \`n\` parameter but has \`orientation\`, the viewer should continue to work and be responsive. We can also depend on specific parameters (as for \`shape.radius\`) if we wish. Either way, the panel should then reactively update to each of the shape's parameters as they are changed in the browser:\\n\\n").servable()\n\nclass ShapeViewer(param.Parameterized):\n\n\n\n    shape = param.Selector(default=shapes[0], objects=shapes)\n\n\n\n    @param.depends('shape', 'shape.param')\n\n    def view(self):\n\n        return self.shape.view()\n\n\n\n    @param.depends('shape', 'shape.radius')\n\n    def title(self):\n\n        return '## %s (radius=%.1f)' % (type(self.shape).__name__, self.shape.radius)\n\n\n\n    def panel(self):\n\n        return pn.Column(self.title, self.view, sizing_mode="stretch_width")\n\n\n\n\n\n# Instantiate and display ShapeViewer\n\nviewer = ShapeViewer()\n\nsubpanel = pn.Column()\n\n\n\npn.Row(\n\n    pn.Column(pn.Param(viewer.param, expand_layout=subpanel, name="Shape Settings"), subpanel),\n\n    viewer.panel(),\n\n).servable()\n\npn.state.template.title = 'Param Subobjects'\n\nawait write_doc()`)
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