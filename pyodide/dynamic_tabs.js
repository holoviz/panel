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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'altair', 'vega-datasets', 'hvplot', 'matplotlib', 'plotly']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nimport numpy as np\n\nimport pandas as pd\n\nimport panel as pn\n\n\n\npn.extension('deckgl', 'echarts', 'plotly', 'vega', template='material')\n\npn.pane.Markdown('\\nThis example demonstrates **how to efficiently render a number of complex components in \`\`Tabs\`\`** by using the \`dynamic\` parameter.\\n\\n').servable()\n\nimport altair as alt\n\nfrom vega_datasets import data\n\n\n\ncars = data.cars()\n\n\n\nchart = alt.Chart(cars).mark_circle(size=60).encode(\n\n    x='Horsepower',\n\n    y='Miles_per_Gallon',\n\n    color='Origin',\n\n    tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']\n\n).properties(width='container', height='container').interactive()\n\n\n\naltair_pane = pn.pane.Vega(chart)\n\n\n\naltair_pane\n\npn.pane.Markdown('\\n').servable()\n\nfrom math import pi\n\n\n\nfrom bokeh.palettes import Category20c, Category20\n\nfrom bokeh.plotting import figure\n\nfrom bokeh.transform import cumsum\n\n\n\nx = {\n\n    'United States': 157,\n\n    'United Kingdom': 93,\n\n    'Japan': 89,\n\n    'China': 63,\n\n    'Germany': 44,\n\n    'India': 42,\n\n    'Italy': 40,\n\n    'Australia': 35,\n\n    'Brazil': 32,\n\n    'France': 31,\n\n    'Taiwan': 31,\n\n    'Spain': 29\n\n}\n\n\n\ndata = pd.Series(x).reset_index(name='value').rename(columns={'index':'country'})\n\ndata['angle'] = data['value']/data['value'].sum() * 2*pi\n\ndata['color'] = Category20c[len(x)]\n\n\n\np = figure(sizing_mode='stretch_both', title="Pie Chart", toolbar_location=None,\n\n           tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0), min_height=800)\n\n\n\nr = p.wedge(x=0, y=1, radius=0.4,\n\n        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),\n\n        line_color="white", fill_color='color', legend_field='country', source=data)\n\n\n\np.axis.axis_label=None\n\np.axis.visible=False\n\np.grid.grid_line_color = None\n\n\n\nbokeh_pane = pn.pane.Bokeh(p, sizing_mode="stretch_both", max_width=1300)\n\n\n\nbokeh_pane\n\npn.pane.Markdown('\\n').servable()\n\nMAPBOX_KEY = (\n\n    "pk.eyJ1IjoibWFyY3Nrb3ZtYWRzZW4iLCJhIjoiY2s1anMzcG5rMDYzazNvcm10NTFybTE4cSJ9."\n\n    "TV1XBgaMfR-iTLvAXM_Iew"\n\n)\n\n\n\njson_spec = {\n\n    "initialViewState": {\n\n        "bearing": -27.36,\n\n        "latitude": 52.2323,\n\n        "longitude": -1.415,\n\n        "maxZoom": 15,\n\n        "minZoom": 5,\n\n        "pitch": 40.5,\n\n        "zoom": 6\n\n    },\n\n    "layers": [{\n\n        "@@type": "HexagonLayer",\n\n        "autoHighlight": True,\n\n        "coverage": 1,\n\n        "data": "https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv",\n\n        "elevationRange": [0, 3000],\n\n        "elevationScale": 50,\n\n        "extruded": True,\n\n        "getPosition": "@@=[lng, lat]",\n\n        "id": "8a553b25-ef3a-489c-bbe2-e102d18a3211", "pickable": True\n\n    }],\n\n    "mapStyle": "mapbox://styles/mapbox/dark-v9",\n\n    "views": [{"@@type": "MapView", "controller": True}]\n\n}\n\n\n\ndeck_gl = pn.pane.DeckGL(json_spec, mapbox_api_key=MAPBOX_KEY, sizing_mode='stretch_both')\n\n\n\ndeck_gl\n\npn.pane.Markdown('\\n').servable()\n\nechart = {\n\n        'title': {\n\n            'text': 'ECharts entry example'\n\n        },\n\n        'tooltip': {},\n\n        'legend': {\n\n            'data':['Sales']\n\n        },\n\n        'xAxis': {\n\n            'data': ["shirt","cardign","chiffon shirt","pants","heels","socks"]\n\n        },\n\n        'yAxis': {},\n\n        'series': [{\n\n            'name': 'Sales',\n\n            'type': 'bar',\n\n            'data': [5, 20, 36, 10, 10, 20]\n\n        }],\n\n    }\n\n\n\necharts_pane = pn.pane.ECharts(echart, sizing_mode='stretch_both')\n\n\n\necharts_pane\n\npn.pane.Markdown('\\n').servable()\n\nimport holoviews as hv\n\nimport hvplot.pandas\n\nimport holoviews.plotting.bokeh\n\n\n\ndef sine(frequency=1.0, amplitude=1.0, function='sin'):\n\n    xs = np.arange(200)/200*20.0\n\n    ys = amplitude*getattr(np, function)(frequency*xs)\n\n    return pd.DataFrame(dict(y=ys), index=xs).hvplot(responsive=True)\n\n\n\ndmap = hv.DynamicMap(sine, kdims=['frequency', 'amplitude', 'function']).redim.range(\n\n    frequency=(0.1, 10), amplitude=(1, 10)).redim.values(function=['sin', 'cos', 'tan']).opts(responsive=True, line_width=4)\n\n\n\nhv_panel = pn.pane.HoloViews(dmap, widgets={\n\n    'amplitude': pn.widgets.LiteralInput(value=1., type=(float, int)),\n\n    'function': pn.widgets.RadioButtonGroup,\n\n    'frequency': {'value': 5},\n\n}, center=True, sizing_mode='stretch_both').layout\n\n\n\nhv_panel\n\npn.pane.Markdown('\\n').servable()\n\nimport numpy as np\n\nimport matplotlib\n\n\n\nmatplotlib.use('agg')\n\n\n\nimport matplotlib.pyplot as plt\n\n\n\nY, X = np.mgrid[-3:3:100j, -3:3:100j]\n\nU = -1 - X**2 + Y\n\nV = 1 + X - Y**2\n\nspeed = np.sqrt(U*U + V*V)\n\n\n\nfig0, ax0 = plt.subplots()\n\nstrm = ax0.streamplot(X, Y, U, V, color=U, linewidth=2, cmap=plt.cm.autumn)\n\nfig0.colorbar(strm.lines)\n\n\n\nmpl_pane = pn.pane.Matplotlib(fig0, format='svg', sizing_mode='stretch_both')\n\n\n\nmpl_pane\n\npn.pane.Markdown('\\n').servable()\n\nimport plotly.graph_objs as go\n\n\n\nxx = np.linspace(-3.5, 3.5, 100)\n\nyy = np.linspace(-3.5, 3.5, 100)\n\nx, y = np.meshgrid(xx, yy)\n\nz = np.exp(-(x-1)**2-y**2)-(x**3+y**4-x/5)*np.exp(-(x**2+y**2))\n\n\n\nsurface = go.Surface(z=z)\n\nlayout = go.Layout(\n\n    title='Plotly 3D Plot',\n\n    autosize=True,\n\n    margin=dict(t=50, b=50, r=50, l=50)\n\n)\n\nfig = dict(data=[surface], layout=layout)\n\n\n\nplotly_pane = pn.pane.Plotly(fig)\n\n\n\nplotly_pane\n\npn.pane.Markdown('\\n').servable()\n\npn.Tabs(\n\n    ('Altair', altair_pane),\n\n    ('Bokeh', bokeh_pane),\n\n    ('deck.GL', deck_gl),\n\n    ('Echarts', echarts_pane),\n\n    ('HoloViews', hv_panel),\n\n    ('Matplotlib', mpl_pane),\n\n    ('Plotly', plotly_pane),\n\n    dynamic=True, sizing_mode='stretch_both'\n\n).servable()\n\npn.state.template.title = 'Dynamic Tabs'\n\nawait write_doc()`)
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