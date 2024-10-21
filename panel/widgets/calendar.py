import datetime

from pathlib import Path

import param

from panel.custom import JSComponent

THIS_DIR = Path(__file__).parent
MODELS_DIR = THIS_DIR.parent / "models"
VIEW_DEFAULT_INCREMENTS = {
    "dayGridMonth": {"days": 1},
    "dayGridWeek": {"weeks": 1},
    "dayGridDay": {"days": 1},
    "timeGridWeek": {"weeks": 1},
    "timeGridDay": {"days": 1},
    "listWeek": {"weeks": 1},
    "listMonth": {"months": 1},
    "listYear": {"years": 1},
    "multiMonthYear": {"years": 1},
}


class Calendar(JSComponent):
    """
    The Calendar widget is a wrapper around the FullCalendar library.
    See https://fullcalendar.io/docs for more information on the parameters.

    Reference: https://panel.holoviz.org/reference/widgets/Calendar.html

    :Example:

    >>> pn.widgets.Calendar(value=[{"date": "2024-10-01", "type": "event"}])
    """

    aspect_ratio = param.Number(
        default=None, doc="Sets the width-to-height aspect ratio of the calendar."
    )

    business_hours = param.Dict(
        default={}, doc="Emphasizes certain time slots on the calendar."
    )

    button_icons = param.Dict(
        default={},
        doc="Icons that will be displayed in buttons of the header/footer toolbar.",
    )

    button_text = param.Dict(
        default={},
        doc="Text that will be displayed on buttons of the header/footer toolbar.",
    )

    content_height = param.String(
        default=None, doc="Sets the height of the view area of the calendar."
    )

    # using String instead of Date because fullcalendar supports fuzzy dates
    current_date = param.String(
        default=None,
        constant=True,
        doc="The onload or current date of the calendar view. Use go_to_date() to change the date.",
    )

    current_view = param.Selector(
        default="dayGridMonth",
        objects=[
            "dayGridMonth",
            "dayGridWeek",
            "dayGridDay",
            "timeGridWeek",
            "timeGridDay",
            "listWeek",
            "listMonth",
            "listYear",
            "multiMonthYear",
        ],
        constant=True,
        doc="The onload or current view of the calendar. Use change_view() to change the view.",
    )

    date_alignment = param.String(
        default=None, doc="Determines how certain views should be initially aligned."
    )

    date_increment = param.String(
        default=None,
        doc="The duration to move forward/backward when prev/next is clicked.",
    )

    expand_rows = param.Boolean(
        default=False,
        doc="If the rows of a given view don't take up the entire height, they will expand to fit.",
    )

    footer_toolbar = param.Dict(
        default={}, doc="Defines the buttons and title at the bottom of the calendar."
    )

    handle_window_resize = param.Boolean(
        default=True,
        doc="Whether to automatically resize the calendar when the browser window resizes.",
    )

    header_toolbar = param.Dict(
        default={
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
        },
        doc="Defines the buttons and title at the top of the calendar."
    )

    multi_month_max_columns = param.Integer(
        default=1,
        doc="Determines the maximum number of columns in the multi-month view.",
    )

    nav_links = param.Boolean(
        default=True,
        doc="Turns various datetime text into clickable links that the user can use for navigation.",
    )

    now_indicator = param.Boolean(
        default=True, doc="Whether to display an indicator for the current time."
    )

    show_non_current_dates = param.Boolean(
        default=False,
        doc="Whether to display dates in the current view that don't belong to the current month.",
    )

    sticky_footer_scrollbar = param.Boolean(
        default=True,
        doc="Whether to fix the view's horizontal scrollbar to the bottom of the viewport while scrolling.",
    )

    sticky_header_dates = param.String(
        default=None,
        doc="Whether to fix the date-headers at the top of the calendar to the viewport while scrolling.",
    )

    title_format = param.String(
        default=None,
        doc="Determines the text that will be displayed in the header toolbar's title.",
    )

    title_range_separator = param.String(
        default=" to ",
        doc="Determines the separator text when formatting the date range in the toolbar title.",
    )

    valid_range = param.DateRange(
        default=None,
        bounds=(None, None),
        doc="Limits the range of time the calendar will display.",
    )

    value = param.List(
        default=[], item_type=dict, doc="List of events to display on the calendar."
    )

    window_resize_delay = param.Integer(
        default=100,
        doc="The time the calendar will wait to adjust its size after a window resize occurs, in milliseconds.",
    )

    _esm = MODELS_DIR / "fullcalendar.js"

    _syncing = param.Boolean(default=False)

    _importmap = {
        "imports": {
            "@fullcalendar/core": "https://cdn.skypack.dev/@fullcalendar/core@6.1.15",
            "@fullcalendar/daygrid": "https://cdn.skypack.dev/@fullcalendar/daygrid@6.1.15",
            "@fullcalendar/timegrid": "https://cdn.skypack.dev/@fullcalendar/timegrid@6.1.15",
            "@fullcalendar/list": "https://cdn.skypack.dev/@fullcalendar/list@6.1.15",
            "@fullcalendar/multimonth": "https://cdn.skypack.dev/@fullcalendar/multimonth@6.1.15",
        }
    }

    def __init__(self, **params):
        super().__init__(**params)
        self.param.watch(
            self._update_option,
            [
                "aspect_ratio",
                "business_hours",
                "button_icons",
                "button_text",
                "content_height",
                "date_alignment",
                "date_increment",
                "expand_rows",
                "footer_toolbar",
                "handle_window_resize",
                "header_toolbar",
                "multi_month_max_columns",
                "nav_links",
                "now_indicator",
                "show_non_current_dates",
                "sticky_footer_scrollbar",
                "sticky_header_dates",
                "title_format",
                "title_range_separator",
                "valid_range",
                "value",
                "window_resize_delay",
            ],
        )

    def click_next(self) -> None:
        """
        Click the next button through the calendar's UI.
        """
        self._send_msg({"type": "next"})

    def click_prev(self) -> None:
        """
        Click the previous button through the calendar's UI.
        """
        self._send_msg({"type": "prev"})

    def click_prev_year(self) -> None:
        """
        Click the previous year button through the calendar's UI.
        """
        self._send_msg({"type": "prevYear"})

    def click_next_year(self) -> None:
        """
        Click the next year button through the calendar's UI.
        """
        self._send_msg({"type": "nextYear"})

    def click_today(self) -> None:
        """
        Click the today button through the calendar's UI.
        """
        self._send_msg({"type": "today"})

    def change_view(
        self,
        view: str,
        date: str | datetime.datetime | datetime.date | int | None = None,
    ) -> None:
        """
        Change the current view of the calendar, and optionally go to a specific date.

        Args:
            view: The view to change to.
                Options: "dayGridMonth", "dayGridWeek", "dayGridDay", "timeGridWeek", "timeGridDay",
                "listWeek", "listMonth", "listYear", "multiMonthYear".
            date: The date to go to after changing the view; if None, the current date will be used.
                Supports ISO 8601 date strings, datetime/date objects, and int in milliseconds.
        """
        self._send_msg({"type": "changeView", "view": view, "date": date})

    def go_to_date(self, date: str | datetime.datetime | datetime.date | int) -> None:
        """
        Go to a specific date on the calendar.

        Args:
            date: The date to go to.
                Supports ISO 8601 date strings, datetime/date objects, and int in milliseconds.
        """
        self._send_msg({"type": "gotoDate", "date": date})

    def increment_date(
        self, increment: str | datetime.timedelta | int | dict | None = None
    ) -> None:
        """
        Increment the current date by a specific amount.

        Args:
            increment: The amount to increment the current date by.
                Supports a string in the format hh:mm:ss.sss, hh:mm:sss or hh:mm, an int in milliseconds,
                datetime.timedelta objects, or a dict with any of the following keys:
                    year, years, month, months, day, days, minute, minutes, second,
                    seconds, millisecond, milliseconds, ms.
                If not provided, the date_increment parameter will be used.
                If date_increment is not set, the default increment for the current view will be used:
                    dayGridMonth: {"days": 1}
                    dayGridWeek: {"weeks": 1}
                    dayGridDay: {"days": 1}
                    timeGridWeek: {"weeks": 1}
                    timeGridDay: {"days": 1}
                    listWeek: {"weeks": 1}
                    listMonth: {"months": 1}
                    listYear: {"years": 1}
                    multiMonthYear: {"years": 1}
        """

        if increment is None and self.date_increment is None:
            increment = VIEW_DEFAULT_INCREMENTS[self.current_view]
        self._send_msg({"type": "incrementDate", "increment": increment})

    def add_event(
        self,
        start: str | datetime.datetime | datetime.date | int,
        end: str | datetime.datetime | datetime.date | int | None = None,
        title: str = "(no title)",
        all_day: bool = False,
        **kwargs,
    ) -> None:
        """
        Add an event to the calendar.

        Args:
            start: The start date of the event.
                Supports ISO 8601 date strings, datetime/date objects, and int in milliseconds.
            end: The end date of the event.
                Supports ISO 8601 date strings, datetime/date objects, and int in milliseconds.
                If None, the event will be all-day.
            title: The title of the event.
            all_day: Whether the event is an all-day event.
            **kwargs: Additional properties to set on the event
        """

        event = {
            "start": start,
            "end": end,
            "title": title,
            "allDay": all_day,
            **kwargs,
        }
        self.value.append(event)

    def _handle_msg(self, msg):
        if "current_date" in msg:
            with param.edit_constant(self):
                self.current_date = msg["current_date"]
        elif "current_view" in msg:
            with param.edit_constant(self):
                self.current_view = msg["current_view"]
        else:
            raise NotImplementedError(f"Unhandled message: {msg}")

    def _update_option(self, event):
        def to_camel_case(string):
            return "".join(
                word.capitalize() if i else word
                for i, word in enumerate(string.split("_"))
            )

        key = to_camel_case(event.name)
        self._send_msg({"type": "updateOption", "key": key, "value": event.new})
