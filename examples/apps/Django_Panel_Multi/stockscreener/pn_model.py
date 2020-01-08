# inputs
# https://stackoverflow.com/questions/55743958/panel-widgets-do-not-update-plot
import datetime as dt

import param
import panel as pn


class StockScreener(param.Parameterized):
    # interface
    df = param.DataFrame(precedence=-1)

    # Index = param.Selector()  # pn.widgets.MultiSelect()
    Rebase = param.Boolean(True, doc='Rebase')    # pn.widgets.Checkbox(name='Rebase', value=True)  # ) #
    # From = param.Selector()   # pn.widgets.DateSlider()

    def __init__(self, df, **params):
        super(StockScreener, self).__init__(**params)
        # init df
        self.df = df
        # self.start_date = dt.datetime(year=df.index[0].year, month=df.index[0].month, day=df.index[0].day)
        # self.end_date = dt.datetime(year=df.index[-1].year, month=df.index[-1].month, day=df.index[-1].day)
        self.col = list(self.df.columns)
        # init interface
        # self.Index = param.ListSelector(name='Index', value=self.col[0:5])
        # self.From = param.Selector()
        # self.Index = pn.widgets.MultiSelect(name='Index', value=self.col[0:5], options=self.col,
        #                                     size=min(10, len(self.col)))
        # self.From = pn.widgets.DateSlider(name='From', start=self.start_date, end=self.end_date,value=self.start_date)
        #

    @param.depends('Rebase', watch=True)
    def update_plot(self, **kwargs):
        unds = self.col[0:5]  # list(self.Index.value)
        pos = 1000  # self.df.index.get_loc(self.From.value, method='bfill')
        dfp = self.df.iloc[pos:][unds]

        if self.Rebase:
            dfp = 100 * dfp / dfp.iloc[0]
        return dfp.hvplot(grid=True, colormap='Paired')

    def widgets(self, **kwargs):
        params = pn.Param(self.param, widgets={
            # 'Index': pn.widgets.MultiSelect,
            'Rebase': pn.widgets.Checkbox,
            # 'From': pn.widgets.DateSlider,
        })

        return params


