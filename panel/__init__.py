"""
# Panel is a high level app and dashboarding framework

Works with the tools you know and ❤️.

[Check out](https://panel.holoviz.org/) | [Get started](https://panel.holoviz.org/getting_started/index.html) | [Join the community](https://discourse.holoviz.org/) | [Github](https://github.com/holoviz/panel) | [Twitter](https://twitter.com/Panel_org) | [LinkedIn](https://www.linkedin.com/company/79754450)

![Panel Dashboard](https://user-images.githubusercontent.com/42288570/152672367-6c239073-0ea0-4a2b-a4c0-817e8090e877.gif)

## Interactive models with `.bind`

![Interactive Model App](https://user-images.githubusercontent.com/42288570/152672364-582016c1-3085-4895-9884-541b896c34a6.gif)

You can use Panels `.bind` to bind your models to widgets.

```python
import panel as pn

color = "#C43F66"

pn.extension(sizing_mode="stretch_width", template="fast")


def model(a, b, emoji):
    result = "#" + (emoji * a) + " + " + (emoji * b) + " = " + (emoji * (a + b))
    return result

pn.pane.Markdown("## Input", margin=(5, 10)).servable(area="sidebar")
input1 = pn.widgets.RadioButtonGroup(value=1, options=[1, 2, 3], button_type="success", name="A").servable(area="sidebar")
input2 = pn.widgets.IntSlider(value=2, start=0, end=3, step=1, margin=(20, 10)).servable(area="sidebar")

interactive_add = pn.bind(model, a=input1, b=input2, emoji="⭐")
pn.panel(interactive_add).servable(area="main", title="My interactive MODEL")

pn.state.template.param.update(site="Panel", accent_base_color=color, header_background=color)
```

You can serve your app via

```bash
$ panel serve 'script.py' --autoreload
2022-01-23 15:00:31,373 Starting Bokeh server version 2.4.2 (running on Tornado 6.1)
2022-01-23 15:00:31,387 User authentication hooks NOT provided (default user enabled)
2022-01-23 15:00:31,389 Bokeh app running at: http://localhost:5006/script
```

The file can be a `.py` script or `.ipynb` notebook.

Try changing the return value of the function. Panel will magically ✨ understand how to show the 
objects you know and ❤️. 

This includes 
[Bokeh](https://panel.holoviz.org/reference/panes/Bokeh.html#panes-gallery-bokeh), \
[HoloViews](https://panel.holoviz.org/reference/panes/HoloViews.html#panes-gallery-holoviews), \
[Matplotlib](https://panel.holoviz.org/reference/panes/Matplotlib.html#panes-gallery-matplotlib) and \
[Plotly](https://panel.holoviz.org/reference/panes/Plotly.html#panes-gallery-plotly) figures.

## Interactive dataframes with `.interactive`

![Interactive DataFrame App](https://user-images.githubusercontent.com/42288570/152672366-39b8b964-5627-4448-9788-5faf86095c3c.gif)

You can use [hvplot .interactive](https://hvplot.holoviz.org/user_guide/Interactive.html) and 
Panels widgets to make your dataframes interactive.

```python
import panel as pn
import pandas as pd
import hvplot.pandas

color = "#0072B5"
df = pd.DataFrame(data={"x": [0, 1, 2, 3, 4], "y": [0, 2, 1, 3, 4]})

pn.extension(sizing_mode="stretch_width", template="fast")

pn.pane.Markdown("## Selection", margin=(10, 10)).servable(area="sidebar")
count = pn.widgets.RadioButtonGroup(value=5, options=[3, 4, 5], name="Count", button_type="success").servable(area="sidebar")

interactive_df = df.interactive().head(n=count)
pn.panel(interactive_df.panel(height=200)).servable(area="main")

interactive_plot = interactive_df.hvplot(x="x", y="y").opts(line_width=6, color=color)
pn.panel(interactive_plot.panel(height=200)).servable(area="main", title="My interactive DATAFRAME")

pn.state.template.param.update(site="Panel", accent_base_color=color, header_background=color)
```

The DataFrames can be any of Pandas, Dask, CuDF and Xarray dataframes.

For more about hvplot `.interactive` check out this [blog post](https://towardsdatascience.com/the-easiest-way-to-create-an-interactive-dashboard-in-python-77440f2511d1).
"""
from . import layout # noqa
from . import links # noqa
from . import pane # noqa
from . import param # noqa
from . import pipeline # noqa
from . import widgets # noqa

from .config import config, panel_extension as extension, __version__ # noqa
from .depends import bind, depends # noqa
from .interact import interact # noqa
from .io import _jupyter_server_extension_paths, ipywidget, serve, state # noqa
from .layout import ( # noqa
    Accordion, Card, Column, GridSpec, GridBox, FlexBox, Tabs, Row,
    Spacer, WidgetBox
)
from .pane import panel, Pane # noqa
from .param import Param # noqa
from .template import Template # noqa
from .widgets import indicators # noqa
