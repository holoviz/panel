from django.conf import settings
import datetime as dt

import panel as pn
import param
import holoviews as hv
import hvplot
import hvplot.pandas


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

    @param.depends('Index.value', 'Rebase.value', 'From.value', watch=True)
    def update_plot(self, **kwargs):
        unds = list(self.Index.value)
        pos = self.df.index.get_loc(self.From.value, method='bfill')
        dfp = self.df.iloc[pos:][unds]
        if self.Rebase.value:
            dfp = 100 * dfp / dfp.iloc[0]

        # legend positions
        # ['top_right', 'top_left', 'bottom_left', 'bottom_right']
        # ['right', 'left', 'top', 'bottom']

        return dfp.hvplot(value_label="Level", colormap=settings.COLOR_MAP)  # dfp.hvplot().opts(legend_position='top_left', responsive=True) # grid=True, colormap='Paired')
