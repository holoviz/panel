/**
 * All copy and link targets for the homepage, kept out of the components so wording can
 * be reviewed without reading JSX.
 *
 * Docs links are absolute under /en/docs/latest/ because the homepage is unversioned and
 * lives at the site root, while the Sphinx build is versioned. See
 * plans/docs-homepage-and-versioning.md §1.
 */

export const DOCS = '/en/docs/latest'
export const GITHUB = 'https://github.com/holoviz/panel'

export const nav = [
  {label: 'Docs', href: `${DOCS}/`},
  {label: 'Components', href: `${DOCS}/reference/index.html`},
  {label: 'How-to', href: `${DOCS}/how_to/index.html`},
  {label: 'Examples', href: `${DOCS}/gallery/index.html`},
  {label: 'API', href: `${DOCS}/api/index.html`},
]

export const social = [
  {label: 'GitHub', href: GITHUB},
  {label: 'Discord', href: 'https://discord.gg/UXdtYyGVQX'},
  {label: 'Discourse', href: 'https://discourse.holoviz.org/c/panel/5'},
]

export const hero = {
  title: 'Data apps that keep their shape as they grow.',
  lede:
    'Panel starts in a notebook cell and does not make you rewrite when the app reaches twelve screens. State is declarative, nothing reruns top to bottom, and the layout is yours.',
  install: 'pip install panel',
  installConda: 'conda install -c conda-forge panel',
  primary: {label: 'Get started', href: `${DOCS}/getting_started/index.html`},
  secondary: {label: 'Run an example in your browser', href: `${DOCS}/gallery/index.html`},
}

/**
 * The hero's app and the hero's code are two views of one thing, so the regions and the
 * lines are keyed to each other by these ids rather than by position.
 */
export type HeroKey = 'widgets' | 'bind' | 'layout'

export const heroCode: {key: HeroKey | null; text: string}[] = [
  {key: null, text: 'import numpy as np, panel as pn'},
  {key: null, text: 'import holoviews as hv'},
  {key: null, text: ''},
  {key: null, text: 'pn.extension()'},
  {key: null, text: ''},
  {key: 'widgets', text: 'window = pn.ui.IntSlider(name="Window", value=30, start=5, end=90)'},
  {key: 'widgets', text: 'sigma  = pn.ui.FloatSlider(name="Volatility", value=1.0, start=0.2, end=3)'},
  {key: 'widgets', text: 'ticker = pn.ui.RadioButtonGroup(name="Series", options=["AAPL", "MSFT", "NVDA"])'},
  {key: null, text: ''},
  {key: 'bind', text: 'def series(window, sigma, ticker):'},
  {key: 'bind', text: '    walk = np.cumsum(rng(ticker).normal(0, sigma, 400))'},
  {key: 'bind', text: '    smooth = np.convolve(walk, np.ones(window) / window, "same")'},
  {key: 'bind', text: '    return hv.Curve(walk).opts(alpha=0.4) * hv.Curve(smooth)'},
  {key: null, text: ''},
  {key: 'layout', text: 'plot = pn.bind(series, window, sigma, ticker)'},
  {key: 'layout', text: 'pn.ui.Row(pn.ui.Column(window, sigma, ticker), plot).servable()'},
]

export const heroRegions: Record<HeroKey, string> = {
  widgets: 'Three widgets, declared once.',
  bind: 'A plain function of their values.',
  layout: 'Bound, laid out, and servable.',
}

/**
 * "Three ways in" is a genuine progression (explore, then script, then serve), so it gets
 * a sequential treatment. Nothing else on the page does.
 */
export const paths = [
  {
    step: 'In the notebook',
    title: 'See it in the cell you wrote it in',
    body:
      'Any Panel object renders in Jupyter, JupyterLab, VS Code, Colab and marimo. Widgets stay live, so you keep exploring in the same place you built the app.',
    code: 'pn.ui.Row(controls, plot)',
  },
  {
    step: 'As a script',
    title: 'Mark what should be served',
    body:
      'Add .servable() and run panel serve. The same file works as a notebook, a script, or a module, and hot reload picks up your edits as you save.',
    code: 'panel serve app.py --dev',
  },
  {
    step: 'In production',
    title: 'Put it behind your own stack',
    body:
      'Serve it standalone, mount it inside FastAPI or Django, scale it across processes, add OAuth, or compile it to WebAssembly and skip the server entirely.',
    code: 'panel convert app.py',
  },
]

/**
 * The rerun contrast, as two execution traces of the same five-block app.
 *
 * Deliberately unnamed: the top-to-bottom model belongs to more than one framework, and
 * naming one would date the page and pick a fight instead of making the point.
 */
export const execution = {
  title: 'A slider move should not re-run your app',
  lede:
    'Most Python app frameworks answer a widget change by executing your script again from the first line. It works until the script does something expensive, and from then on you are managing caches instead of writing the app.',
  blocks: ['load 4M rows', 'clean and join', 'fit the model', 'draw the chart', 'draw the table'],
  traces: [
    {
      id: 'rerun',
      label: 'Script re-executed top to bottom',
      // Indices into `blocks` that run again when the model's one parameter changes.
      runs: [0, 1, 2, 3, 4],
      note: 'Every block runs again, including the four that could not have changed. Caching decorators exist to undo this.',
    },
    {
      id: 'panel',
      label: 'Panel',
      runs: [2, 3],
      note: 'The widget is bound to the model, and the chart depends on the model. Nothing else is asked to do anything.',
    },
  ],
  link: {
    label: 'How Panel compares, framework by framework',
    href: `${DOCS}/explanation/comparisons/compare_streamlit.html`,
  },
}

/**
 * The same app at three sizes. Not numbered: this is not a sequence you walk through once,
 * it is where you end up depending on how far the thing goes.
 */
export const growth = {
  title: 'The code grows, the model does not change',
  lede:
    'A bound function, a component with typed state, and a component made of components are the same idea at three sizes. Moving between them is refactoring, not rewriting, because each one is a Python object that renders.',
  stages: [
    {
      title: 'A function of its inputs',
      body:
        'pn.bind takes a plain function and the widgets that feed it. There is nothing to learn and nothing to register.',
      code: ['plot = pn.bind(view, df, window=window)', '', 'pn.ui.Column(window, plot).servable()'].join('\n'),
    },
    {
      title: 'A component with typed state',
      body:
        'Param gives the same app declared state with bounds and validation, and methods that say what they depend on. You can instantiate it twice, or test it with no browser in sight.',
      code: [
        'class Explorer(pn.viewable.Viewer):',
        '    data = param.DataFrame(allow_refs=True)',
        '    window = param.Integer(30, bounds=(5, 90))',
        '',
        '    @param.depends("data", "window")',
        '    def plot(self):',
        '        return view(self.data, self.window)',
      ].join('\n'),
    },
    {
      title: 'Components made of components',
      body:
        'Hand one component a reference to another one\'s state and they stay in step, however deep the tree goes. Twelve screens is twelve of these, not twelve branches in one callback.',
      code: [
        'class Dashboard(pn.viewable.Viewer):',
        '    data = param.DataFrame()',
        '',
        '    def __panel__(self):',
        '        ref = self.param.data',
        '        return pn.ui.Tabs(',
        '            ("Explore", Explorer(data=ref)),',
        '            ("Report", Report(data=ref)),',
        '        )',
      ].join('\n'),
    },
  ],
  link: {
    label: 'Functions or classes, and when to switch',
    href: `${DOCS}/explanation/api/functions_vs_classes.html`,
  },
}

/**
 * Reference thumbnails come from assets.holoviz.org, which is where nbsite_gallery_conf
 * already points them, and the path segment doubles as the docs reference section.
 */
const thumb = (section: string, name: string) =>
  `https://assets.holoviz.org/panel/thumbnails/reference/${section}/${name}.png`
const reference = (section: string, name: string) => `${DOCS}/reference/${section}/${name}.html`

/**
 * Where a pn.ui component is the Material implementation rather than a re-export of the classic
 * one, its picture and its page have to come from panel-material-ui, which is where that
 * implementation and its reference page currently live. Otherwise a tile would show a widget
 * that does not look like the one the snippets on this page produce.
 */
const materialThumb = (section: string, name: string) =>
  `https://assets.holoviz.org/panel-material-ui/thumbnails/reference/${section}/${name}.png`
const materialReference = (section: string, name: string) =>
  `https://panel-material-ui.holoviz.org/reference/${section}/${name}.html`

/**
 * Plotnine and Seaborn are absent as entries because they draw through Matplotlib and share
 * its pane rather than having one of their own.
 */
export const panes = {
  title: 'Bring the plotting library you already use',
  lede:
    'Panel renders the objects your library already produces, rather than asking you to port your figures to a chart API of its own. Where the library supports it the pane is two-way, so clicks, selections and ranges come back to Python.',
  items: [
    {name: 'Matplotlib', file: 'Matplotlib', note: 'Any Figure, including what Plotnine and Seaborn draw.'},
    {name: 'Plotly', file: 'Plotly', note: 'Click, hover, selection and relayout events come back.'},
    {name: 'Bokeh', file: 'Bokeh', note: 'Bokeh figures and models, with no wrapper in between.'},
    {name: 'HoloViews', file: 'HoloViews', note: 'hvPlot and HoloViews objects, with their widgets generated for you.'},
    {name: 'Altair and Vega', file: 'Vega', note: 'Altair charts and raw Vega-Lite specs, selections included.'},
    {name: 'ECharts', file: 'ECharts', note: 'ECharts option dictionaries and pyecharts objects.'},
    {name: 'Deck.gl', file: 'DeckGL', note: 'Large geographic scenes, drawn on the GPU.'},
    {name: 'VTK', file: 'VTK', note: 'Volumes and meshes, rotatable in the browser.'},
    {name: 'Perspective', file: 'Perspective', note: 'Pivot, filter and chart a dataframe in place.'},
    {name: 'Vizzu', file: 'Vizzu', note: 'Animated transitions between chart types.'},
    {name: 'ipywidgets', file: 'IPyWidget', note: 'Any ipywidget, so ipyleaflet and pydeck come along too.'},
  ].map((p) => ({
    ...p,
    // pn.ui re-exports the panes unchanged rather than reimplementing them, so the reference
    // page under panes/ documents the same class this names.
    api: `pn.ui.${p.file}`,
    image: thumb('panes', p.file),
    href: reference('panes', p.file),
  })),
}

/**
 * A dozen of the components from the reference gallery, chosen because they read at
 * thumbnail size and because each one is a thing people otherwise stop and build.
 *
 * The count is examples/reference/{widgets,panes,layouts,indicators,chat}, which stood at
 * 134 on 2026-09-05. Rounded down in the copy so it stays true as things are added.
 */
export const components = {
  title: 'The component you were about to build is already here',
  lede:
    'More than 130 components ship in pn.ui, Panel\'s Material UI component namespace, each documented on its own page with the code that produced it. These are the ones people are surprised to find.',
  items: [
    {name: 'Tabulator', section: 'widgets', note: 'Millions of rows, edited in place'},
    {name: 'ChatInterface', section: 'chat', note: 'Streaming tokens and nested steps', material: true},
    {name: 'Terminal', section: 'widgets', note: 'Stream stdout, or take input'},
    {name: 'JSONEditor', section: 'widgets', note: 'Nested config, validated as you type'},
    {name: 'Trend', section: 'indicators', note: 'A number and its sparkline'},
    {name: 'Gauge', section: 'indicators', note: 'One bounded value, at a glance'},
    {name: 'Swipe', section: 'layouts', note: 'Two views, split by a slider'},
    {name: 'TextEditor', section: 'widgets', note: 'Rich text in, HTML out'},
    {name: 'FileDropper', section: 'widgets', note: 'Chunked uploads with progress'},
    {name: 'CrossSelector', section: 'widgets', note: 'Move items between two lists', material: true},
    {name: 'NestedSelect', section: 'widgets', note: 'Dependent dropdowns from a dict', material: true},
    {name: 'Player', section: 'widgets', note: 'Step or animate through a range'},
  ].map((c) => ({
    ...c,
    image: (c.material ? materialThumb : thumb)(c.section, c.name),
    href: (c.material ? materialReference : reference)(c.section, c.name),
  })),
  link: {label: 'Browse all components', href: `${DOCS}/reference/index.html`},
}

export const capabilities = [
  {
    title: 'Streaming and async, without a rewrite',
    body:
      'Async callbacks, periodic callbacks, generators and WebSocket streaming are first-class. A function can yield partial results and the page updates as they arrive.',
    href: `${DOCS}/how_to/callbacks/index.html`,
  },
  {
    title: 'Your own components, in the language you like',
    body:
      'Write a component in React, Vue or plain JavaScript against an ESM entry point, declare its dependencies in an import map, and use it from Python like any other widget.',
    href: `${DOCS}/how_to/custom_components/index.html`,
  },
  {
    title: 'Runs with no server at all',
    body:
      'panel convert compiles an app to WebAssembly and runs it in the browser through Pyodide, which is how every example in these docs is editable in place.',
    href: `${DOCS}/how_to/wasm/index.html`,
  },
  {
    title: 'Authentication, caching, profiling',
    body:
      'OAuth against the usual providers, a caching decorator with disk and memory backends, per-session state, and a built-in admin panel that profiles what is slow.',
    href: `${DOCS}/how_to/authentication/index.html`,
  },
]

/**
 * Screenshots come from assets.holoviz.org, which is where nbsite_gallery_conf already
 * points, and they are all square thumbnails. Links go to the docs gallery pages rather
 * than the panel-gallery deployment, which is currently returning 404 for every path.
 */
const shot = (name: string) => `https://assets.holoviz.org/panel/gallery/${name}.png`
const galleryPage = (name: string) => `${DOCS}/gallery/${name}.html`

export const gallery = [
  {name: 'portfolio_analyzer', title: 'Portfolio analyzer', note: 'Tabulator and streaming quotes'},
  {name: 'penguin_crossfilter', title: 'Penguin crossfilter', note: 'Linked selections across four plots'},
  {name: 'windturbines', title: 'Wind turbines', note: '60k points, rendered server side'},
  {name: 'vtk_slicer', title: 'Volume slicer', note: 'VTK, in the browser'},
  {name: 'hvplot_explorer', title: 'hvPlot explorer', note: 'A UI generated from a dataframe'},
  {name: 'deckgl_game_of_life', title: 'Game of life', note: 'Deck.gl on a periodic callback'},
  {name: 'xgboost_classifier', title: 'XGBoost classifier', note: 'Retrains on every widget change'},
  {name: 'glaciers', title: 'Glaciers', note: 'Geographic crossfiltering'},
].map((g) => ({...g, image: shot(g.name), href: galleryPage(g.name)}))

export const adoption = {
  title: 'Panel is used where the analysis matters more than the framework',
  body:
    'It is part of HoloViz, has been developed in the open since 2018, and is maintained by a team at Anaconda together with contributors from research labs, banks, and instrument makers. Questions get answered on Discourse and Discord, usually the same day.',
  // Checked against the GitHub API on 2026-09-05. Worth refreshing whenever this page is
  // touched; nothing here reads it live.
  stats: [
    {value: '5.8k', label: 'GitHub stars'},
    {value: '2018', label: 'First release'},
    {value: '220+', label: 'Contributors'},
    {value: 'BSD-3', label: 'Licence'},
  ],
}

export const footerColumns = [
  {
    heading: 'Learn',
    links: [
      {label: 'Getting started', href: `${DOCS}/getting_started/index.html`},
      {label: 'Tutorials', href: `${DOCS}/tutorials/index.html`},
      {label: 'How-to guides', href: `${DOCS}/how_to/index.html`},
      {label: 'Explanation', href: `${DOCS}/explanation/index.html`},
    ],
  },
  {
    heading: 'Reference',
    links: [
      {label: 'Component gallery', href: `${DOCS}/reference/index.html`},
      {label: 'API reference', href: `${DOCS}/api/index.html`},
      {label: 'Example apps', href: `${DOCS}/gallery/index.html`},
      {label: 'Release notes', href: `${DOCS}/about/releases.html`},
    ],
  },
  {
    heading: 'Community',
    links: [
      {label: 'Discourse', href: 'https://discourse.holoviz.org/c/panel/5'},
      {label: 'Discord', href: 'https://discord.gg/UXdtYyGVQX'},
      {label: 'GitHub issues', href: `${GITHUB}/issues`},
      {label: 'Contributing', href: `${GITHUB}/blob/main/CONTRIBUTING.MD`},
    ],
  },
  {
    heading: 'HoloViz',
    links: [
      {label: 'hvPlot', href: 'https://hvplot.holoviz.org'},
      {label: 'HoloViews', href: 'https://holoviews.org'},
      {label: 'Param', href: 'https://param.holoviz.org'},
      {label: 'Panel Material UI', href: 'https://panel-material-ui.holoviz.org'},
    ],
  },
]
