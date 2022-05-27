import holoviews as hv
import hvplot

import panel as pn

# import hvplot.pandas


def __disable_logo(plot, element):
    plot.state.toolbar.logo = None


def plot_themes():
    # format
    hv.plotting.bokeh.ElementPlot.finalize_hooks.append(__disable_logo)
    pn.widgets.DatetimeInput.format = '%d %B %Y'
    hv.plotting.bokeh.ElementPlot.bgcolor = "#fbfcfc"
    hv.plotting.bokeh.ElementPlot.gridstyle = {"grid_line_alpha": 0.6, "grid_line_dash": 'dashed'}
