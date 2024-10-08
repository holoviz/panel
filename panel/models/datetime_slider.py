from bokeh.core.properties import Override
from bokeh.models.widgets.sliders import DateSlider


class DatetimeSlider(DateSlider):
    """ Slider-based datetime selection widget. """

    # explicit __init__ to support Init signatures
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    step = Override(default=3_600_000)

    format = Override(default="%d %b %Y %H:%M:%S")
