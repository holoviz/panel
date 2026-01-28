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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'fastparquet', 'pyodide-http']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport panel as pn\nimport pandas as pd\nimport param\n\npn.extension('deckgl', design='bootstrap', theme='dark', template='bootstrap')\n\n_pn__state._cell_outputs['fbba7ec1-5e4c-4d04-a21a-5b5d3fb67bf9'].append((pn.state.template.config.raw_css.append("""\n#main {\n  padding: 0;\n}""")))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['fbba7ec1-5e4c-4d04-a21a-5b5d3fb67bf9'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['fbba7ec1-5e4c-4d04-a21a-5b5d3fb67bf9'].append(_fig__out)\n\n_pn__state._cell_outputs['9925cce4-516f-4f44-8c5d-cd7cb72d3f16'].append("""## Define App""")\nclass App(pn.viewable.Viewer):\n\n    data = param.DataFrame(precedence=-1)\n\n    view = param.DataFrame(precedence=-1)\n\n    arc_view = param.DataFrame(precedence=-1)\n\n    radius = param.Integer(default=50, bounds=(20, 1000))\n\n    elevation = param.Integer(default=10, bounds=(0, 50))\n\n    hour = param.Integer(default=0, bounds=(0, 23))\n\n    speed = param.Integer(default=1, bounds=(0, 10), precedence=-1)\n\n    play = param.Event(label='\u25b7')\n\n    def __init__(self, **params):\n        self.deck_gl = None\n        super().__init__(**params)\n        self._update_arc_view()\n        self.deck_gl = pn.pane.DeckGL(\n            self.spec,\n            throttle={'click': 10},\n            sizing_mode='stretch_both',\n            margin=0\n        )\n        self.deck_gl.param.watch(self._update_arc_view, 'click_state')\n        self._playing = False\n        self._cb = pn.state.add_periodic_callback(\n            self._update_hour, 1000//self.speed, start=False\n        )\n\n    @param.depends('view', 'radius', 'elevation', 'arc_view')\n    def spec(self):\n        return {\n            "initialViewState": {\n                "bearing": 0,\n                "latitude": 40.7,\n                "longitude": -73.9,\n                "maxZoom": 15,\n                "minZoom": 5,\n                "pitch": 40.5,\n                "zoom": 11\n            },\n            "mapStyle": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",\n            "layers": [self.hex_layer, self.arc_layer],\n            "views": [\n                {"@@type": "MapView", "controller": True}\n            ]\n        }\n\n    @property\n    def hex_layer(self):\n        return {\n            "@@type": "HexagonLayer",\n            "autoHighlight": True,\n            "coverage": 1,\n            "data": self.data if self.view is None else self.view,\n            "elevationRange": [0, 100],\n            "elevationScale": self.elevation,\n            "radius": self.radius,\n            "extruded": True,\n            "getPosition": "@@=[pickup_x, pickup_y]",\n            "id": "8a553b25-ef3a-489c-bbe2-e102d18a3211"\n        }\n\n    @property\n    def arc_layer(self):\n        return {\n            "@@type": "ArcLayer",\n            "id": 'arc-layer',\n            "data": self.arc_view,\n            "pickable": True,\n            "getWidth": 2,\n            "getSourcePosition": "@@=[pickup_x, pickup_y]",\n            "getTargetPosition": "@@=[dropoff_x, dropoff_y]",\n            "getSourceColor": [0, 255, 0, 180],\n            "getTargetColor": [240, 100, 0, 180]\n        }\n\n    def _update_hour(self):\n        self.hour = (self.hour+1) % 24\n\n    @param.depends('hour', watch=True, on_init=True)\n    def _update_hourly_view(self):\n        self.view = self.data[self.data.hour==self.hour]\n\n    @param.depends('view', 'radius', watch=True)\n    def _update_arc_view(self, event=None):\n        data = self.data if self.view is None else self.view\n        lon, lat, = (-73.9857, 40.7484)\n        if self.deck_gl:\n            lon, lat = self.deck_gl.click_state.get('coordinate', (lon, lat))\n        tol = self.radius / 100000\n        self.arc_view = data[\n            (data.pickup_x>=float(lon-tol)) &\n            (data.pickup_x<=float(lon+tol)) &\n            (data.pickup_y>=float(lat-tol)) &\n            (data.pickup_y<=float(lat+tol))\n        ]\n\n    @param.depends('speed', watch=True)\n    def _update_speed(self):\n        self._cb.period = 1000//self.speed\n\n    @param.depends('play', watch=True)\n    def _play_pause(self):\n        if self._playing:\n            self._cb.stop()\n            self.param.play.label = '\u25b7'\n            self.param.speed.precedence = -1\n        else:\n            self._cb.start()\n            self.param.play.label = '\u275a\u275a'\n            self.param.speed.precedence = 1\n        self._playing = not self._playing\n\n    @property\n    def controls(self):\n        return pn.Param(app.param, show_name=False)\n\n    def __panel__(self):\n        return pn.Row(\n            self.controls,\n            self.deck_gl,\n            min_height=800,\n            sizing_mode='stretch_both',\n        )\n_pn__state._cell_outputs['fbda0317-8c0c-47b1-8247-2cf223d8a6ad'].append("""## Display app""")\ndf = pd.read_parquet('https://datasets.holoviz.org/nyc_taxi_small/v1/nyc_taxi_small.parq')\n\napp = App(data=df)\n\napp.controls.servable(area='sidebar')\napp.deck_gl.servable(title='NYC Taxi Deck.GL Explorer')\n\n_pn__state._cell_outputs['189e7992-6988-49bf-96d5-46d6ddbaa26e'].append((app))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['189e7992-6988-49bf-96d5-46d6ddbaa26e'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['189e7992-6988-49bf-96d5-46d6ddbaa26e'].append(_fig__out)\n\n\nawait write_doc()`)
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