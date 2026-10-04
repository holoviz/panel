/**
 * All copy and link targets for the homepage, kept out of the components so wording can
 * be reviewed without reading JSX.
 *
 * Docs links are absolute under /en/docs/latest/ because the homepage is unversioned and
 * lives at the site root, while the Sphinx build is versioned. See
 * plans/docs-homepage-and-versioning.md §1.
 */

import {asset} from './assets'

// The panel-dev staging site has no latest build, so its homepage links into dev.
export const DOCS = import.meta.env.VITE_DOCS_PATH ?? '/en/docs/latest'
export const GITHUB = 'https://github.com/holoviz/panel'

export const nav = [
  {label: 'Docs', href: `${DOCS}/`},
  {label: 'How-to', href: `${DOCS}/how_to/index.html`},
  {label: 'Components', href: `${DOCS}/reference/index.html`},
  {label: 'App Gallery', href: `${DOCS}/gallery/index.html`},
  {label: 'API', href: `${DOCS}/api/index.html`},
]

export const social = [
  {label: 'GitHub', href: GITHUB},
  {label: 'Discord', href: 'https://discord.gg/UXdtYyGVQX'},
  {label: 'Discourse', href: 'https://discourse.holoviz.org/c/panel/5'},
]

export const hero = {
  title: 'Python data apps that keep their shape as they grow.',
  lede:
    'Panel is an open-source Python library for dashboards and data apps. An app starts in a notebook cell and grows into a multi-page application without a rewrite, because state is declarative, nothing reruns top to bottom, and the layout is yours.',
  install: 'pip install panel',
  installConda: 'conda install -c conda-forge panel',
  primary: {label: 'Get started', href: `${DOCS}/getting_started/index.html`},
  secondary: {label: 'See example apps', href: `${DOCS}/gallery/index.html`},
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
  {key: 'bind', text: '    rng = np.random.default_rng(sum(map(ord, ticker)))'},
  {key: 'bind', text: '    walk = np.cumsum(rng.normal(0, sigma, 400))'},
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
  // The changed widget is a model hyperparameter, so exactly the model and what reads its
  // output are downstream of it.
  trigger: 'alpha = 0.1 → 0.5',
  blocks: ['load 4M rows', 'clean and join', 'fit the model', 'draw the forecast', 'draw the data table'],
  traces: [
    {
      id: 'rerun',
      label: 'Script re-executed top to bottom',
      // Indices into `blocks` that run again when alpha changes.
      runs: [0, 1, 2, 3, 4],
      note: 'Every block runs again, including the three that could not have changed. Caching decorators exist to undo this.',
    },
    {
      id: 'panel',
      label: 'Panel',
      runs: [2, 3],
      note: 'The widget is bound to the model, and only the forecast reads the model. The data and the table are left alone.',
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
        'Hand one component a reference to another one\'s state and they stay in step, however deep the tree goes. A large app is many of these, not one callback with a branch per page.',
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

const reference = (section: string, name: string) => `${DOCS}/reference/${section}/${name}.html`

/**
 * Where a pn.ui component is the Material implementation rather than a re-export of the classic
 * one, its reference page lives in panel-material-ui.
 */
const materialReference = (section: string, name: string) =>
  `https://panel-material-ui.holoviz.org/reference/${section}/${name}.html`

/**
 * Eight panes get a picture and the rest a mention: eleven pictures left a ragged last row,
 * and the eight shown are the ones most readers arrive with.
 */
export const panes = {
  title: 'Bring the plotting library you already use',
  lede:
    'Panel renders the objects your library already produces, rather than asking you to port your figures to a chart API of its own. Where the library supports it the pane is two-way, so clicks, selections and ranges come back to Python.',
  items: [
    {name: 'Matplotlib', file: 'Matplotlib', note: 'Any Figure, including Seaborn and Plotnine'},
    {name: 'Plotly', file: 'Plotly', note: 'Click, hover and selection events'},
    {name: 'Bokeh', file: 'Bokeh', note: 'Figures and models, unwrapped'},
    {name: 'hvPlot and HoloViews', file: 'HoloViews', note: 'Widgets generated for you'},
    {name: 'Altair and Vega', file: 'Vega', note: 'Selections come back to Python'},
    {name: 'ECharts', file: 'ECharts', note: 'Option dicts and pyecharts objects'},
    {name: 'Deck.gl', file: 'DeckGL', note: 'Large geographic scenes on the GPU'},
    {name: 'Vizzu', file: 'Vizzu', note: 'Animated transitions between charts'},
  ].map((p) => ({
    ...p,
    api: `pn.ui.${p.file}`,
    image: asset(`panes/${p.file}.webp`),
    href: reference('panes', p.file),
  })),
  more: [
    {name: 'VTK', href: reference('panes', 'VTK')},
    {name: 'ipywidgets', href: reference('panes', 'IPyWidget')},
    {name: 'Folium', href: reference('panes', 'Folium')},
  ],
}

/**
 * A dozen components, chosen because each one is a thing people otherwise stop and build.
 *
 * The count is examples/reference/{widgets,panes,layouts,indicators,chat}, which stood at
 * 134 on 2026-09-05. Rounded down in the copy so it stays true as things are added.
 */
export const components = {
  title: 'The component you were about to build is already here',
  lede:
    'More than 130 components ship with Panel, each documented on its own page with the code that produced it. These are the ones people are surprised to find.',
  items: [
    {name: 'Tabulator', section: 'widgets', note: 'Sort, filter and edit large tables'},
    {name: 'ChatInterface', section: 'chat', note: 'Streaming tokens and nested steps', material: true},
    {name: 'Terminal', section: 'widgets', note: 'Stream stdout, or take input'},
    {name: 'JSONEditor', section: 'widgets', note: 'Nested config, validated as you type'},
    {name: 'Trend', section: 'indicators', note: 'A number and its sparkline'},
    {name: 'Gauge', section: 'indicators', note: 'One bounded value, at a glance'},
    {name: 'Swipe', section: 'layouts', note: 'Two views, split by a slider'},
    {name: 'TextEditor', section: 'widgets', note: 'Rich text in, HTML out'},
    {name: 'Perspective', section: 'panes', note: 'Pivot, filter and chart a dataframe'},
    {name: 'CrossSelector', section: 'widgets', note: 'Move items between two lists', material: true},
    {name: 'NestedSelect', section: 'widgets', note: 'Dependent dropdowns from a dict', material: true},
    {name: 'Player', section: 'widgets', note: 'Step or animate through a range', material: true},
  ].map((c) => ({
    ...c,
    image: asset(`components/${c.name}.webp`),
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
      'panel convert compiles an app to WebAssembly and runs it in the browser through Pyodide, which is how the example apps in these docs run without a server.',
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
 * Full-window screenshots of the served gallery apps, taken by scripts/thumbnails.py. Links
 * go to the docs gallery pages rather than the panel-gallery deployment, which does not serve
 * the newest apps yet. The first entry is the featured tile.
 */
const galleryPage = (name: string) => `${DOCS}/gallery/${name}.html`

export const gallery = [
  {
    name: 'gaia_million_star_atlas',
    title: 'Gaia million star atlas',
    note: 'A million Gaia DR3 measurements, brushed across the sky map and the color–magnitude diagram at once.',
  },
  {name: 'model_serving_monitor', title: 'Model serving monitor', note: 'Live latency, drift and alerts'},
  {name: 'portfolio_analyzer', title: 'Portfolio analyzer', note: 'Tabulator linked to price charts'},
  {name: 'glaciers', title: 'Glaciers of the world', note: '200,000 glaciers, crossfiltered'},
  {name: 'penguin_crossfilter', title: 'Penguin crossfilter', note: 'One selection across four plots'},
  {name: 'storm_surge_studio', title: 'Storm surge studio', note: 'A flood model you can steer'},
].map((g) => ({...g, image: asset(`gallery/${g.name}.webp`), href: galleryPage(g.name)}))

export const adoption = {
  title: 'Developed in the open since 2018',
  body:
    'Panel is maintained by a team at Anaconda together with contributors from research labs, banks, and instrument makers. Ask questions on Discourse or Discord, and report bugs on GitHub.',
  // Checked against the GitHub API on 2026-10-03. Worth refreshing whenever this page is
  // touched; nothing here reads it live.
  stats: [
    {value: '5.8k', label: 'GitHub stars'},
    {value: '2018', label: 'First release'},
    {value: '220+', label: 'Contributors'},
    {value: 'BSD-3', label: 'License'},
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
