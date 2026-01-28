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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'holoviews', 'colorcet', 'hvplot']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport numpy as np\nimport pandas as pd\nimport holoviews as hv\nimport panel as pn\n\nfrom colorcet import bmy\n\npn.extension('tabulator', template='fast')\nimport hvplot.pandas\n_pn__state._cell_outputs['df3cf9ed-a109-410b-9955-0dcb42d06eac'].append("""## Create intro""")\ninstruction = pn.pane.Markdown("""\nThis dashboard visualizes all global glaciers and allows exploring the relationships\nbetween their locations and variables such as their elevation, temperature and annual\nprecipitation.<br><br>Box- or lasso-select on each plot to subselect and hit the \n"Clear selection" button to reset. See the notebook source code for how to build apps\nlike this!""", width=600)\n\npanel_logo = pn.pane.PNG(\n    'https://panel.holoviz.org/_static/logo_stacked.png',\n    link_url='https://panel.holoviz.org', height=95, align='center'\n)\n\noggm_logo = pn.pane.PNG(\n    'https://raw.githubusercontent.com/OGGM/oggm/master/docs/_static/logos/oggm_s_alpha.png',\n    link_url='https://oggm.org/', height=100, align='center'\n)\n\nintro = pn.Row(\n    oggm_logo,\n    instruction,\n    pn.layout.HSpacer(),\n    panel_logo,\n    sizing_mode='stretch_width'\n)\n\n_pn__state._cell_outputs['a2d16e0e-9dd5-4f04-8724-4e25ac07f34f'].append((intro))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['a2d16e0e-9dd5-4f04-8724-4e25ac07f34f'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['a2d16e0e-9dd5-4f04-8724-4e25ac07f34f'].append(_fig__out)\n\n_pn__state._cell_outputs['130476bf-0923-46ec-bb39-f349439127e7'].append("""### Load and cache data""")\nfrom holoviews.element.tiles import lon_lat_to_easting_northing\n\n@pn.cache\ndef load_data():\n    df = pd.read_parquet('https://datasets.holoviz.org/oggm_glaciers/v1/oggm_glaciers.parq')\n    df['latdeg'] = df.cenlat\n    df['x'], df['y'] = lon_lat_to_easting_northing(df.cenlon, df.cenlat)\n    return df\n\ndf = load_data()\n\n_pn__state._cell_outputs['361cec45-e131-44f8-8dad-32706e187ded'].append((df.tail()))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['361cec45-e131-44f8-8dad-32706e187ded'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['361cec45-e131-44f8-8dad-32706e187ded'].append(_fig__out)\n\n_pn__state._cell_outputs['4d9b4125-eef1-4d28-9557-315f8fb42737'].append("""### Set up linked selections""")\nls = hv.link_selections.instance()\n\ndef clear_selections(event):\n    ls.selection_expr = None\n\nclear_button = pn.widgets.Button(name='Clear selection', align='center')\n\nclear_button.param.watch(clear_selections, 'clicks');\n\ntotal_area = df.area_km2.sum()\n\ndef count(data):\n    selected_area  = np.sum(data['area_km2'])\n    selected_percentage = selected_area / total_area * 100\n    return f'## Glaciers selected: {len(data)} | Area: {selected_area:.0f} km\xb2 ({selected_percentage:.1f}%)</font>'\n\n_pn__state._cell_outputs['336c6b94-062c-4409-b67b-327089616d91'].append((pn.Row(\n    pn.pane.Markdown(pn.bind(count, ls.selection_param(df)), align='center', width=600),\n    clear_button\n).servable(area='header', title='OGGM Glaciers')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['336c6b94-062c-4409-b67b-327089616d91'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['336c6b94-062c-4409-b67b-327089616d91'].append(_fig__out)\n\n_pn__state._cell_outputs['4a1834f9-5759-448e-86eb-28f92d99d1c6'].append("""### Create plots""")\ngeo = df.hvplot.points(\n    'x', 'y', rasterize=True, tools=['hover'], tiles='ESRI', cmap=bmy, logz=True, colorbar=True,\n    xaxis=None, yaxis=False, ylim=(-7452837.583633271, 6349198.00989753), min_height=400, responsive=True\n).opts('Tiles', alpha=0.8)\n\nscatter = df.hvplot.scatter(\n    'avg_prcp', 'mean_elev', rasterize=True, fontscale=1.2, grid=True,\n    xlabel='Avg. Precipitation', ylabel='Elevation', responsive=True, min_height=400\n)\n\ntemp = df.hvplot.hist(\n    'avg_temp_at_mean_elev', fontscale=1.2, responsive=True, min_height=350, fill_color='#85c1e9'\n)\n\nprecipitation = df.hvplot.hist(\n    'avg_prcp', fontscale=1.2, responsive=True, min_height=350, fill_color='#f1948a'\n)\n\nplots = pn.pane.HoloViews(ls(geo + scatter + temp + precipitation).cols(2).opts(sizing_mode='stretch_both'))\n_pn__state._cell_outputs['b9b79640-3acf-4722-8038-d192283100a9'].append((plots))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['b9b79640-3acf-4722-8038-d192283100a9'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['b9b79640-3acf-4722-8038-d192283100a9'].append(_fig__out)\n\n_pn__state._cell_outputs['28fc8348-3ef0-4028-ac73-3bcc9e09b46e'].append("""## Dashboard content\n""")\npn.Column(intro, plots, sizing_mode='stretch_both').servable();\n\nawait write_doc()`)
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