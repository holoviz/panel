import datetime

import hvplot.pandas
import pandas as pd
import param

import panel as pn

pn.extension()

URL = (
    "https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?network=DE__ASOS&stations={station}&"
    "year1={yesterday.year}&month1={yesterday.month}&day1={yesterday.day}&"
    "year2={today.year}&month2={today.month}&day2={today.day}"
    "&var=max_temp_f&na=blank&format=csv"
)


class WeatherApp(param.Parameterized):
    station = param.Selector(default="EDDB", objects=["EDDB", "EDDM", "EDDH"])
    days = param.Integer(default=7, bounds=(1, 14))
    today = param.Date(default=datetime.date.today(), readonly=True)

    def __init__(self, **params):
        super().__init__(**params)
        pn.state.location.sync(self)

    @param.depends("station", "days")
    def _display_data(self):
        yesterday = self.today - datetime.timedelta(days=self.days)
        url = URL.format(station=self.station, today=self.today, yesterday=yesterday)
        df = pd.read_csv(url, index_col="day")
        return pn.Tabs(("Plot", df.hvplot(title=self.station)), ("Table", df))

    def panel(self):
        return pn.Row(
            # throttle
            pn.Param(
                self.param,
                parameters=["station", "days"],
                widgets={"days": {"throttled": True}},
            ),
            self._display_data,
        )


weather_app = WeatherApp()
weather_app.panel().servable()
