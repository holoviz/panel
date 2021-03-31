from bokeh.core.enums import CalendarPosition
from bokeh.core.properties import (
    Bool,
    Date,
    Datetime,
    Either,
    Enum,
    List,
    Nullable,
    String,
    Tuple,
)
from bokeh.models.widgets.inputs import InputWidget


class DatetimePicker(InputWidget):
    ''' Calendar-based date picker widget.

    '''

    value = String(help="""
    The initial or picked date.
    """)

    min_date = Nullable(Either(Date, Datetime), help="""
    Optional earliest allowable date.
    """)

    max_date = Nullable(Either(Date, Datetime), help="""
    Optional latest allowable date.
    """)

    disabled_dates = List(Either(Date, Datetime, Tuple(Date, Date), Tuple(Datetime, Datetime)), default=[], help="""
    A list of dates of ``(start, end)`` date ranges to make unavailable for
    selection. All other dates will be avalable.

    .. note::
        Only one of ``disabled_dates`` and ``enabled_dates`` should be specified.
    """)

    enabled_dates = List(Either(Date, Datetime, Tuple(Date, Date), Tuple(Datetime, Datetime)), default=[], help="""
    A list of dates of ``(start, end)`` date ranges to make available for
    selection. All other dates will be unavailable.

    .. note::
        Only one of ``disabled_dates`` and ``enabled_dates`` should be specified.
    """)

    position = Enum(CalendarPosition, default="auto", help="""
    Where the calendar is rendered relative to the input when ``inline`` is False.
    """)

    inline = Bool(default=False, help="""
    Whether the calendar sholud be displayed inline.
    """)

    enable_time = Bool(default=True)

    enable_seconds = Bool(default=True)

    military_time = Bool(default=True)

    date_format = String("Y-m-d H:i:S")

    mode = String(default="single", help="""
    Should either be "single" or "range".""")
