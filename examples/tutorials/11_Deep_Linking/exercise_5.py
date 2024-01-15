import hvplot.pandas
import pandas as pd
import param

from bokeh.sampledata import stocks

import panel as pn

pn.extension()

TICKERS = list(stocks.__all__)


class StockExplorer(param.Parameterized):
    ticker = param.ListSelector(default=TICKERS[:1], objects=TICKERS)
    date_range = param.DateRange()

    def __init__(self, **params):
        super().__init__(**params)
        df = pd.concat(
            pd.DataFrame(getattr(stocks, ticker)).assign(**{"ticker": ticker})
            for ticker in TICKERS
        )
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        self._df = df
        self.date_range = (df.index[0], df.index[-1])
        self.param["date_range"].bounds = (df.index[0], df.index[-1])

    @param.depends("ticker", "date_range")
    def update_plot(self):
        df = self._df.loc[self._df["ticker"].isin(self.ticker)]
        return df.hvplot(
            y="close",
            by="ticker",
            responsive=True,
            xlim=self.date_range,
        ).opts(legend_position="top_left")

    def panel(self):
        widget_col = pn.Param(
            self,
            widgets={
                "ticker": {
                    "type": pn.widgets.MultiChoice,
                },
                "date_range": {
                    "type": pn.widgets.DateRangeSlider,
                },
            },
            show_name=False,
        )
        return pn.Row(widget_col, self.update_plot)


stock_explorer = StockExplorer()
panel = stock_explorer.panel()
panel.servable()
