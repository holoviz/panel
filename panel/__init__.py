"""
Panel is a high level app and dashboarding framework
====================================================

Works with the tools you know and ❤️.

`Getting Started<https://panel.holoviz.org>`_ \| `Discourse`_ \| `Github`_ \| `Twitter`_ \|
`LinkedIn`_

Interactive models with ``.bind``
---------------------------------

.. figure:: https://user-images.githubusercontent.com/42288570/150686594-21b03e55-79ef-406b-9e61-1764c6b493c3.gif
   :alt: Interactive Model App

   Interactive Model App

You can use Panels ``.bind`` to bind your models to widgets.

.. code:: python

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

You can serve your app via

.. code:: bash

   $ panel serve 'script.py' --autoreload
   2022-01-23 15:00:31,373 Starting Bokeh server version 2.4.2 (running on Tornado 6.1)
   2022-01-23 15:00:31,387 User authentication hooks NOT provided (default user enabled)
   2022-01-23 15:00:31,389 Bokeh app running at: http://localhost:5006/script

The file can be a ``.py`` script or ``.ipynb`` notebook.

Try changing the return value of the function. Panel will magically ✨
understand how to show the objects you know and ❤️.

| This includes `Bokeh`_,
| `HoloViews`_,
| `Matplotlib`_ and
| `Plotly`_ figures.

Interactive dataframes with ``.interactive``
--------------------------------------------

.. figure:: https://user-images.githubusercontent.com/42288570/150683991-9cece6a1-3751-42d2-8256-505f5deb12be.gif
   :alt: Interactive DataFrame App

   Interactive DataFrame App

You can use `hvplot .interactive`_ to make your dataframes interactive.

\```python import panel as pn import pandas as pd import hvplot.pandas

color = “#0072B5” df = pd.DataFrame(data={“x”: [0, 1, 2, 3, 4], “y”: [0,
2, 1, 3, 4]})

pn.extension(sizing_mode=“stretch_width”, template=“fast”)

pn.pane.Markdown(“## Selection”, margin=(10,
10)).servable(area=“sidebar”) count =
pn.widgets.RadioButtonGroup(value=5, options=[3, 4, 5], name=“Count”,
button_type=“success”).servable(area=“sidebar”)

interactive_df = df.interactive().head

.. _Discourse: https://discourse.holoviz.org/
.. _Github: https://github.com/holoviz/panel
.. _Twitter: https://twitter.com/Panel_org
.. _LinkedIn: https://www.linkedin.com/company/79754450
.. _Bokeh: https://panel.holoviz.org/reference/panes/Bokeh.html#panes-gallery-bokeh
.. _HoloViews: https://panel.holoviz.org/reference/panes/HoloViews.html#panes-gallery-holoviews
.. _Matplotlib: https://panel.holoviz.org/reference/panes/Matplotlib.html#panes-gallery-matplotlib
.. _Plotly: https://panel.holoviz.org/reference/panes/Plotly.html#panes-gallery-plotly
.. _hvplot .interactive: https://hvplot.holoviz.org/user_guide/Interactive.html
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
