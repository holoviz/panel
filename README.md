<a href="https://panel.holoviz.org/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/holoviz/panel/raw/main/doc/_static/logo_horizontal_dark_theme.png">
    <img src="https://github.com/holoviz/panel/raw/main/doc/_static/logo_horizontal_light_theme.png" alt="Panel logo -- text is white in dark theme and black in light theme" width=400/>
  </picture>
</a>

# Panel: The powerful data exploration & web app framework for Python

Panel is an [open-source](https://github.com/holoviz/panel/blob/main/LICENSE.txt) Python library that lets you **easily build powerful tools, dashboards and complex applications entirely in Python**. It has a batteries-included philosophy, putting the PyData ecosystem, powerful data tables and much more at your fingertips. High-level reactive APIs and lower-level callback based APIs ensure you can quickly build exploratory applications, but you aren't limited if you build complex, multi-page apps with rich interactivity. Panel is a member of the [HoloViz](https://holoviz.org/) ecosystem, your gateway into a connected ecosystem of data exploration tools.

---

Enjoying Panel? Show your support with a [Github star](https://github.com/holoviz/panel) — it’s a simple click that means the world to us and helps others discover it too! ⭐️

---

<table>
<tbody>
<tr>
<td>Downloads</td>
<td><a href="https://pypistats.org/packages/panel" alt="PyPi Downloads"><img src="https://img.shields.io/pypi/dm/panel?label=pypi" /></a> <a href="https://anaconda.org/pyviz/panel" alt="Conda Downloads"><img src="https://pyviz.org/_static/cache/panel_conda_downloads_badge.svg" /></a></td>
</tr>
<tr>
<td>Build Status</td>
<td><a href="https://github.com/holoviz/panel/actions/workflows/test.yaml?query=branch%3Amain"><img src="https://github.com/holoviz/panel/workflows/tests/badge.svg?query=branch%3Amain" alt="Linux/MacOS Build Status"></a></td>
</tr>
<tr>
<td>Coverage</td>
<td><a href="https://codecov.io/gh/holoviz/panel"><img src="https://codecov.io/gh/holoviz/panel/branch/main/graph/badge.svg" alt="codecov"></a></td>
</tr>
<tr>
<td>Latest dev release</td>
<td><a href="https://github.com/holoviz/panel/tags"><img src="https://img.shields.io/github/v/tag/holoviz/panel.svg?label=tag&amp;colorB=11ccbb" alt="Github tag"></a> <a href="https://holoviz-dev.github.io/panel/"><img src="https://img.shields.io/website-up-down-green-red/https/holoviz-dev.github.io/panel.svg?label=dev%20website" alt="dev-site"></a></td>
</tr>
<tr>
<td>Latest release</td>
<td><a href="https://github.com/holoviz/panel/releases"><img src="https://img.shields.io/github/release/holoviz/panel.svg?label=tag&amp;colorB=11ccbb" alt="Github release"></a> <a href="https://pypi.python.org/pypi/panel"><img src="https://img.shields.io/pypi/v/panel.svg?colorB=cc77dd" alt="PyPI version"></a> <a href="https://anaconda.org/pyviz/panel"><img src="https://img.shields.io/conda/v/pyviz/panel.svg?colorB=4488ff&amp;style=flat" alt="panel version"></a> <a href="https://anaconda.org/conda-forge/panel"><img src="https://img.shields.io/conda/v/conda-forge/panel.svg?label=conda%7Cconda-forge&amp;colorB=4488ff" alt="conda-forge version"></a> <a href="https://anaconda.org/anaconda/panel"><img src="https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults&amp;style=flat&amp;colorB=4488ff" alt="defaults version"></a></td>
</tr>
<tr>
<td>Docs</td>
<td><a href="https://github.com/holoviz/panel/tree/gh-pages"><img src="https://img.shields.io/github/last-commit/holoviz/panel/gh-pages.svg" alt="gh-pages"></a> <a href="https://panel.holoviz.org"><img src="https://img.shields.io/website-up-down-green-red/https/panel.holoviz.org.svg" alt="site"></a></td>
</tr>
<tr>
<td>Notebooks</td>
<td><a href="https://panelite.holoviz.org/"><img src="https://img.shields.io/website-up-down-green-red/https/panel.holoviz.org.svg?label=Panelite" alt="dev-site"></a></td>
</tr>
<tr>
<td>Support</td>
<td><a href="https://discourse.holoviz.org/"><img src="https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.holoviz.org" alt="Discourse"></a> <a href="https://discord.gg/rb6gPXbdAr"><img alt="Discord" src="https://img.shields.io/discord/1075331058024861767"></a>
</td>
</tr>
</tbody>
</table>

[Home](https://panel.holoviz.org/) | [Installation instructions](#installation-instructions) | [Getting Started Guide](https://panel.holoviz.org/getting_started/index.html) | [Reference Guides](https://panel.holoviz.org/reference/index.html) | [Examples](#examples) | [License](#license) | [Support](#support--feedback)

## Panel works with the tools you know and love

[Panel](https://panel.holoviz.org/) makes it easy to combine widgets, plots, tables and other viewable Python objects into custom analysis tools, applications, and dashboards.

[![Panel NYC Taxi Linked Brushing](https://assets.holoviz.org/panel/readme/linked_brushing.gif)](https://panel.holoviz.org/reference/templates/FastGridTemplate.html)

<br/>

Panel works really well with the visualization tools you already know and love like [Altair/ Vega](https://panel.holoviz.org/reference/panes/Vega.html), [Bokeh](https://panel.holoviz.org/reference/panes/Bokeh.html), [Datashader](https://datashader.org/), [Deck.gl/ pydeck](https://panel.holoviz.org/reference/panes/DeckGL.html), [Echarts/ pyecharts](https://panel.holoviz.org/reference/panes/ECharts.html), [Folium](https://panel.holoviz.org/reference/panes/Folium.html), [HoloViews](https://holoviews.org/), [hvPlot](https://hvplot.holoviz.org), [plotnine](https://panel.holoviz.org/reference/panes/Matplotlib.html), [Matplotlib](https://panel.holoviz.org/reference/panes/Matplotlib.html), [Plotly](https://panel.holoviz.org/reference/panes/Plotly.html), [PyVista/ VTK](https://panel.holoviz.org/reference/panes/VTK.html), [Seaborn](https://panel.holoviz.org/gallery/styles/SeabornStyle.html) and more. Panel also works with the [ipywidgets](https://panel.holoviz.org/reference/panes/IPyWidget.html) ecosystem.

[![Pythons DataViz works with Panel](https://assets.holoviz.org/panel/readme/dataviz.gif)](https://panel.holoviz.org/reference/index.html#panes)

Panel provides bi-directional communication making it possible to react to clicks, selections, hover etc. events.

[![Vega Selections](https://assets.holoviz.org/panel/readme/vega_selections.gif)](https://panel.holoviz.org/reference/panes/Vega.html)

You can develop in [Jupyter Notebooks](http://jupyter.org) as well as editors like [VS Code](https://code.visualstudio.com/), [PyCharm](https://www.jetbrains.com/pycharm/) or [Spyder](https://www.spyder-ide.org/).

<table>
  <tr>
    <td><a href="https://blog.holoviz.org/panel_0.12.0.html#JupyterLab-previews"><img src="https://assets.holoviz.org/panel/readme/jupyterlab.gif" /></a></td>
    <td><a href="https://blog.holoviz.org/panel_0.11.0.html#Autoreload"><img src="https://assets.holoviz.org/panel/readme/editor.gif" /></a></td>
  </tr>
 </table>

Panel provides a unique combination of deployment options. You can share your data and models as

- a web application running on the [Tornado](https://www.tornadoweb.org/en/stable/) (default), [Flask](https://flask.palletsprojects.com/), [Django](https://www.djangoproject.com/) or [Fast API](https://fastapi.tiangolo.com/) web server.
- a stand alone client side application powered by [Pyodide](https://pyodide.org/en/stable/) or [PyScript](https://pyscript.net/) via [`panel convert`](https://panel.holoviz.org/how_to/wasm/convert.html).
- an interactive Jupyter notebook component.
- a static `.html` web page, a `.gif` video, a `.png` image and more.

Panel has something to offer for every one *from beginner to data pro*.

## Panel is a member of the HoloViz ecosystem

Panel is a member of the ambitious [HoloViz](https://holoviz.org/) dataviz ecosystem and has first class support for the other members like [hvPlot](https://hvplot.holoviz.org) (simple .hvplot plotting api), [HoloViews](https://holoviews.org/) (powerful plotting api), and [Datashader](https://datashader.org/) (big data viz).

Panel is built on top of [Param](https://param.holoviz.org). Param enables you to annotate your code with parameter ranges, documentation, and dependencies between parameters and code. With this approach,

- you don't ever have to commit to whether your code will be used in a notebook, a data app, in batch processing, or reports.
- you will write less code and be able to develop large, maintainable code bases!

## Mini getting-started

Head over to the [getting started guide](https://panel.holoviz.org/getting_started/index.html) for more!

### Installation Instructions

Panel can be installed on Linux, Windows, or Mac with ``conda``:

```bash
conda install panel
```

or with ``pip``:

```bash
pip install panel
```

See the [Environments](#environments) section below for additional instructions for your environment.

### Interactive data apps

Bring your data or model

```python
def model(n=5):
    return "⭐"*n
```

Bind it to a Panel *widget* and *lay it out*.

```python
import panel as pn

pn.extension()

slider = pn.widgets.IntSlider(value=5, start=1, end=5)

interactive_model = pn.bind(model, n=slider)

layout = pn.Column(slider, interactive_model)
```

![Panel Notebook Example](https://assets.holoviz.org/panel/readme/notebook.gif)

For deployment on a web server wrap it in a nice template.

```python
pn.template.FastListTemplate(
    site="Panel", title="Example", main=[layout],
).servable()
```

Start the server with

```bash
panel serve name_of_script.py --show
```

or

```bash
panel serve name_of_notebook.ipynb --show
```

![Panel Example App](https://assets.holoviz.org/panel/readme/example_app.gif)

## Examples

[![Panel Gallery](https://assets.holoviz.org/panel/readme/gallery.jpg)](https://panel.holoviz.org/gallery/index.html)

[![Panel Chat Examples](https://assets.holoviz.org/panel/readme/panel-chat-examples.jpg)](https://holoviz-topics.github.io/panel-chat-examples/)

[![Awesome Panel Gallery](https://assets.holoviz.org/panel/readme/awesome_panel.jpg)](https://www.awesome-panel.org)

## Get started

Develop applications in your favorite notebook or editor environment, including Jupyter(Lab) notebooks, VSCode, Google Colab and many more, [see our getting started guide](https://panel.holoviz.org/getting_started/installation.html#developing-in-different-editors) for more details.

## Support & Feedback

- Usage questions and showcases -> [HoloViz Community](https://holoviz.org/community.html)
- Bug reports and feature requests -> [Github](https://github.com/holoviz/panel)
- Developer discussions -> [Discord](https://discord.gg/rb6gPXbdAr)

For more detail check out the [HoloViz Community Guide](https://holoviz.org/community.html).

## Contributing ❤️

Check out the [Contributing Guide](CONTRIBUTING.MD).

## License

Panel is completely free and open-source. It is licensed under the [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause).

## Sponsors

The Panel project is also very grateful for the sponsorship by the organizations and companies below:

<table align="center">
<tr>
  <td>
    <a href="https://www.anaconda.com/">
      <img src="https://static.bokeh.org/sponsor/anaconda.png"
         alt="Anaconda Logo" width="200"/>
	 </a>
  </td>
  <td>
    <a href="https://www.blackstone.com/the-firm/">
    <img src="https://static.bokeh.org/sponsor/blackstone.png"
         alt="Blackstone Logo" width="200"/>
    </a>
  </td>
  <td>
    <a href="https://numfocus.org/">
    <img src="https://numfocus.org/wp-content/uploads/2017/03/numfocusweblogo_orig-1.png"
         alt="NumFOCUS Logo" width="200"/>
    </a>
  </td>
  <td>
    <a href="[https://www.blackstone.com/the-firm/](https://quansight.com/)">
    <img src="https://assets.holoviz.org/logos/Quansight-logo.svg"
         alt="Quansight Logo" width="200"/>
    </a>
  </td>

</tr>
</table>
