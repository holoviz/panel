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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'hvplot', 'scikit-learn', 'bokeh_sampledata']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport numpy as np\nimport pandas as pd\nimport panel as pn\nimport hvplot.pandas\n\nfrom sklearn.cluster import KMeans\nfrom bokeh.sampledata import iris\n\n_pn__state._cell_outputs['3142788f'].append((pn.extension(design='material', template='material')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['3142788f'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['3142788f'].append(_fig__out)\n\n_pn__state._cell_outputs['283f4e69'].append("""This app provides an example of building a simple dashboard using Panel. It demonstrates how to take the output of  k-means clustering on the Iris dataset (performed using scikit-learn), parameterizing the number of clusters and the x and y variables to plot. The entire clustering and plotting pipeline is expressed as a single reactive function that returns a plot that responsively updates when one of the widgets changes.""")\nflowers = iris.flowers.copy()\ncols = list(flowers.columns)[:-1]\n\nx = pn.widgets.Select(name='x', options=cols)\ny = pn.widgets.Select(name='y', options=cols, value='sepal_width')\nn_clusters = pn.widgets.IntSlider(name='n_clusters', start=1, end=5, value=3)\n\ndef get_clusters(x, y, n_clusters):\n    kmeans = KMeans(n_clusters=n_clusters, n_init='auto')\n    est = kmeans.fit(iris.flowers.iloc[:, :-1].values)\n    flowers['labels'] = est.labels_.astype('str')\n    centers = flowers.groupby('labels')[[x] if x == y else [x, y]].mean()\n    return (\n        flowers.sort_values('labels').hvplot.scatter(\n            x, y, c='labels', size=100, height=500, responsive=True\n        ) *\n        centers.hvplot.scatter(\n            x, y, marker='x', c='black', size=400, padding=0.1, line_width=5\n        )\n    )\n\n_pn__state._cell_outputs['43a3b08a'].append((pn.Row(\n    pn.WidgetBox(\n        '# Iris K-Means Clustering',\n        pn.Column(\n            """This app provides an example of **building a simple dashboard using Panel**.\\n\\nIt demonstrates how to take the output of **k-means clustering on the Iris dataset** using scikit-learn, parameterizing the number of clusters and the variables to plot.\\n\\nThe entire clustering and plotting pipeline is expressed as a **single reactive function** that responsively returns an updated plot when one of the widgets changes.\\n\\n The **\`x\` marks the center** of the cluster.""",\n            x, y, n_clusters\n        ).servable(target='sidebar')\n    ),\n    pn.pane.HoloViews(\n        pn.bind(get_clusters, x, y, n_clusters), sizing_mode='stretch_width'\n    ).servable(title='Iris K-Means Clustering')\n)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['43a3b08a'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['43a3b08a'].append(_fig__out)\n\n\nawait write_doc()`)
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