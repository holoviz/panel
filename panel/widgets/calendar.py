from pathlib import Path

import param

from panel.custom import JSComponent

THIS_DIR = Path(__file__).parent
MODELS_DIR = THIS_DIR.parent / "models"


class Calendar(JSComponent):

    value = param.List(default=[], item_type=dict)

    initial_view = param.Selector(
        default="dayGridMonth", objects=["dayGridMonth", "timeGridWeek", "timeGridDay"]
    )

    selectable = param.Boolean(default=True)

    editable = param.Boolean(default=True)

    event_limit = param.Integer(default=3)  # Limit for event rendering

    _esm = MODELS_DIR / "fullcalendar.ts"

    _importmap = {
        "imports": {
            "@fullcalendar/core": "https://cdn.skypack.dev/@fullcalendar/core@6.1.15",
            "@fullcalendar/daygrid": "https://cdn.skypack.dev/@fullcalendar/daygrid@6.1.15",
            "@fullcalendar/timegrid": "https://cdn.skypack.dev/@fullcalendar/timegrid@6.1.15",
        }
    }

    def add_event(self, start: str, end: str | None = None, title: str = "(no title)", all_day: bool = False, **kwargs):
        self.value.append({"start": start, "end": end, "title": title, **kwargs})
