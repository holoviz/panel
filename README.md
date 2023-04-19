<a href="https://panel.holoviz.org/"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/holoviz/panel/raw/main/doc/_static/logo_horizontal_dark_theme.png">
  <img src="https://github.com/holoviz/panel/raw/main/doc/_static/logo_horizontal_light_theme.png" alt="Panel logo -- text is white in dark theme and black in light theme" width=400/>
</picture></a>

# Panel: the most flexible data app framework for Python

<table>
<tbody>
<tr>
<td>Build Status</td>
<td><a href="https://github.com/holoviz/panel/actions/workflows/test.yaml?query=branch%3Amain"><img src="https://github.com/holoviz/panel/workflows/pytest/badge.svg?query=branch%3Amain" alt="Linux/MacOS Build Status"></a></td>
</tr>
<tr>
<td>Coverage</td>
<td><a href="https://codecov.io/gh/holoviz/panel"><img src="https://codecov.io/gh/holoviz/panel/branch/main/graph/badge.svg" alt="codecov"></a></td>
</tr>
<tr>
<td>Latest dev release</td>
<td><a href="https://github.com/holoviz/panel/tags"><img src="https://img.shields.io/github/v/tag/holoviz/panel.svg?label=tag&amp;colorB=11ccbb" alt="Github tag"></a> <a href="https://pyviz-dev.github.io/panel/"><img src="https://img.shields.io/website-up-down-green-red/https/pyviz-dev.github.io/panel.svg?label=dev%20website" alt="dev-site"></a></td>
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
<td><a href="https://panelite.holoviz.org/"><img src="https://img.shields.io/website-up-down-green-red/https/panel.holoviz.org.svg?label=Panelite" alt="dev-site"></a> <a href="https://mybinder.org/v2/gh/holoviz/panel/v0.14.2?urlpath=lab/tree/examples"><img src="https://img.shields.io/badge/launch%20v0.14.2-binder-579aca.svg?logo=data:image/png;base64,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" alt="Binder"></a></td>
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

[![Vega Selections](https://blog.holoviz.org/images/vega_selection.gif)](https://panel.holoviz.org/reference/panes/Vega.html)

You can develop in [Jupyter Notebooks](http://jupyter.org) as well as editors like [VS Code](https://code.visualstudio.com/), [PyCharm](https://www.jetbrains.com/pycharm/) or [Spyder](https://www.spyder-ide.org/).

<table>
  <tr>
    <td><a href="https://blog.holoviz.org/panel_0.12.0.html#JupyterLab-previews"><img src="https://assets.holoviz.org/panel/readme/jupyterlab.gif" /></a></td>
    <td><a href="https://blog.holoviz.org/panel_0.11.0.html#Autoreload"><img src="https://assets.holoviz.org/panel/readme/editor.gif" /></a></td>
  </tr>
 </table>

Panel provides a unique combination of deployment options. You can share your data and models as

- a web application running on the [Tornado](https://www.tornadoweb.org/en/stable/) (default), [Flask](https://flask.palletsprojects.com/), [Django](https://www.djangoproject.com/) or [Fast API](https://fastapi.tiangolo.com/) web server.
- a stand alone client side application powered by [Pyodide](https://pyodide.org/en/stable/) or [PyScript](https://pyscript.net/) via [`panel convert`](https://panel.holoviz.org/user_guide/Running_in_Webassembly.html).
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
conda install -c pyviz panel
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

[![Awesome Panel Gallery](https://assets.holoviz.org/panel/readme/awesome_panel.jpg)](https://www.awesome-panel.org/gallery?theme=default)

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

The Panel project is grateful for the numerous contributions from the community including

- The [awesome-panel.org](https://www.awesome-panel.org/) project, [tweets](https://twitter.com/MarcSkovMadsen) and [videos](https://www.youtube.com/watch?v=7dJO4j4ENhg&list=PLrrcIlm1vLr69f4CsTlrO0wSNBw6VbsJA) by [Marc Skov Madsen](https://www.linkedin.com/in/marcskovmadsen)
- Inspiring [blog posts](https://sophiamyang.medium.com/), [tweets](https://twitter.com/sophiamyang) and [videos](https://www.youtube.com/watch?v=wlzkiGPIV3I&list=PL2KLV6jxFCI39YW7v-nVZOp34cVhYpSJO) by [Sophia Yang](https://www.linkedin.com/in/sophiamyang/)
- Cool [videos](https://youtu.be/uhxiXOTKzfs) by [Thu Hien Vu](https://www.linkedin.com/in/thu-hien-vu-3766b174/)

The Panel project is also very grateful for the sponsorship by the organizations and companies below:

<table align="center">
<tr>
  <td>
    <a href="https://www.anaconda.com/">
      <img src="https://static.bokeh.org/sponsor/anaconda.png"
         alt="Anaconda Logo" width="200"/>
	 </a>
  </td>
  <td colspan="2">
    <a href="https://www.blackstone.com/the-firm/">
    <img src="https://static.bokeh.org/sponsor/blackstone.png"
         alt="Blackstone Logo" width="400"/>
    </a>
  </td>
</tr>
</table>
