import datetime as dt

import panel as pn
import param
import hvplot.pandas



class StockScreener(param.Parameterized):

    df = param.DataFrame(precedence=-1)

    index = param.ListSelector()

    normalize = param.Boolean(default=True)

    start = param.Date()

    def __init__(self, df, **params):
        start = dt.date(year=df.index[0].year, month=df.index[0].month, day=df.index[0].day)
        end = dt.date(year=df.index[-1].year, month=df.index[-1].month, day=df.index[-1].day)
        super(StockScreener, self).__init__(df=df, start=start, **params)
        self.param.start.bounds = (start, end)
        columns = list(self.df.columns)
        self.param.index.objects = columns
        self.index = columns[:5]

    @param.depends('index', 'normalize', 'start')
    def update_plot(self):
        pos = self.df.index.get_loc(self.start, method='bfill')
        dfp = self.df.iloc[pos:][self.index]
        if self.normalize:
            dfp = 100 * dfp / dfp.iloc[0]
        return dfp.hvplot(group_label='Ticker')

    def panel(self):
        return pn.Row(
            pn.panel(self.param, widgets={'start': pn.widgets.DateSlider}),
            self.update_plot
        )
