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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'altair']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport altair as alt\nimport panel as pn\nimport pandas as pd\n\nfrom sklearn.cluster import KMeans\n\n_pn__state._cell_outputs['a99fc380-490f-417f-8c84-dd223295b337'].append((pn.extension('tabulator', 'vega', design='material', template='material')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['a99fc380-490f-417f-8c84-dd223295b337'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['a99fc380-490f-417f-8c84-dd223295b337'].append(_fig__out)\n\n_pn__state._cell_outputs['1d3fef85-1cc7-4f55-bc05-418f05c14a71'].append("""## Load data""")\npenguins = pn.cache(pd.read_csv)('https://datasets.holoviz.org/penguins/v1/penguins.csv').dropna()\ncols = list(penguins.columns)[2:6]\n_pn__state._cell_outputs['4f9fd6ea-1b56-4d5f-85ab-6f3a3cc9f559'].append("""## Define application""")\n@pn.cache\ndef get_clusters(n_clusters):\n    kmeans = KMeans(n_clusters=n_clusters, n_init='auto')\n    est = kmeans.fit(penguins[cols].values)\n    df = penguins.copy()\n    df['labels'] = est.labels_.astype('str')\n    return df\n\n@pn.cache\ndef get_chart(x, y, df):\n    centers = df.groupby('labels')[[x] if x == y else [x, y]].mean()\n    return (\n        alt.Chart(df)\n            .mark_point(size=100)\n            .encode(\n                x=alt.X(x, scale=alt.Scale(zero=False)),\n                y=alt.Y(y, scale=alt.Scale(zero=False)),\n                shape='labels',\n                color='species'\n            ).add_params(brush) +\n        alt.Chart(centers)\n            .mark_point(size=250, shape='cross', color='black')\n            .encode(x=x+':Q', y=y+':Q')\n    ).properties(width='container', height='container')\n\nintro = pn.pane.Markdown("""\nThis app provides an example of **building a simple dashboard using\nPanel**.\\n\\nIt demonstrates how to take the output of **k-means\nclustering on the Penguins dataset** using scikit-learn,\nparameterizing the number of clusters and the variables to\nplot.\\n\\nThe plot and the table are linked, i.e. selecting on the plot\nwill filter the data in the table.\\n\\n The **\`x\` marks the center** of\nthe cluster.\n""", sizing_mode='stretch_width')\n\nx = pn.widgets.Select(name='x', options=cols, value='bill_depth_mm')\ny = pn.widgets.Select(name='y', options=cols, value='bill_length_mm')\nn_clusters = pn.widgets.IntSlider(name='n_clusters', start=1, end=5, value=3)\n\nbrush = alt.selection_interval(name='brush')  # selection of type "interval"\n\nclusters = pn.bind(get_clusters, n_clusters)\n\nchart = pn.pane.Vega(\n    pn.bind(get_chart, x, y, clusters), min_height=400, max_height=800, sizing_mode='stretch_width'\n)\n\ntable = pn.widgets.Tabulator(\n    clusters,\n    pagination='remote', page_size=10, height=600,\n    sizing_mode='stretch_width'\n)\n\ndef vega_filter(filters, df):\n    filtered = df\n    for field, drange in (filters or {}).items():\n        filtered = filtered[filtered[field].between(*drange)]\n    return filtered\n\n_pn__state._cell_outputs['7061fb2e-3c93-4144-a321-bc0e17e4539d'].append((table.add_filter(pn.bind(vega_filter, chart.selection.param.brush))))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['7061fb2e-3c93-4144-a321-bc0e17e4539d'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['7061fb2e-3c93-4144-a321-bc0e17e4539d'].append(_fig__out)\n\n_pn__state._cell_outputs['23d4c182-72e5-4676-bbe0-1b461a9bcbb8'].append("""## Layout app""")\n_pn__state._cell_outputs['cd9eb64f-6a25-4c47-81be-0ffe62bb8620'].append((pn.Row(\n    pn.Column(x, y, n_clusters).servable(area='sidebar'),\n    pn.Column(\n        intro, chart, table,\n    ).servable(title='KMeans Clustering'),\n    sizing_mode='stretch_both',\n    min_height=1000\n)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['cd9eb64f-6a25-4c47-81be-0ffe62bb8620'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['cd9eb64f-6a25-4c47-81be-0ffe62bb8620'].append(_fig__out)\n\n\nawait write_doc()`)
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