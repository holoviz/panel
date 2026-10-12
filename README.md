<a href="https://panel.holoviz.org/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/holoviz/panel/raw/main/doc/_static/logo_horizontal_dark_theme.png">
    <img src="https://github.com/holoviz/panel/raw/main/doc/_static/logo_horizontal_light_theme.png" alt="Panel logo" width=400/>
  </picture>
</a>

# Build data apps with the Python tools you know

Panel is an [open-source](https://github.com/holoviz/panel/blob/main/LICENSE.txt) library for interactive dashboards and web apps. Widgets, plots and layouts are ordinary Python objects that you connect to your data and models, pass between functions and classes, and test like the rest of your code. There are no string IDs to match up and no script that reruns on every click.

[![PyPI](https://img.shields.io/pypi/v/panel.svg?colorB=cc77dd)](https://pypi.python.org/pypi/panel) [![conda-forge](https://img.shields.io/conda/v/conda-forge/panel.svg?label=conda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/panel) [![Downloads](https://img.shields.io/pypi/dm/panel?label=downloads)](https://pypistats.org/packages/panel) [![Tests](https://github.com/holoviz/panel/workflows/tests/badge.svg?query=branch%3Amain)](https://github.com/holoviz/panel/actions/workflows/test.yaml?query=branch%3Amain) [![Coverage](https://codecov.io/gh/holoviz/panel/branch/main/graph/badge.svg)](https://codecov.io/gh/holoviz/panel) [![Discourse](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.holoviz.org)](https://discourse.holoviz.org/c/panel/5) [![Discord](https://img.shields.io/discord/1075331058024861767)](https://discord.gg/UXdtYyGVQX)

[Home](https://panel.holoviz.org/) | [Getting started](https://panel.holoviz.org/getting_started/index.html) | [Components](https://panel.holoviz.org/reference/index.html) | [App gallery](https://panel.holoviz.org/gallery/index.html) | [API](https://panel.holoviz.org/api/index.html) | [Support](#community-and-support)

```bash
pip install panel
```

or `conda install -c conda-forge panel`.

<a href="https://panel.holoviz.org/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/readme/hero-dark.webp">
    <img src="https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/readme/hero-light.webp" alt="Three widgets beside a chart of a random walk and its moving average"/>
  </picture>
</a>

Create the controls, define the plot, then connect the controls and arrange the app. The same code renders in a notebook cell and serves as an app with `panel serve app.py`.

```python
import numpy as np, panel as pn
import holoviews as hv

pn.extension()

window = pn.ui.IntSlider(name="Window", value=30, start=5, end=90)
sigma  = pn.ui.FloatSlider(name="Volatility", value=1.0, start=0.2, end=3)
ticker = pn.ui.RadioButtonGroup(name="Series", options=["AAPL", "MSFT", "NVDA"])

def series(window, sigma, ticker):
    rng = np.random.default_rng(sum(map(ord, ticker)))
    walk = np.cumsum(rng.normal(0, sigma, 400))
    smooth = np.convolve(walk, np.ones(window) / window, "same")
    return hv.Curve(walk).opts(alpha=0.4) * hv.Curve(smooth)

plot = pn.bind(series, window, sigma, ticker)
pn.ui.Row(pn.ui.Column(window, sigma, ticker), plot).servable()
```

## Update only what needs to change

When a user changes a control, Panel runs only the code connected to it. In a small app, rerunning everything is cheap and the difference is hard to notice. In a real application that loads large datasets, fits models and keeps user state, it determines how quickly the app responds and how much caching and state management you have to write to keep it that way.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/readme/execution-dark.webp">
  <img src="https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/readme/execution-light.webp" alt="The same five-step app after a control change: full-script execution repeats all five steps, while Panel updates only the model and forecast"/>
</picture>

[Compare Panel and Streamlit](https://panel.holoviz.org/explanation/comparisons/compare_streamlit.html)

## Built with Panel

Explore example apps for science, finance and machine learning. Each includes source code you can run and adapt.

<table>
  <tr>
    <td width="33%"><a href="https://panel.holoviz.org/gallery/gaia_million_star_atlas.html"><img src="https://raw.githubusercontent.com/holoviz/panel/main/doc/homepage/src/assets/gallery/gaia_million_star_atlas.webp" alt="Gaia million star atlas"/></a><br/><b>Gaia million star atlas</b><br/>Explore a million stars with linked views of their positions, brightness and color</td>
    <td width="33%"><a href="https://panel.holoviz.org/gallery/model_serving_monitor.html"><img src="https://raw.githubusercontent.com/holoviz/panel/main/doc/homepage/src/assets/gallery/model_serving_monitor.webp" alt="Model serving monitor"/></a><br/><b>Model serving monitor</b><br/>Monitor model response times, drift and alerts</td>
    <td width="33%"><a href="https://panel.holoviz.org/gallery/portfolio_analyzer.html"><img src="https://raw.githubusercontent.com/holoviz/panel/main/doc/homepage/src/assets/gallery/portfolio_analyzer.webp" alt="Portfolio analyzer"/></a><br/><b>Portfolio analyzer</b><br/>Explore investments with linked tables and price charts</td>
  </tr>
  <tr>
    <td><a href="https://panel.holoviz.org/gallery/glaciers.html"><img src="https://raw.githubusercontent.com/holoviz/panel/main/doc/homepage/src/assets/gallery/glaciers.webp" alt="Glaciers of the world"/></a><br/><b>Glaciers of the world</b><br/>Filter and explore data on 200,000 glaciers</td>
    <td><a href="https://panel.holoviz.org/gallery/penguin_crossfilter.html"><img src="https://raw.githubusercontent.com/holoviz/panel/main/doc/homepage/src/assets/gallery/penguin_crossfilter.webp" alt="Penguin crossfilter"/></a><br/><b>Penguin crossfilter</b><br/>Explore penguin data across four linked plots</td>
    <td><a href="https://panel.holoviz.org/gallery/storm_surge_studio.html"><img src="https://raw.githubusercontent.com/holoviz/panel/main/doc/homepage/src/assets/gallery/storm_surge_studio.webp" alt="Storm surge studio"/></a><br/><b>Storm surge studio</b><br/>Explore a flood model with interactive controls</td>
  </tr>
</table>

[Browse all examples](https://panel.holoviz.org/gallery/index.html)

## AI tools for developers and users

Use HoloViz skills to help coding assistants work with Panel, and Lumen to add an assistant to your app.

**Build with coding assistants.** [HoloViz skills](https://skills.holoviz.org/) give coding assistants guidance on building, reviewing, debugging and testing Panel apps with current APIs. Install them for Claude Code, Codex, Copilot, Cursor, Gemini CLI and other supported tools.

```bash
pip install holoviz-skills
holoviz-skills install
```

**Let users explore through chat.** [Lumen](https://lumen.holoviz.org/) lets users change filters and adjust views through plain-language requests. The assistant works with the app's existing controls and respects their available options and limits.

```python
from lumen.ai import Planner
from lumen.ai.agents import ChatAgent, ComponentControlAgent
from lumen.ai.llm import OpenAI

agent = ComponentControlAgent(components=page)
assistant = Planner(agents=[ChatAgent, agent], llm=OpenAI())
drawer = pn.ui.Drawer(assistant, anchor="right", variant="docked")
page.main.append(drawer)
```

<a href="https://github.com/holoviz/lumen/blob/main/examples/ai/penguin_copilot.py"><img src="https://raw.githubusercontent.com/holoviz/panel/main/doc/homepage/src/assets/ai/penguin_copilot.webp" alt="A chat assistant beside a penguin dashboard, showing updated filters and chart settings"/></a>

One request updates the species filter, x-axis and color setting in Lumen's [penguin copilot](https://github.com/holoviz/lumen/blob/main/examples/ai/penguin_copilot.py).

## Organize your app as it grows

Connect widgets to functions for a simple app, or use reusable components to organize a larger one. Both approaches work together. Use `pn.bind` to connect a Python function to widgets, group data, settings and behavior in a component, and build pages from smaller components that share data and stay in sync. [Param](https://param.holoviz.org) lets you define valid values and how changes affect the app, making components easier to reuse and test.

```python
class Explorer(pn.viewable.Viewer):
    data = param.DataFrame(allow_refs=True)
    window = param.Integer(30, bounds=(5, 90))

    @param.depends("data", "window")
    def plot(self):
        return view(self.data, self.window)

class Dashboard(pn.viewable.Viewer):
    data = param.DataFrame()

    def __panel__(self):
        ref = self.param.data
        return pn.ui.Tabs(
            ("Explore", Explorer(data=ref)),
            ("Report", Report(data=ref)),
        )
```

Built this way, Panel apps run in production as multi-page internal platforms with authentication, editable tables, review workflows and chat assistants used by whole teams. [Lumen](https://lumen.holoviz.org/), a complete AI data exploration application, is built entirely with Panel. Because Panel keeps a live Python session for every visitor, it suits apps built around data, models and computation. A consumer product such as a public message board or a full word processor is better served by a general-purpose web framework, which can still embed Panel apps through FastAPI or Django.

[Choosing between functions and classes](https://panel.holoviz.org/explanation/api/functions_vs_classes.html)

## From development to deployment

Work in a notebook or your preferred editor, then deploy the same app for others to use.

1. **In a notebook.** Explore data with live widgets and plots in Jupyter, JupyterLab, VS Code, Colab or marimo.
2. **From your editor.** Build your app in a Python file, mark the layout with `.servable()` and run `panel serve app.py --dev`. Development mode reloads the app as you edit.
3. **In production.** Host your app on your own infrastructure, add authentication, or integrate it with FastAPI or Django. Compatible apps can also run entirely in the browser with WebAssembly via `panel convert app.py`.

## Use your preferred plotting library

Display your existing plots in Panel and connect them to interactive controls. Where supported, selections and clicks in a plot can update the rest of the app. Panel works with [Matplotlib](https://panel.holoviz.org/reference/panes/Matplotlib.html) (including Seaborn and Plotnine), [Plotly](https://panel.holoviz.org/reference/panes/Plotly.html), [Bokeh](https://panel.holoviz.org/reference/panes/Bokeh.html), [hvPlot and HoloViews](https://panel.holoviz.org/reference/panes/HoloViews.html), [Altair and Vega](https://panel.holoviz.org/reference/panes/Vega.html), [ECharts](https://panel.holoviz.org/reference/panes/ECharts.html), [Deck.gl](https://panel.holoviz.org/reference/panes/DeckGL.html), [Vizzu](https://panel.holoviz.org/reference/panes/Vizzu.html), [VTK](https://panel.holoviz.org/reference/panes/VTK.html), [Folium](https://panel.holoviz.org/reference/panes/Folium.html) and [ipywidgets](https://panel.holoviz.org/reference/panes/IPyWidget.html).

## Tables, chat, editors and more

Panel includes more than 130 components for building app interfaces, with documentation and examples for each, from [Tabulator](https://panel.holoviz.org/reference/widgets/Tabulator.html) for sorting, filtering and editing large tables to [ChatInterface](https://panel-material-ui.holoviz.org/reference/chat/ChatInterface.html) for streaming responses, a [Terminal](https://panel.holoviz.org/reference/widgets/Terminal.html) and [Perspective](https://panel.holoviz.org/reference/panes/Perspective.html) pivot tables. [Browse all components](https://panel.holoviz.org/reference/index.html)

## Extend your app

Handle live data, add custom interfaces and manage access to your app.

- **[Live data and streaming](https://panel.holoviz.org/how_to/callbacks/index.html).** Update charts as new data arrives or display results as they become available. Panel supports asynchronous functions, scheduled updates and streaming responses.
- **[Custom components](https://panel.holoviz.org/how_to/custom_components/index.html).** Build components in React, Vue or JavaScript and use them alongside Panel's existing widgets.
- **[Run apps in the browser](https://panel.holoviz.org/how_to/wasm/index.html).** Package compatible apps to run entirely in the browser with WebAssembly, without a separate Python server.
- **[Authentication and performance](https://panel.holoviz.org/how_to/authentication/index.html).** Control access with OAuth, cache expensive computations and use Panel's admin tools to inspect performance.

## Community and support

Panel has been developed in the open, since its first release in 2018. It is maintained by a team at Anaconda together with contributors from research labs, banks, and instrument makers, and is part of [HoloViz](https://holoviz.org/), a set of Python tools for working with data.

- Ask usage questions on [Discourse](https://discourse.holoviz.org/c/panel/5) or [Discord](https://discord.gg/UXdtYyGVQX).
- Report bugs and request features in [GitHub issues](https://github.com/holoviz/panel/issues).
- See the [contributing guide](CONTRIBUTING.MD) to get involved.

Panel is free and open-source under the [BSD 3-Clause License](https://github.com/holoviz/panel/blob/main/LICENSE.txt).

## Sponsors

The Panel project is grateful for the sponsorship by the organizations and companies below:

<table align="center">
<tr>
  <td>
    <a href="https://www.anaconda.com/">
      <img src="https://static.bokeh.org/sponsor/anaconda.png" alt="Anaconda Logo" width="200"/>
    </a>
  </td>
  <td>
    <a href="https://www.blackstone.com/the-firm/">
      <img src="https://static.bokeh.org/sponsor/blackstone.png" alt="Blackstone Logo" width="200"/>
    </a>
  </td>
  <td>
    <a href="https://numfocus.org/">
      <img src="https://numfocus.org/wp-content/uploads/2017/03/numfocusweblogo_orig-1.png" alt="NumFOCUS Logo" width="200"/>
    </a>
  </td>
  <td>
    <a href="https://quansight.com/">
      <img src="https://assets.holoviz.org/logos/Quansight-logo.svg" alt="Quansight Logo" width="200"/>
    </a>
  </td>
</tr>
</table>
