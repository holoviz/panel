importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.5/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/wheels/bokeh-3.7.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.7.5/dist/wheels/panel-1.7.5-py3-none-any.whl', 'pyodide-http==0.2.1', 'altair']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  \nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport altair as alt\nimport pandas as pd\nimport panel as pn\n\npn.extension('vega', template='fast')\n\npn.state.template.title = "Altair Brushing Example"\n_pn__state._cell_outputs['cc2aa754'].append("""This example demonstrates how to leverage the brushing/linked-selections support in the Vega pane to update a table.""")\ndf = pd.read_json("https://raw.githubusercontent.com/vega/vega/master/docs/data/penguins.json")\n\nbrush = alt.selection_interval(name='brush')  # selection of type "interval"\n\nchart = alt.Chart(df).mark_point().encode(\n    x=alt.X('Beak Length (mm):Q', scale=alt.Scale(zero=False)),\n    y=alt.Y('Beak Depth (mm):Q', scale=alt.Scale(zero=False)),\n    color=alt.condition(brush, 'Species:N', alt.value('lightgray'))\n).properties(\n    width=300,\n    height=300\n).add_params(\n    brush\n)\n\nvega_pane = pn.pane.Vega(chart, debounce=10)\n\ndef filtered_table(selection):\n    if not selection:\n        return df.iloc[:0]\n    query = ' & '.join(\n        f'{crange[0]:.3f} <= \`{col}\` <= {crange[1]:.3f}'\n        for col, crange in selection.items()\n    )\n    return df.query(query)\n\npn.Column(\n    'Select points on the plot and watch the linked table update.',\n    sizing_mode='stretch_width'\n).servable()\n\n_pn__state._cell_outputs['9327af65'].append((pn.Row(\n    vega_pane,\n    pn.Column(\n        pn.pane.DataFrame(\n            pn.bind(filtered_table, vega_pane.selection.param.brush)\n        ),\n        height=350\n    )\n).servable()))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['9327af65'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['9327af65'].append(_fig__out)\n\n\nawait write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
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