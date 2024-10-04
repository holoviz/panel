import datetime
from pathlib import Path

import param

from panel.custom import JSComponent

THIS_DIR = Path(__file__).parent
MODELS_DIR = THIS_DIR.parent / "models"


class Calendar(JSComponent):

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

    current_date = param.Date(
        default=None, doc="The current date of the calendar view."
    )

    date_alignment = param.String(
        default="month", doc="Determines how certain views should be initially aligned."
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
        doc="Defines the buttons and title at the top of the calendar.",
    )

    initial_date = param.Date(
        default=None,
        doc="The initial date the calendar should display when first loaded.",
    )

    initial_view = param.Selector(
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
        doc="The initial view when the calendar loads.",
    )

    multi_month_max_columns = param.Integer(
        default=1,
        doc="Determines the maximum number of columns in the multi-month view.",
    )

    now_indicator = param.Boolean(
        default=False, doc="Whether to display an indicator for the current time."
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

    def next(self):
        self._send_msg({"type": "next"})

    def prev(self):
        self._send_msg({"type": "prev"})

    def prev_year(self):
        self._send_msg({"type": "prevYear"})

    def next_year(self):
        self._send_msg({"type": "nextYear"})

    def today(self):
        self._send_msg({"type": "today"})

    def go_to_date(self, date):
        self._send_msg({"type": "gotoDate", "date": date.isoformat()})

    def increment_date(self, increment):
        self._send_msg({"type": "incrementDate", "increment": increment})

    def update_size(self):
        self._send_msg({"type": "updateSize"})

    def _handle_msg(self, msg):
        if "current_date" in msg:
            self.current_date = datetime.datetime.strptime(
                msg["current_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        else:
            raise NotImplementedError(f"Unhandled message: {msg}")

    def add_event(
        self,
        start: str,
        end: str | None = None,
        title: str = "(no title)",
        all_day: bool = False,
        **kwargs,
    ):
        event = {
            "start": start,
            "end": end,
            "title": title,
            "allDay": all_day,
            **kwargs,
        }
        self.value.append(event)

    def _update_option(self, event):
        def to_camel_case(string):
            return "".join(
                word.capitalize() if i else word
                for i, word in enumerate(string.split("_"))
            )
        key = to_camel_case(event.name)
        self._send_msg(
            {"type": "updateOption", "key": key, "value": event.new}
        )
