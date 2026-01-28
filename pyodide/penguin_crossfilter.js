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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'hvplot']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport numpy as np\nimport pandas as pd\nimport panel as pn\n\nimport holoviews as hv\nimport hvplot.pandas # noqa\n\npn.extension(template='fast')\n\npn.state.template.logo = 'https://github.com/allisonhorst/palmerpenguins/raw/main/man/figures/logo.png'\n_pn__state._cell_outputs['9dec41f5'].append("""## Introduction""")\nwelcome = "## Welcome and meet the Palmer penguins!"\n\npenguins_art = pn.pane.PNG('https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/man/figures/palmerpenguins.png', height=160)\n\ncredit = "### Artwork by @allison_horst"\n\ninstructions = """\nUse the box-select and lasso-select tools to select a subset of penguins\nand reveal more information about the selected subgroup through the power\nof cross-filtering.\n"""\n\nlicense = """\n### License\n\nData are available by CC-0 license in accordance with the Palmer Station LTER Data Policy and the LTER Data Access Policy for Type I data."\n"""\n\nart = pn.Column(\n    welcome, penguins_art, credit, instructions, license,\n    sizing_mode='stretch_width'\n).servable(area='sidebar')\n\n_pn__state._cell_outputs['dac88965'].append((art))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['dac88965'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['dac88965'].append(_fig__out)\n\n_pn__state._cell_outputs['bf538442'].append("""## Building some plots\n\nLet us first load the Palmer penguin dataset ([Gorman et al.](https://allisonhorst.github.io/palmerpenguins/)) which contains measurements about a number of penguin species:""")\npenguins = pd.read_csv('https://datasets.holoviz.org/penguins/v1/penguins.csv')\npenguins = penguins[~penguins.sex.isnull()].reset_index().sort_values('species')\n\n_pn__state._cell_outputs['5cafa999'].append((penguins.head()))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['5cafa999'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['5cafa999'].append(_fig__out)\n\n_pn__state._cell_outputs['df455cd4'].append("""Next we will set up a linked selections instance that will allow us to perform cross-filtering on the plots we will create in the next step:""")\nls = hv.link_selections.instance()\n\ndef count(selected):\n    return f"## {len(selected)}/{len(penguins)} penguins selected"\n\nselected = pn.pane.Markdown(\n    pn.bind(count, ls.selection_param(penguins)),\n    align='center', width=400, margin=(0, 100, 0, 0)\n)\n\nheader = pn.Row(\n    pn.layout.HSpacer(), selected,\n    sizing_mode='stretch_width'\n).servable(area='header')\n\n_pn__state._cell_outputs['7a1e8387'].append((selected))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['7a1e8387'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['7a1e8387'].append(_fig__out)\n\n_pn__state._cell_outputs['69638fe1'].append("""Now we can start plotting the data with hvPlot, which provides a familiar API to pandas \`.plot\` users but generates interactive plots and use the linked selections object to allow cross-filtering across the plots:""")\ncolors = {\n    'Adelie': '#1f77b4',\n    'Gentoo': '#ff7f0e',\n    'Chinstrap': '#2ca02c'\n}\n\nscatter = penguins.hvplot.points(\n    'bill_length_mm', 'bill_depth_mm', c='species',\n    cmap=colors, responsive=True, min_height=300\n)\n\nhistogram = penguins.hvplot.hist(\n    'body_mass_g', by='species', color=hv.dim('species').categorize(colors),\n    legend=False, alpha=0.5, responsive=True, min_height=300\n)\n\nbars = penguins.hvplot.bar(\n    'species', 'index', c='species', cmap=colors,\n    responsive=True, min_height=300, ylabel=''\n).aggregate(function=np.count_nonzero)\n\nviolin = penguins.hvplot.violin(\n    'flipper_length_mm', by=['species', 'sex'], cmap='Category20',\n    responsive=True, min_height=300, legend='bottom_right'\n).opts(split='sex')\n\nplots = pn.pane.HoloViews(\n    ls(scatter.opts(show_legend=False) + bars + histogram + violin).opts(sizing_mode='stretch_both').cols(2)\n).servable(title='Palmer Penguins')\n\n_pn__state._cell_outputs['d8b0f8aa'].append((plots))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['d8b0f8aa'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['d8b0f8aa'].append(_fig__out)\n\n\nawait write_doc()`)
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