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
      await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.8.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.8.7/dist/wheels/panel-1.8.7-py3-none-any.whl', 'pyodide-http', 'pandas', 'plotly']);
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
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(`\nimport asyncio\n\nfrom panel.io.pyodide import init_doc, write_doc\n\ninit_doc()\n\nfrom panel import state as _pn__state\nfrom panel.io.handlers import CELL_DISPLAY as _CELL__DISPLAY, display, get_figure as _get__figure\n\n_pn__state._cell_outputs['60f394d7-82f1-4326-9109-82478dfd9dd9'].append("""The Portfolio Analysis App demonstrates the powerful [Tabulator](../reference/widgets/Tabulator.ipynb) table that ships with Panel.\n\n<img style=\\"max-height:500px\\" src=\\"https://assets.holoviz.org/panel/gifs/portfolio_analyzer.gif\\"></img>\n\nThis app is heavily inspired by the Dash AG Grid App [here](https://github.com/plotly/dash-ag-grid/blob/main/docs/demo_stock_portfolio.py). Having both enables you to compare [pros and cons of Panel w. Tabulator versus Dash w. AG Grid](https://github.com/holoviz/panel/issues/4341).""")\nimport pandas as pd\nimport plotly.express as px\nimport plotly.graph_objects as go\n\nimport panel as pn\n\n_pn__state._cell_outputs['06ac7f7d-4966-446e-8b2b-ef47450e0642'].append((pn.extension('plotly', 'tabulator')))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['06ac7f7d-4966-446e-8b2b-ef47450e0642'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['06ac7f7d-4966-446e-8b2b-ef47450e0642'].append(_fig__out)\n\nACCENT = "#BB2649"\nRED = "#D94467"\nGREEN = "#5AD534"\n\nLINK_SVG = """\n<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up-right-square" viewBox="0 0 16 16">\n  <path fill-rule="evenodd" d="M15 2a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2zM0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm5.854 8.803a.5.5 0 1 1-.708-.707L9.243 6H6.475a.5.5 0 1 1 0-1h3.975a.5.5 0 0 1 .5.5v3.975a.5.5 0 1 1-1 0V6.707l-4.096 4.096z"/>\n</svg>\n"""\n\nCSV_URL = "https://datasets.holoviz.org/equities/v1/equities.csv"\n_pn__state._cell_outputs['3c831a15-da71-4371-9f8a-a04dd464019f'].append("""Lets define our list of equities""")\nEQUITIES = {\n    "AAPL": "Apple",\n    "MSFT": "Microsoft",\n    "AMZN": "Amazon",\n    "GOOGL": "Alphabet",\n    "TSLA": "Tesla",\n    "BRK-B": "Berkshire Hathaway",\n    "UNH": "United Health Group",\n    "JNJ": "Johnson & Johnson",\n}\nEQUITY_LIST = tuple(EQUITIES.keys())\n_pn__state._cell_outputs['22487003-4910-4ae1-95e1-4e871ddd4535'].append("""## Extract the data\n\nWe would be using *caching* (\`pn.cache\`) to improve the performance of the app if we where loading data from a live data source like \`yfinance\`.""")\n@pn.cache(ttl=600)\ndef get_historical_data(tickers=EQUITY_LIST, period="2y"):\n    """Downloads the historical data from Yahoo Finance"""\n    df = pd.read_csv(CSV_URL, index_col=[0, 1], parse_dates=['Date'])\n    return df\n\nhistorical_data = get_historical_data()\n_pn__state._cell_outputs['babaf3df-678d-4aea-8dd6-300201f13bf9'].append((historical_data.head(3).round(2)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['babaf3df-678d-4aea-8dd6-300201f13bf9'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['babaf3df-678d-4aea-8dd6-300201f13bf9'].append(_fig__out)\n\n_pn__state._cell_outputs['a50540fa-5f12-4b84-95b0-13a935f8319c'].append("""## Transform the data\n\nLet us calculate the \`summary_data\` to show in the Table.""")\ndef last_close(ticker, data=historical_data):\n    """Returns the last close pricefor the given ticker"""\n    return data.loc[ticker]["Close"].iloc[-1]\n\n_pn__state._cell_outputs['f3c8cf02-327d-4cbb-abfe-8f9f9d9eac63'].append((last_close("AAPL")))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['f3c8cf02-327d-4cbb-abfe-8f9f9d9eac63'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['f3c8cf02-327d-4cbb-abfe-8f9f9d9eac63'].append(_fig__out)\n\nsummary_data_dict = {\n    "ticker": EQUITY_LIST,\n    "company": EQUITIES.values(),\n    "info": [\n        f"""<a href='https://finance.yahoo.com/quote/{ticker}' target='_blank'>\n        <div title='Open in Yahoo'>{LINK_SVG}</div></a>"""\n        for ticker in EQUITIES\n    ],\n    "quantity": [75, 40, 100, 50, 40, 60, 20, 40],\n    "price": [last_close(ticker) for ticker in EQUITIES],\n    "value": None,\n    "action": ["buy", "sell", "hold", "hold", "hold", "hold", "hold", "hold"],\n    "notes": ["" for i in range(8)],\n}\n\nsummary_data = pd.DataFrame(summary_data_dict)\n\ndef get_value_series(data=summary_data):\n    """Returns the quantity * price series"""\n    return data["quantity"] * data["price"]\n\nsummary_data["value"] = get_value_series()\n_pn__state._cell_outputs['d3f6da46-3f83-48e6-9060-27751300861d'].append((summary_data.head(2)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['d3f6da46-3f83-48e6-9060-27751300861d'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['d3f6da46-3f83-48e6-9060-27751300861d'].append(_fig__out)\n\n_pn__state._cell_outputs['2ddedd48-a25a-4e79-8f7b-720925c47df0'].append("""## Define the *Summary Table*\n\nWe define the configuration of the Tabulator below.""")\ntitles = {\n    "ticker": "Stock Ticker",\n    "company": "Company",\n    "info": "Info",\n    "quantity": "Shares",\n    "price": "Last Close Price",\n    "value": "Market Value",\n    "action": "Action",\n    "notes": "Notes",\n}\nfrozen_columns = ["ticker", "company"]\neditors = {\n    "ticker": None,\n    "company": None,\n    "quantity": {"type": "number", "min": 0, "step": 1},\n    "price": None,\n    "value": None,\n    "action": {\n        "type": "list",\n        "values": {"buy": "buy", "sell": "sell", "hold": "hold"},\n    },\n    "notes": {\n        "type": "textarea",\n        "elementAttributes": {"maxlength": "100"},\n        "selectContents": True,\n        "verticalNavigation": "editor",\n        "shiftEnterSubmit": True,\n    },\n    "info": None,\n}\n\nwidths = {"notes": 400}\nformatters = {\n    "price": {"type": "money", "decimal": ".", "thousand": ",", "precision": 2},\n    "value": {"type": "money", "decimal": ".", "thousand": ",", "precision": 0},\n    "info": {"type": "html", "field": "html"},\n}\n\ntext_align = {\n    "price": "right",\n    "value": "right",\n    "action": "center",\n    "info": "center",\n}\nbase_configuration = {\n    "clipboard": "copy"\n}\n_pn__state._cell_outputs['e8ba0bd7-a8ae-4a71-888a-94f70538a468'].append("""Here we define the \`summary_table\` *widget*.""")\nsummary_table = pn.widgets.Tabulator(\n    summary_data,\n    editors=editors,\n    formatters=formatters,\n    frozen_columns=frozen_columns,\n    layout="fit_data_table",\n    selectable=1,\n    show_index=False,\n    text_align=text_align,\n    titles=titles,\n    widths=widths,\n    configuration=base_configuration,\n)\n_pn__state._cell_outputs['6b4ed809-9844-4628-83da-466afc1f60ce'].append((summary_table))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['6b4ed809-9844-4628-83da-466afc1f60ce'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['6b4ed809-9844-4628-83da-466afc1f60ce'].append(_fig__out)\n\n_pn__state._cell_outputs['cb9cc6ff-04b4-485e-848f-cabd2576c0cb'].append("""Now lets *style* the table using the *Pandas styler* api.""")\ndef style_of_action_cell(value, colors={'buy': GREEN, 'sell': RED}):\n    """Returns the css to apply to an 'action' cell depending on the val"""\n    return f'color: {colors[value]}' if value in colors else ''\n\n_pn__state._cell_outputs['b2a10653-125d-4735-a202-202a8e384b7a'].append((summary_table.style.map(style_of_action_cell, subset=["action"]).set_properties(\n    **{"background-color": "#444"}, subset=["quantity"]\n)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['b2a10653-125d-4735-a202-202a8e384b7a'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['b2a10653-125d-4735-a202-202a8e384b7a'].append(_fig__out)\n\n_pn__state._cell_outputs['4cb5379a-6664-4b84-bf37-7c04d7a555ab'].append("""For later we also need a function to handle when a user edits a cell in the table""")\npatches = pn.widgets.IntInput(description="Used to raise an event when a cell value has changed")\n\ndef handle_cell_edit(event, table=summary_table):\n    """Updates the \`value\` cell when the \`quantity\` cell is updated"""\n    row = event.row\n    column = event.column\n    if column == "quantity":\n        quantity = event.value\n        price = summary_table.value.loc[row, "price"]\n        value = quantity * price\n        table.patch({"value": [(row, value)]})\n\n        patches.value +=1\n_pn__state._cell_outputs['9f3e8f0b-70ef-41ee-9259-2a8f82940c76'].append("""## Define the plots""")\ndef candlestick(selection=[], data=summary_data):\n    """Returns a candlestick plot"""\n    if not selection:\n        ticker = "AAPL"\n        company = "Apple"\n    else:\n        index = selection[0]\n        ticker = data.loc[index, "ticker"]\n        company = data.loc[index, "company"]\n\n    dff_ticker_hist = historical_data.loc[ticker].reset_index()\n    dff_ticker_hist["Date"] = pd.to_datetime(dff_ticker_hist["Date"])\n\n    fig = go.Figure(\n        go.Candlestick(\n            x=dff_ticker_hist["Date"],\n            open=dff_ticker_hist["Open"],\n            high=dff_ticker_hist["High"],\n            low=dff_ticker_hist["Low"],\n            close=dff_ticker_hist["Close"],\n        )\n    )\n    fig.update_layout(\n        title_text=f"{ticker} {company} Daily Price",\n        template="plotly_dark",\n        autosize=True,\n    )\n    return fig\n\n_pn__state._cell_outputs['efe47a55-3e77-4b5f-9b43-4d8ea4e8b4ef'].append((pn.pane.Plotly(candlestick())))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['efe47a55-3e77-4b5f-9b43-4d8ea4e8b4ef'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['efe47a55-3e77-4b5f-9b43-4d8ea4e8b4ef'].append(_fig__out)\n\ndef portfolio_distribution(patches=0):\n    """Returns the distribution of the portfolio"""\n    data = summary_table.value\n    portfolio_total = data["value"].sum()\n\n    fig = px.pie(\n        data,\n        values="value",\n        names="ticker",\n        hole=0.3,\n        title=f"Portfolio Total $ {portfolio_total:,.0f}",\n        template="plotly_dark",\n    )\n    fig.layout.autosize = True\n    return fig\n\n_pn__state._cell_outputs['9b0fd432-f167-43c7-a5ff-b23ccf427080'].append((pn.pane.Plotly(portfolio_distribution())))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['9b0fd432-f167-43c7-a5ff-b23ccf427080'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['9b0fd432-f167-43c7-a5ff-b23ccf427080'].append(_fig__out)\n\n_pn__state._cell_outputs['6e25cad3-c418-4423-8d23-2fc460b4ca10'].append("""## Bind the widgets and functions""")\n_pn__state._cell_outputs['19948be6-f4df-4d88-aa58-8f9038e1cf15'].append("""We want the \`candlestick\` plot to depend on the selection in \`summary_table\`""")\ncandlestick = pn.bind(candlestick, selection=summary_table.param.selection)\n_pn__state._cell_outputs['53747c38-38a2-4f7e-891e-02bf6267e482'].append("""We want the \`portfolio_distribution\` to be updated when ever a cell value changes in the table""")\nsummary_table.on_edit(handle_cell_edit)\n\nportfolio_distribution = pn.bind(portfolio_distribution, patches=patches)\n_pn__state._cell_outputs['5024d93f-f17f-4dc8-b251-493bd9f772d7'].append("""## Test the app""")\n_pn__state._cell_outputs['9b3f2e30-5a5a-4fc3-a925-b357f236415b'].append((pn.Column(\n    pn.Row(\n        pn.pane.Plotly(candlestick), \n        pn.pane.Plotly(portfolio_distribution)\n    ),\n    summary_table,\n    height=600\n)))\nfor _cell__out in _CELL__DISPLAY:\n    _pn__state._cell_outputs['9b3f2e30-5a5a-4fc3-a925-b357f236415b'].append(_cell__out)\n_CELL__DISPLAY.clear()\n_fig__out = _get__figure()\nif _fig__out:\n    _pn__state._cell_outputs['9b3f2e30-5a5a-4fc3-a925-b357f236415b'].append(_fig__out)\n\n_pn__state._cell_outputs['ad8b4f4d-81ff-4f1e-a57a-8f666516d5f5'].append("""## Layout the app in a nice template\n\nWe will use the \`FastGridTemplate\` which provides a nice dashboard layout with Panels you can resize and move around interactively.""")\ntemplate = pn.template.FastGridTemplate(\n    title="Portfolio Analysis",\n    accent_base_color=ACCENT,\n    header_background=ACCENT,\n    prevent_collision=True,\n    save_layout=True,\n    theme_toggle=False,\n    theme='dark',\n    row_height=160\n)\n_pn__state._cell_outputs['fd56569a-14f6-425c-a049-ad7a6b1bd7d1'].append("""Lets add the plots and table to the template""")\ntemplate.main[0:3, 0:8]  = pn.pane.Plotly(candlestick)\ntemplate.main[0:3, 8:12] = pn.pane.Plotly(portfolio_distribution)\ntemplate.main[3:5, :]    = summary_table\n_pn__state._cell_outputs['a7169d20-4fdc-4040-82c4-1171985c711d'].append("""The template does not display in a notebook so we only output it when in a *server* context.""")\nif pn.state.served:\n    template.servable()\n\nawait write_doc()`)
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