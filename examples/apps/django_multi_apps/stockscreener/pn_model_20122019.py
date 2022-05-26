# inputs
# https://stackoverflow.com/questions/55743958/panel-widgets-do-not-update-plot
import datetime as dt

import holoviews as hv
import hvplot
import hvplot.pandas
import param

import panel as pn

# # initialization
# pn.widgets.DatetimeInput.format = '%d %B %Y'
# hv.plotting.bokeh.ElementPlot.bgcolor = "#fbfcfc"
# hv.plotting.bokeh.ElementPlot.gridstyle = {"grid_line_alpha": 0.6, "grid_line_dash": 'dashed'}
# # hv.plotting.bokeh.ElementPlot.gridstyle={"grid_line_alpha": 1.0}
#
#
#
# def __disable_logo(plot, element):
#     plot.state.toolbar.logo = None
#
#
# hv.plotting.bokeh.ElementPlot.finalize_hooks.append(__disable_logo)
#
# css = '''
# .background-grey {
#   background: bl#fbfcfc;
#   border-radius: 5px;
#   border: 1px black solid;
# }
# '''
# pn.extension(raw_css=[css])


class StockScreener(param.Parameterized):
    # interface
    df = param.DataFrame(precedence=-1)
    Index = pn.widgets.MultiSelect()
    Rebase = pn.widgets.Checkbox(name='Rebase', value=True)
    From = pn.widgets.DateSlider()

    def __init__(self, df, **params):
        super(StockScreener, self).__init__(**params)
        # init df
        self.df = df
        self.start_date = dt.datetime(year=df.index[0].year, month=df.index[0].month, day=df.index[0].day)
        self.end_date = dt.datetime(year=df.index[-1].year, month=df.index[-1].month, day=df.index[-1].day)
        self.col = list(self.df.columns)
        # init interface
        self.Index = pn.widgets.MultiSelect(name='Index', value=self.col[0:5], options=self.col,
                                            size=min(10, len(self.col)))
        self.From = pn.widgets.DateSlider(name='From', start=self.start_date, end=self.end_date, value=self.start_date)

    @param.depends('Index', 'Rebase', 'From.value', watch=True)
    def update_plot(self, **kwargs):
        unds = list(self.Index.value)
        pos = self.df.index.get_loc(self.From.value, method='bfill')
        dfp = self.df.iloc[pos:][unds]
        if self.Rebase.value:
            dfp = 100 * dfp / dfp.iloc[0]
        return dfp.hvplot(grid=True, colormap='Paired')
