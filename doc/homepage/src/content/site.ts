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
  title: 'Build data apps with the Python tools you know.',
  lede:
    'Panel is an open-source library for interactive dashboards and web apps. Widgets, plots and layouts are ordinary Python objects that you connect to your data and models, pass between functions and classes, and test like the rest of your code. There are no string IDs to match up and no script that reruns on every click.',
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
  widgets: 'Create the controls.',
  bind: 'Define the plot.',
  layout: 'Connect the controls and arrange the app.',
}

/**
 * "Three ways in" is a genuine progression (explore, then script, then serve), so it gets
 * a sequential treatment. Nothing else on the page does.
 */
export const paths = [
  {
    title: 'In a notebook',
    body: 'Explore data with live widgets and plots in Jupyter, JupyterLab, VS Code, Colab or marimo.',
    code: 'pn.ui.Row(controls, plot)',
  },
  {
    title: 'From your editor',
    body:
      'Build your app in a Python file, mark the layout with `.servable()` and run `panel serve`. Development mode reloads the app as you edit.',
    code: 'panel serve app.py --dev',
  },
  {
    title: 'In production',
    body:
      'Host your app on your own infrastructure, add authentication, or integrate it with FastAPI or Django. Compatible apps can also run entirely in the browser with WebAssembly.',
    code: 'panel convert app.py',
    codeLabel: 'Browser deployment',
  },
]

/**
 * The rerun contrast, as two execution traces of the same five-block app.
 *
 * Deliberately unnamed: the top-to-bottom model belongs to more than one framework, and
 * naming one would date the page and pick a fight instead of making the point.
 */
export const execution = {
  title: 'Update only what needs to change',
  lede:
    'When a user changes a control, Panel runs only the code connected to it. In a small app, rerunning everything is cheap and the difference is hard to notice. In a real application that loads large datasets, fits models and keeps user state, it determines how quickly the app responds and how much caching and state management you have to write to keep it that way.',
  // The changed widget is a model hyperparameter, so exactly the model and what reads its
  // output are downstream of it.
  trigger: 'alpha = 0.1 → 0.5',
  blocks: ['load 4M rows', 'clean and join', 'fit the model', 'draw the forecast', 'draw the data table'],
  traces: [
    {
      id: 'rerun',
      label: 'Full-script execution',
      // Indices into `blocks` that run again when alpha changes.
      runs: [0, 1, 2, 3, 4],
      note: 'In this example, a full script rerun repeats all five steps unless caching or other controls are added.',
    },
    {
      id: 'panel',
      label: 'Panel',
      runs: [2, 3],
      note: 'Only the model and forecast update. The dataset and table stay in place.',
    },
  ],
  link: {
    label: 'Compare Panel and Streamlit',
    href: `${DOCS}/explanation/comparisons/compare_streamlit.html`,
  },
}

/**
 * The same app at three sizes. Not numbered: this is not a sequence you walk through once,
 * it is where you end up depending on how far the thing goes.
 */
export const growth = {
  title: 'Organize your app as it grows',
  lede:
    'Connect widgets to functions for a simple app, or use reusable components to organize a larger one. Both approaches work together.',
  stages: [
    {
      title: 'Connect a function',
      body: 'Use `pn.bind` to connect a Python function to widgets. Panel updates the result when their values change.',
      code: ['plot = pn.bind(view, df, window=window)', '', 'pn.ui.Column(window, plot).servable()'].join('\n'),
    },
    {
      title: 'Create a reusable component',
      body:
        'Group data, settings and behavior in a component. Param lets you define valid values and how changes affect the app, making components easier to reuse and test.',
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
      title: 'Combine components',
      body: 'Build pages from smaller components that share data and stay in sync.',
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
  ceiling:
    'Built this way, Panel apps run in production as multi-page internal platforms with authentication, editable tables, review workflows and chat assistants used by whole teams. Lumen, a complete AI data exploration application, is built entirely with Panel. Because Panel keeps a live Python session for every visitor, it suits apps built around data, models and computation. A consumer product such as a public message board or a full word processor is better served by a general-purpose web framework, which can still embed Panel apps through FastAPI or Django.',
  link: {
    label: 'Choosing between functions and classes',
    href: `${DOCS}/explanation/api/functions_vs_classes.html`,
  },
}

/**
 * AI on both sides of an app: the agent writing it and the person using it. The copilot
 * picture is a real LLM turn against Lumen's demo, taken by scripts/thumbnails.py copilot.
 */
export const ai = {
  title: 'AI tools for developers and users',
  lede:
    'Use HoloViz skills to help coding assistants work with Panel, and Lumen to add an assistant to your app.',
  items: [
    {
      id: 'skills',
      title: 'Build with coding assistants',
      body:
        'HoloViz skills give coding assistants guidance on building, reviewing, debugging and testing Panel apps with current APIs. Install them for Claude Code, Codex, Copilot, Cursor, Gemini CLI and other supported tools.',
      code: ['pip install holoviz-skills', 'holoviz-skills install'].join('\n'),
      link: {label: 'Browse the skills', href: 'https://skills.holoviz.org/'},
    },
    {
      id: 'copilot',
      title: 'Let users explore through chat',
      body:
        "Lumen lets users change filters and adjust views through plain-language requests. The assistant works with the app's existing controls and respects their available options and limits.",
      code: [
        'from lumen.ai import Planner',
        'from lumen.ai.agents import ChatAgent, ComponentControlAgent',
        'from lumen.ai.llm import OpenAI',
        '',
        'agent = ComponentControlAgent(components=page)',
        'assistant = Planner(agents=[ChatAgent, agent], llm=OpenAI())',
        'drawer = pn.ui.Drawer(assistant, anchor="right", variant="docked")',
        'page.main.append(drawer)',
      ].join('\n'),
      link: {
        label: 'Run the penguin copilot',
        href: 'https://github.com/holoviz/lumen/blob/main/examples/ai/penguin_copilot.py',
      },
    },
  ],
  screenshot: {
    image: asset('ai/penguin_copilot.webp'),
    caption: "One request updates the species filter, x-axis and color setting in Lumen's penguin copilot.",
    alt: 'A chat assistant beside a penguin dashboard, showing updated filters and chart settings',
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
  title: 'Use your preferred plotting library',
  lede:
    'Display your existing plots in Panel and connect them to interactive controls. Where supported, selections and clicks in a plot can update the rest of the app.',
  items: [
    {name: 'Matplotlib', file: 'Matplotlib', note: 'Figures from Matplotlib, Seaborn and Plotnine'},
    {name: 'Plotly', file: 'Plotly', note: 'Charts with click, hover and selection support'},
    {name: 'Bokeh', file: 'Bokeh', note: 'Interactive plots and visualizations'},
    {name: 'hvPlot and HoloViews', file: 'HoloViews', note: 'Plots with automatically generated controls'},
    {name: 'Altair and Vega', file: 'Vega', note: 'Charts with selections that update your app'},
    {name: 'ECharts', file: 'ECharts', note: 'Interactive charts from ECharts and pyecharts'},
    {name: 'Deck.gl', file: 'DeckGL', note: 'Large maps and geographic visualizations'},
    {name: 'Vizzu', file: 'Vizzu', note: 'Animated transitions between charts'},
  ].map((p) => ({
    ...p,
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
  title: 'Tables, chat, editors and more',
  lede:
    'Panel includes more than 130 components for building app interfaces, with documentation and examples for each.',
  items: [
    {name: 'Tabulator', section: 'widgets', note: 'Sort, filter and edit large tables'},
    {name: 'ChatInterface', section: 'chat', note: 'Streaming responses and conversation steps', material: true},
    {name: 'Terminal', section: 'widgets', note: 'Display live output and accept text input'},
    {name: 'JSONEditor', section: 'widgets', note: 'Edit and validate structured data'},
    {name: 'Trend', section: 'indicators', note: 'Track a value alongside its recent history'},
    {name: 'Gauge', section: 'indicators', note: 'Show a value within a range'},
    {name: 'Swipe', section: 'layouts', note: 'Compare two views with a draggable divider'},
    {name: 'TextEditor', section: 'widgets', note: 'Write and format rich text'},
    {name: 'Perspective', section: 'panes', note: 'Explore data with pivot tables, filters and charts'},
    {name: 'CrossSelector', section: 'widgets', note: 'Choose items by moving them between lists', material: true},
    {name: 'CodeEditor', section: 'widgets', note: 'Edit code with syntax highlighting'},
    {name: 'Player', section: 'widgets', note: 'Step through a sequence or play it as an animation', material: true},
  ].map((c) => ({
    ...c,
    image: asset(`components/${c.name}.webp`),
    href: (c.material ? materialReference : reference)(c.section, c.name),
  })),
  link: {label: 'Browse all components', href: `${DOCS}/reference/index.html`},
}

export const capabilities = [
  {
    title: 'Live data and streaming',
    body:
      'Update charts as new data arrives or display results as they become available. Panel supports asynchronous functions, scheduled updates and streaming responses.',
    href: `${DOCS}/how_to/callbacks/index.html`,
  },
  {
    title: 'Custom components',
    body: "Build components in React, Vue or JavaScript and use them alongside Panel's existing widgets.",
    href: `${DOCS}/how_to/custom_components/index.html`,
  },
  {
    title: 'Run apps in the browser',
    body: 'Package compatible apps to run entirely in the browser with WebAssembly, without a separate Python server.',
    href: `${DOCS}/how_to/wasm/index.html`,
  },
  {
    title: 'Authentication and performance',
    body: "Control access with OAuth, cache expensive computations and use Panel's admin tools to inspect performance.",
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
    note: 'Explore a million stars with linked views of their positions, brightness and color.',
  },
  {name: 'model_serving_monitor', title: 'Model serving monitor', note: 'Monitor model response times, drift and alerts'},
  {name: 'portfolio_analyzer', title: 'Portfolio analyzer', note: 'Explore investments with linked tables and price charts'},
  {name: 'glaciers', title: 'Glaciers of the world', note: 'Filter and explore data on 200,000 glaciers'},
  {name: 'penguin_crossfilter', title: 'Penguin crossfilter', note: 'Explore penguin data across four linked plots'},
  {name: 'storm_surge_studio', title: 'Storm surge studio', note: 'Explore a flood model with interactive controls'},
].map((g) => ({...g, image: asset(`gallery/${g.name}.webp`), href: galleryPage(g.name)}))

export const adoption = {
  title: 'Developed in the open, since 2018',
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
