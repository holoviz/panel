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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'altair', 'plotly', 'hvplot', 'matplotlib']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\nimport param\nimport numpy as np \nimport pandas as pd\nimport panel as pn\n\nimport altair as alt\nimport plotly.graph_objs as go\nimport plotly.io as pio\nimport matplotlib.pyplot as plt\n\npn.extension('vega', 'plotly', defer_load=True, template='fast')\nimport hvplot.pandas\n_pn__state._cell_outputs['07748711'].append("""## Configuration\n\nLet us start by configuring some high-level variables and configure the template:""")\nXLABEL = 'GDP per capita (2000 dollars)'\nYLABEL = 'Life expectancy (years)'\nYLIM = (20, 90)\nACCENT = "#00A170"\n\nPERIOD = 1000 # milliseconds\n\n_pn__state._cell_outputs['9e210c23'].append((pn.state.template.param.update(\n    site_url="https://panel.holoviz.org",\n    title="Hans Rosling's Gapminder",\n    header_background=ACCENT,\n    accent_base_color=ACCENT,\n    favicon="static/extensions/panel/images/favicon.ico",\n    theme_toggle=False\n)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['9e210c23'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['9e210c23'].append(_fig__out)\n\n_pn__state._cell_outputs['04c470ed'].append("""## Extract the dataset\n\nFirst, we'll get the data into a Pandas dataframe. We use the [built in \`cache\`](https://panel.holoviz.org/how_to/caching/memoization.html) to speed up the app.""")\n@pn.cache\ndef get_dataset():\n    url = 'https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv'\n    return pd.read_csv(url)\n\ndataset = get_dataset()\n\nYEARS = [int(year) for year in dataset.year.unique()]\n\n_pn__state._cell_outputs['432db0ff'].append((dataset.sample(10)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['432db0ff'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['432db0ff'].append(_fig__out)\n\n_pn__state._cell_outputs['b4458ea6'].append("""## Set up widgets and description\n\nNext we will set up a periodic callback to allow cycling through the years, set up the widgets to control the application and write an introduction:""")\ndef play():\n    if year.value == YEARS[-1]:\n        year.value = YEARS[0]\n        return\n\n    index = YEARS.index(year.value)\n    year.value = YEARS[index+1]    \n\nyear = pn.widgets.DiscreteSlider(\n    value=YEARS[-1], options=YEARS, name="Year", width=280\n)\nshow_legend = pn.widgets.Checkbox(value=True, name="Show Legend")\n\nperiodic_callback = pn.state.add_periodic_callback(play, start=False, period=PERIOD)\nplayer = pn.widgets.Checkbox.from_param(periodic_callback.param.running, name="Autoplay")\n\nwidgets = pn.Column(year, player, show_legend, margin=(0,15))\n\ndesc = """## \U0001f393 Info\n\nThe [Panel](http://panel.holoviz.org) library from [HoloViz](http://holoviz.org)\nlets you make widget-controlled apps and dashboards from a wide variety of \nplotting libraries and data types. Here you can try out four different plotting libraries\ncontrolled by a couple of widgets, for Hans Rosling's \n[gapminder](https://demo.bokeh.org/gapminder) example.\n\nSource: [pyviz-topics - gapminder](https://github.com/pyviz-topics/examples/blob/master/gapminders/gapminders.ipynb)\n"""\n\nsettings = pn.Column(\n    "## \u2699\ufe0f Settings", widgets, desc,\n    sizing_mode='stretch_width'\n).servable(area='sidebar')\n\n_pn__state._cell_outputs['478d25b1'].append((settings))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['478d25b1'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['478d25b1'].append(_fig__out)\n\n_pn__state._cell_outputs['44abdff9'].append("""## Define plotting functions\n\nNow let's define helper functions and functions to plot this dataset with Matplotlib, Plotly, Altair, and hvPlot (using HoloViews and Bokeh).""")\n@pn.cache\ndef get_data(year):\n    df = dataset[(dataset.year==year) & (dataset.gdpPercap < 10000)].copy()\n    df['size'] = np.sqrt(df['pop']*2.666051223553066e-05)\n    df['size_hvplot'] = df['size']*6\n    return df\n\ndef get_title(library, year):\n    return f"{library}: Life expectancy vs. GDP, {year}"\n\ndef get_xlim(data):\n    return (data['gdpPercap'].min()-100,data['gdpPercap'].max()+1000)\n\n@pn.cache\ndef mpl_view(year=1952, show_legend=True):\n    data = get_data(year)\n    title = get_title("Matplotlib", year)\n    xlim = get_xlim(data)\n\n    plot = plt.figure(figsize=(10, 6), facecolor=(0, 0, 0, 0))\n    ax = plot.add_subplot(111)\n    ax.set_xscale("log")\n    ax.set_title(title)\n    ax.set_xlabel(XLABEL)\n    ax.set_ylabel(YLABEL)\n    ax.set_ylim(YLIM)\n    ax.set_xlim(xlim)\n\n    for continent, df in data.groupby('continent'):\n        ax.scatter(df.gdpPercap, y=df.lifeExp, s=df['size']*5,\n                   edgecolor='black', label=continent)\n\n    if show_legend:\n        ax.legend(loc=4)\n\n    plt.close(plot)\n    return plot\n\npio.templates.default = None\n\n@pn.cache\ndef plotly_view(year=1952, show_legend=True):\n    data = get_data(year)\n    title = get_title("Plotly", year)\n    xlim = get_xlim(data)\n\n    traces = []\n    for continent, df in data.groupby('continent'):\n        marker=dict(symbol='circle', sizemode='area', sizeref=0.1, size=df['size'], line=dict(width=2))\n        traces.append(go.Scatter(x=df.gdpPercap, y=df.lifeExp, mode='markers', marker=marker, name=continent, text=df.country))\n\n    axis_opts = dict(gridcolor='rgb(255, 255, 255)', zerolinewidth=1, ticklen=5, gridwidth=2)\n    layout = go.Layout(\n        title=title, showlegend=show_legend,\n        xaxis=dict(title=XLABEL, type='log', **axis_opts),\n        yaxis=dict(title=YLABEL, **axis_opts),\n        autosize=True, paper_bgcolor='rgba(0,0,0,0)',\n    )\n    \n    return go.Figure(data=traces, layout=layout)\n\n@pn.cache\ndef altair_view(year=1952, show_legend=True, height="container", width="container"):\n    data = get_data(year)\n    title = get_title("Altair/ Vega", year)\n    xlim = get_xlim(data)\n    legend= ({} if show_legend else {'legend': None})\n    return (\n        alt.Chart(data)\n            .mark_circle().encode(\n                alt.X('gdpPercap:Q', scale=alt.Scale(type='log'), axis=alt.Axis(title=XLABEL)),\n                alt.Y('lifeExp:Q', scale=alt.Scale(zero=False, domain=YLIM), axis=alt.Axis(title=YLABEL)),\n                size=alt.Size('pop:Q', scale=alt.Scale(type="log"), legend=None),\n                color=alt.Color('continent', scale=alt.Scale(scheme="category10"), **legend),\n                tooltip=['continent','country'])\n            .configure_axis(grid=False)\n            .properties(title=title, height=height, width=width, background='rgba(0,0,0,0)') \n            .configure_view(fill="white")\n            .interactive()\n    )\n\n@pn.cache\ndef hvplot_view(year=1952, show_legend=True):\n    data = get_data(year)\n    title = get_title("hvPlot/ Bokeh", year)\n    xlim = get_xlim(data)\n    return data.hvplot.scatter(\n        'gdpPercap', 'lifeExp', by='continent', s='size_hvplot', alpha=0.8,\n        logx=True, title=title, responsive=True, legend='bottom_right',\n        hover_cols=['country'], ylim=YLIM, xlim=xlim, ylabel=YLABEL, xlabel=XLABEL\n    )\n_pn__state._cell_outputs['539222f6'].append("""## Bind the plot functions to the widgets""")\nmpl_view    = pn.bind(mpl_view,    year=year, show_legend=show_legend)\nplotly_view = pn.bind(plotly_view, year=year, show_legend=show_legend)\naltair_view = pn.bind(altair_view, year=year, show_legend=show_legend)\nhvplot_view = pn.bind(hvplot_view, year=year, show_legend=show_legend)\n\nplots = pn.GridBox(\n    pn.pane.HoloViews(hvplot_view, sizing_mode='stretch_both', margin=10),\n    pn.pane.Plotly(plotly_view, sizing_mode='stretch_both', margin=10),\n    pn.pane.Matplotlib(mpl_view, format='png', sizing_mode='scale_both', tight=True, margin=10),\n    pn.pane.Vega(altair_view, sizing_mode='stretch_both', margin=10),\n    ncols=2,\n    sizing_mode="stretch_both"\n).servable()\n\n_pn__state._cell_outputs['cdf1e00f'].append((plots))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['cdf1e00f'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['cdf1e00f'].append(_fig__out)\n\n\nawait write_doc()`)
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