from bokeh.core.properties import Override
from bokeh.models.widgets.sliders import DateSlider


class DatetimeSlider(DateSlider):
    """ Slider-based datetime selection widget. """

    step = Override(default=60)

    format = Override(default="%d %b %Y %H:%M:%S")
