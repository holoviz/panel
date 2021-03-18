from bokeh.models.widgets.inputs import DatePicker
from bokeh.core.properties import (
    Bool,
    Datetime,
    Either,
    String,
    Override,
)


class DatetimePicker(DatePicker):
    ''' Calendar-based date picker widget.

    '''

    value = Either(Datetime, String, help="""
    The initial or picked date.
    """)

    enable_time = Bool(default=False)

    enable_seconds = Bool(default=False)

    military_time = Bool(default=False)
