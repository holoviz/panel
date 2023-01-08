<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/holoviz/panel/raw/main/doc/_static/logo_horizontal_dark_theme.png">
  <img src="https://github.com/holoviz/panel/raw/main/doc/_static/logo_horizontal_light_theme.png" alt="Panel logo -- text is white in dark theme and black in light theme" width=400/>
</picture>

-----------------

# Panel makes it easy to share your data or model as a dashboard or web app

|    |    |
| --- | --- |
| Build Status | [![Linux/MacOS Build Status](https://github.com/holoviz/panel/workflows/pytest/badge.svg?query=branch%3Amain)](https://github.com/holoviz/panel/actions/workflows/test.yaml?query=branch%3Amain)
| Coverage | [![codecov](https://codecov.io/gh/holoviz/panel/branch/main/graph/badge.svg)](https://codecov.io/gh/holoviz/panel) |
| Latest dev release | [![Github tag](https://img.shields.io/github/v/tag/holoviz/panel.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/panel/tags) [![dev-site](https://img.shields.io/website-up-down-green-red/https/pyviz-dev.github.io/panel.svg?label=dev%20website)](https://pyviz-dev.github.io/panel/) |
| Latest release | [![Github release](https://img.shields.io/github/release/holoviz/panel.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/panel/releases) [![PyPI version](https://img.shields.io/pypi/v/panel.svg?colorB=cc77dd)](https://pypi.python.org/pypi/panel) [![panel version](https://img.shields.io/conda/v/pyviz/panel.svg?colorB=4488ff&style=flat)](https://anaconda.org/pyviz/panel) [![conda-forge version](https://img.shields.io/conda/v/conda-forge/panel.svg?label=conda%7Cconda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/panel) [![defaults version](https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults&style=flat&colorB=4488ff)](https://anaconda.org/anaconda/panel) |
| Docs | [![gh-pages](https://img.shields.io/github/last-commit/holoviz/panel/gh-pages.svg)](https://github.com/holoviz/panel/tree/gh-pages) [![site](https://img.shields.io/website-up-down-green-red/https/panel.holoviz.org.svg)](https://panel.holoviz.org) |
| Binder | [![Binder](https://img.shields.io/badge/launch%20v0.14.2-binder-579aca.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFkAAABZCAMAAABi1XidAAAB8lBMVEX///9XmsrmZYH1olJXmsr1olJXmsrmZYH1olJXmsr1olJXmsrmZYH1olL1olJXmsr1olJXmsrmZYH1olL1olJXmsrmZYH1olJXmsr1olL1olJXmsrmZYH1olL1olJXmsrmZYH1olL1olL0nFf1olJXmsrmZYH1olJXmsq8dZb1olJXmsrmZYH1olJXmspXmspXmsr1olL1olJXmsrmZYH1olJXmsr1olL1olJXmsrmZYH1olL1olLeaIVXmsrmZYH1olL1olL1olJXmsrmZYH1olLna31Xmsr1olJXmsr1olJXmsrmZYH1olLqoVr1olJXmsr1olJXmsrmZYH1olL1olKkfaPobXvviGabgadXmsqThKuofKHmZ4Dobnr1olJXmsr1olJXmspXmsr1olJXmsrfZ4TuhWn1olL1olJXmsqBi7X1olJXmspZmslbmMhbmsdemsVfl8ZgmsNim8Jpk8F0m7R4m7F5nLB6jbh7jbiDirOEibOGnKaMhq+PnaCVg6qWg6qegKaff6WhnpKofKGtnomxeZy3noG6dZi+n3vCcpPDcpPGn3bLb4/Mb47UbIrVa4rYoGjdaIbeaIXhoWHmZYHobXvpcHjqdHXreHLroVrsfG/uhGnuh2bwj2Hxk17yl1vzmljzm1j0nlX1olL3AJXWAAAAbXRSTlMAEBAQHx8gICAuLjAwMDw9PUBAQEpQUFBXV1hgYGBkcHBwcXl8gICAgoiIkJCQlJicnJ2goKCmqK+wsLC4usDAwMjP0NDQ1NbW3Nzg4ODi5+3v8PDw8/T09PX29vb39/f5+fr7+/z8/Pz9/v7+zczCxgAABC5JREFUeAHN1ul3k0UUBvCb1CTVpmpaitAGSLSpSuKCLWpbTKNJFGlcSMAFF63iUmRccNG6gLbuxkXU66JAUef/9LSpmXnyLr3T5AO/rzl5zj137p136BISy44fKJXuGN/d19PUfYeO67Znqtf2KH33Id1psXoFdW30sPZ1sMvs2D060AHqws4FHeJojLZqnw53cmfvg+XR8mC0OEjuxrXEkX5ydeVJLVIlV0e10PXk5k7dYeHu7Cj1j+49uKg7uLU61tGLw1lq27ugQYlclHC4bgv7VQ+TAyj5Zc/UjsPvs1sd5cWryWObtvWT2EPa4rtnWW3JkpjggEpbOsPr7F7EyNewtpBIslA7p43HCsnwooXTEc3UmPmCNn5lrqTJxy6nRmcavGZVt/3Da2pD5NHvsOHJCrdc1G2r3DITpU7yic7w/7Rxnjc0kt5GC4djiv2Sz3Fb2iEZg41/ddsFDoyuYrIkmFehz0HR2thPgQqMyQYb2OtB0WxsZ3BeG3+wpRb1vzl2UYBog8FfGhttFKjtAclnZYrRo9ryG9uG/FZQU4AEg8ZE9LjGMzTmqKXPLnlWVnIlQQTvxJf8ip7VgjZjyVPrjw1te5otM7RmP7xm+sK2Gv9I8Gi++BRbEkR9EBw8zRUcKxwp73xkaLiqQb+kGduJTNHG72zcW9LoJgqQxpP3/Tj//c3yB0tqzaml05/+orHLksVO+95kX7/7qgJvnjlrfr2Ggsyx0eoy9uPzN5SPd86aXggOsEKW2Prz7du3VID3/tzs/sSRs2w7ovVHKtjrX2pd7ZMlTxAYfBAL9jiDwfLkq55Tm7ifhMlTGPyCAs7RFRhn47JnlcB9RM5T97ASuZXIcVNuUDIndpDbdsfrqsOppeXl5Y+XVKdjFCTh+zGaVuj0d9zy05PPK3QzBamxdwtTCrzyg/2Rvf2EstUjordGwa/kx9mSJLr8mLLtCW8HHGJc2R5hS219IiF6PnTusOqcMl57gm0Z8kanKMAQg0qSyuZfn7zItsbGyO9QlnxY0eCuD1XL2ys/MsrQhltE7Ug0uFOzufJFE2PxBo/YAx8XPPdDwWN0MrDRYIZF0mSMKCNHgaIVFoBbNoLJ7tEQDKxGF0kcLQimojCZopv0OkNOyWCCg9XMVAi7ARJzQdM2QUh0gmBozjc3Skg6dSBRqDGYSUOu66Zg+I2fNZs/M3/f/Grl/XnyF1Gw3VKCez0PN5IUfFLqvgUN4C0qNqYs5YhPL+aVZYDE4IpUk57oSFnJm4FyCqqOE0jhY2SMyLFoo56zyo6becOS5UVDdj7Vih0zp+tcMhwRpBeLyqtIjlJKAIZSbI8SGSF3k0pA3mR5tHuwPFoa7N7reoq2bqCsAk1HqCu5uvI1n6JuRXI+S1Mco54YmYTwcn6Aeic+kssXi8XpXC4V3t7/ADuTNKaQJdScAAAAAElFTkSuQmCC)](https://mybinder.org/v2/gh/holoviz/panel/v0.14.2?urlpath=lab/tree/examples) |
| Support | [![Discourse](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.holoviz.org)](https://discourse.holoviz.org/) |

## Panel works with the tools you know and love

[Panel](https://panel.holoviz.org/) makes it easy to combine widgets, plots, tables and other viewable objects into custom analysis tools, applications, and dashboards.

[![Panel Example](https://user-images.githubusercontent.com/42288570/211207118-23d1e6d5-0c47-4489-aab5-892de338cc3b.gif)](https://panel.holoviz.org/reference/templates/FastGridTemplate.html)

<br/>

Panel is a member of the [HoloViz](https://holoviz.org/) dataviz ecosystem and has first class support for the other members like [hvPlot](https://hvplot.holoviz.org) (simple .hvplot api),  and [Datashader](https://datashader.org/) (big data viz).

<table>
  <tr>
    <td border=1><a href="https://panel.holoviz.org"><img style="max-height:130px;width:90%;margin-right:20px;" src="https://holoviz.org/assets/panel.png"></a></td>
    <td border=1><a href="https://hvplot.holoviz.org"><img style="max-height:130px;width:90%;margin-right:20px;" src="https://holoviz.org/assets/hvplot.png"></a></td>
    <td border=1><a href="https://holoviews.org"><img style="max-height:130px;width:90%;margin-right:20px;" src="https://holoviz.org/assets/holoviews.png"></a></td>
    <td border=1><a href="https://geoviews.org"><img style="max-height:130px;width:90%;margin-right:20px;" src="https://holoviz.org/assets/geoviews.png"></a></td>
    <td border=1><a href="https://datashader.org"><img style="max-height:130px;width:90%;margin-right:20px;" src="https://holoviz.org/assets/datashader.png"></a></td>
    <td border=1><a href="https://lumen.holoviz.org"><img style="max-height:130px;width:90%;margin-right:20px;" src="https://holoviz.org/assets/lumen.png"></a></td>
    <td border=1><a href="https://param.holoviz.org"><img style="max-height:130px;width:90%;margin-right:20px;" src="https://holoviz.org/assets/param.png"></a></td>
    <td border=1><a href="https://colorcet.holoviz.org"><img style="max-height:130px;width:90%;margin-right:20px;" src="https://holoviz.org/assets/colorcet.png"></a></td>
  <tr>
</table>

<br/>

Panel works really well with the rest of Pythons dataviz ecosystem including [Altair](https://altair-viz.github.io/), [Bokeh](https://bokeh.pydata.org), [Folium](https://python-visualization.github.io/folium/), [PlotNine](https://plotnine.readthedocs.io/en/stable/), [Matplotlib](https://matplotlib.org/), [Plotly](https://plotly.com/), [pydeck](https://pydeck.gl/), [pyecharts](https://pyecharts.org/#/), [PyVista](https://docs.pyvista.org/), [Seaborn](https://seaborn.pydata.org/) and more. Panel also works with the [ipywidgets](https://ipywidgets.readthedocs.io/en/stable/) ecosystem.

[![Pythons DataViz works with Panel](https://github.com/MarcSkovMadsen/dataviz-in-python/raw/main/assets/dataviz-in-python.gif)](https://panel.holoviz.org/reference/index.html#panes)

You can develop in [Jupyter Notebooks](http://jupyter.org) as well as editors like [VS Code](https://code.visualstudio.com/), [PyCharm](https://www.jetbrains.com/pycharm/) or [Spyder](https://www.spyder-ide.org/).

<table>
    <tr>
      <td border=1><img src="https://user-images.githubusercontent.com/42288570/211206926-e8300669-07ad-4fa9-b326-18790e0a2758.gif" /></td>
      <td border=1><img src="https://user-images.githubusercontent.com/42288570/211208453-b574a257-aa0e-42be-bcce-879fcb5ecc86.gif" /></a></td>
    <tr>
  </table>

<br>

Panel provides a unique combination of sharing options. You can share your work as

- a web application running on the [Tornado](https://www.tornadoweb.org/en/stable/) (default), [Flask](https://flask.palletsprojects.com/), [Django](https://www.djangoproject.com/) or [Fast API](https://fastapi.tiangolo.com/) web server.
- a stand alone client side application powered by [Pyodide](https://pyodide.org/en/stable/) or [PyScript](https://pyscript.net/) via [`panel convert`](https://panel.holoviz.org/user_guide/Running_in_Webassembly.html).
- an interactive Jupyter notebook component.
- a static `.html` web page or a `.png` image.

<br>

Examples

<table>
  <tr>
    <td border=1><a href="https://examples.pyviz.org/attractors/attractors_panel.html"><b>Attractors</b></a><br><a href="https://attractors.pyviz.demo.anaconda.com/attractors_panel"><img src="http://assets.holoviews.org/panel/thumbnails/index/attractors.png" /></a></td>
    <td border=1><a href="https://examples.pyviz.org/gapminders/gapminders.html"><b>Gapminders</b></a><br><a href="https://gapminders.pyviz.demo.anaconda.com"><img src="http://assets.holoviews.org/panel/thumbnails/index/gapminders.png" /></a></td>
    <td border=1><a href="https://examples.pyviz.org/nyc_taxi/dashboard.html"><b>NYC Taxi</b></a><br><a href="https://nyc-taxi.pyviz.demo.anaconda.com"><img src="http://assets.holoviews.org/panel/thumbnails/index/nyc_taxi.png" /></a></td>
    <td border=1><a href="https://examples.pyviz.org/glaciers/glaciers.html"><b>Glaciers</b></a><br><a href="https://glaciers.pyviz.demo.anaconda.com"><img src="http://assets.holoviews.org/panel/thumbnails/index/glaciers.png" /></a></td>
    <td border=1><a href="https://examples.pyviz.org/portfolio_optimizer/portfolio.html"><b>Portfolio Optimizer</b></a><br><a href="https://portfolio-optimizer.pyviz.demo.anaconda.com"><img src="http://assets.holoviews.org/panel/thumbnails/index/portfolio_optimizer.png" /></a></td>
  <tr>
</table>

## Using Panel for declarative, reactive programming

Panel can also be used with the separate [Param](https://param.pyviz.org) project to create interactively configurable objects with or without associated visualizations, in a fully [declarative](https://en.wikipedia.org/wiki/Declarative_programming) way. With this approach, you declare your configurable object using the pure-Python, zero-dependency `param` library, annotating your code with parameter ranges, documentation, and dependencies between parameters and your code.  Using this information, you can make all of your domain-specific code be optionally configurable in a GUI, with optional visual displays and debugging information if you like, all with just a few lines of declarations. With this approach, you don't ever have to commit to whether your code will be used in a notebook, in a GUI app, or completely behind the scenes in batch processing or reports -- the same code can support all of these cases equally well, once you declare the associated parameters and constraints. This approach lets you completely separate your domain-specific code from anything to do with web browsers, GUI toolkits, or other volatile technologies that would otherwise make your hard work become obsolete as they change over time.

## Usage

Panel can be used in a wide range of development environments:

### Editor + Server


You can edit your Panel code as a `.py` file in any text editor, marking the objects you want to render as ``.servable()``, then launch a server with:

```bash
panel serve my_script.py --show --autoreload
```

to open a browser tab showing your app or dashboard and backed by a live Python process. The `--autoreload` flag ensures that the app reloads whenever you make a change to the Python source.

### JupyterLab and Classic notebook

In the classic Jupyter notebook environment and JupyterLab, first make sure to load the ``pn.extension()``. Panel objects will then render themselves if they are the last item in a notebook cell. For versions of ``jupyterlab>=3.0`` the necessary extension is automatically bundled in the ``pyviz_comms`` package, which must be >=2.0. However note that for version of ``jupyterlab<3.0`` you must also manually install the JupyterLab extension with:

```bash
jupyter labextension install @pyviz/jupyterlab_pyviz
```

### Google Colab

In the Google Colaboratory notebook, first make sure to load the `pn.extension()`. Panel objects will then render themselves if they are the last item in a notebook cell. Please note that in Colab rendering for each notebook cell is isolated, which means that every cell must reload the Panel extension code separately. This will result in somewhat slower and larger notebook than with other notebook technologies.

### VSCode notebook

Visual Studio Code (VSCode) versions 2020.4.74986 and later support ipywidgets, and Panel objects can be used as ipywidgets since Panel 0.10 thanks to `jupyter_bokeh`, which means that you can now use Panel components interactively in VSCode. Ensure you install `jupyter_bokeh` with `pip install jupyter_bokeh` or `conda install -c bokeh jupyter_bokeh` and then enable the extension with `pn.extension()`.

### nteract and other ipywidgets notebooks

In other notebook environments that support rendering ipywidgets interactively, such as nteract, you can use the same underlying ipywidgets support as for vscode: Install `jupyter_bokeh` and then use `pn.extension(comms='ipywidgets')`.

### Other environments

If your development environment offers embedded Python processes but does not support ipywidgets or Jupyter "comms" (communication channels), you will notice that some or all interactive functionality is missing. Some widgets that operate only in JavaScript will work fine, but others require communication channels between JavaScript and Python. In such cases you can either request ipywidgets or Panel support from the editor or environment, or else use the Editor + Server approach above.

## Sponsors

The Panel project is grateful for the sponsorship by the organizations and companies below:

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
