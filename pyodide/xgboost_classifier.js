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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'pandas', 'scikit-learn', 'xgboost']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport panel as pn\n\nfrom sklearn.datasets import load_iris\nfrom sklearn.metrics import accuracy_score\nfrom xgboost import XGBClassifier\n\n_pn__state._cell_outputs['6bbdabb2'].append((pn.extension(sizing_mode="stretch_width", design='material', template="fast")))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['6bbdabb2'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['6bbdabb2'].append(_fig__out)\n\n_pn__state._cell_outputs['860a31bd'].append("""This example was adapted from an example by [Bojan Tunguz](https://twitter.com/tunguz). It demonstrates how to build a simple ML demo demonstrating how hyper-parameters affect the accuracy of the XGBoostClassifier.""")\npn.state.template.param.update(title="XGBoost Example")\n\niris_df = load_iris(as_frame=True)\n\nn_trees = pn.widgets.IntSlider(start=2, end=30, name="Number of trees")\nmax_depth = pn.widgets.IntSlider(start=1, end=10, value=2, name="Maximum Depth") \nbooster = pn.widgets.Select(options=['gbtree', 'gblinear', 'dart'], name="Booster")\n\ndef pipeline(n_trees, max_depth, booster):\n    model = XGBClassifier(max_depth=max_depth, n_estimators=n_trees, booster=booster)\n    model.fit(iris_df.data, iris_df.target)\n    accuracy = round(accuracy_score(iris_df.target, model.predict(iris_df.data)) * 100, 1)\n    return pn.indicators.Number(\n        name=f"Test score",\n        value=accuracy,\n        format="{value}%",\n        colors=[(97.5, "red"), (99.0, "orange"), (100, "green")],\n        align='center'\n    )\n\n_pn__state._cell_outputs['3dd96529'].append((pn.Row(\n    pn.Column(booster, n_trees, max_depth, width=320).servable(area='sidebar'),\n    pn.Column(\n        "Simple example of training an XGBoost classification model on the small Iris dataset.",\n        iris_df.data.head(),\n        \n        "Adjust the hyperparameters to re-run the XGBoost classifier. The training accuracy score will adjust accordingly:",\n        pn.bind(pipeline, n_trees, max_depth, booster),\n        pn.bind(lambda n_trees, max_depth, booster: f'# <code>{n_trees=}, {max_depth=}, {booster=}</code>', n_trees, max_depth, booster),\n    ).servable(),\n)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['3dd96529'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['3dd96529'].append(_fig__out)\n\n\nawait write_doc()`)
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