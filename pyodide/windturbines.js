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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'hvplot', 'fastparquet']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport holoviews as hv\nimport panel as pn\nimport pandas as pd\n\npn.extension('vizzu', 'tabulator', design='material', template='material')\nimport hvplot.pandas\n_pn__state._cell_outputs['0e88022a-73cb-4f7e-9f2f-e1f055f176ae'].append("""## Load data""")\nwindturbines = pn.state.as_cached(\n    'windturbines',\n    pd.read_parquet,\n    path='https://datasets.holoviz.org/windturbines/v1/windturbines.parq'\n)\n\n_pn__state._cell_outputs['c6a43f64-ea27-41eb-9685-816abbe308ab'].append((windturbines.head()))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['c6a43f64-ea27-41eb-9685-816abbe308ab'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['c6a43f64-ea27-41eb-9685-816abbe308ab'].append(_fig__out)\n\n_pn__state._cell_outputs['70724dc4-fcf0-4411-8943-4dc5dbb8b3c6'].append("""## Plot data""")\ndef data(df, groupby, quant):\n    if quant == 'Count':\n        return df.value_counts(groupby).to_frame(name='Count').sort_index().reset_index().iloc[:50]\n    else:\n        return df.groupby(groupby)[quant].sum().reset_index().iloc[:50]\n\ndef config(chart_type, groupby, quant):\n    if chart_type == 'Bubble Chart':\n        return {\n            "channels": {\n                "x": None,\n                "y": None,\n                "color": groupby,\n                "label": groupby,\n                "size": quant\n            },\n            'geometry': 'circle'\n        }\n    else:\n        return {\n            "channels": {\n                "x": groupby,\n                "y": quant,\n                "color": None,\n                "label": None,\n                "size": None\n            },\n            'geometry': 'rectangle'\n        }\n    \nls = hv.link_selections.instance()\n\ngeo = ls(windturbines.hvplot.points(\n    'easting', 'northing', xaxis=None, yaxis=None, rasterize=True,\n    tiles='CartoLight', responsive=True, dynspread=True,\n    height=500, cnorm='log', cmap='plasma', xlim=(-14000000, -8000000),\n    ylim=(3000000, 6500000)\n))\n    \ngroupby = pn.widgets.RadioButtonGroup(\n    options={'State': 't_state', 'Year': 'p_year', 'Manufacturer': 't_manu'}, align='center'\n)\nchart_type = pn.widgets.RadioButtonGroup(\n    options=['Bar Chart', 'Bubble Chart'], align='center'\n)\nquant = pn.widgets.RadioButtonGroup(\n    options={'Count': 'Count', 'Capacity': 'p_cap'}, align='center'\n)\nlsdata = ls.selection_param(windturbines)\n\nvizzu = pn.pane.Vizzu(\n    pn.bind(data, lsdata, groupby, quant),\n    config=pn.bind(config, chart_type, groupby, quant),\n    column_types={'p_year': 'dimension'},\n    style={\n        "plot": {\n            "xAxis": {\n                "label": {\n                    "angle": "-45deg"\n                }\n            }\n        }\n    },\n    sizing_mode='stretch_both'\n)\n\ndef format_df(df):\n    df = df[['t_state', 't_county', 'p_name', 'p_year', 't_manu', 't_cap']]\n    return df.rename(\n        columns={col: col.split('_')[1].title() for col in df.columns}\n    )\n\n\ntable = pn.widgets.Tabulator(\n    pn.bind(format_df, lsdata), page_size=8, pagination='remote',\n    show_index=False,\n)\n\n_pn__state._cell_outputs['99185c2a-b628-43ce-93ba-4010346b8f5c'].append((pn.Column(\n    pn.Row(quant, "# by", groupby, "# as a", chart_type).servable(area='header'),\n    pn.Column(\n        pn.Row(geo, table),\n        vizzu, min_height=1000,\n        sizing_mode='stretch_both'\n    ).servable(title='Windturbines')\n)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['99185c2a-b628-43ce-93ba-4010346b8f5c'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['99185c2a-b628-43ce-93ba-4010346b8f5c'].append(_fig__out)\n\n\nawait write_doc()`)
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