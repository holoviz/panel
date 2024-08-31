from bokeh.models import TimePicker as BkTimePicker


class TimePicker(BkTimePicker):
    """
    A custom Panel version of the Bokeh TimePicker model which fixes timezones.
    """
