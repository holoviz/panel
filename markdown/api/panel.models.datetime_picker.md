# panel.models.datetime_picker module

class panel.models.datetime_picker.DatetimePicker(\*args: Any, id: ID \| None = None, **kwargs: Any)
Bases: `InputWidget`

Calendar-based date picker widget.

Attributes:
**allow_input**
Enable manual date input in the widget.

**date_format**

**disabled_dates**
A list of dates of
`(start,`` ``end)`
date ranges to make unavailable for selection. All other dates will be
available.

Note

Only one of `disabled_dates` and
`enabled_dates` should be specified.

**enable_seconds**

**enable_time**

**enabled_dates**
A list of dates of
`(start,`` ``end)`
date ranges to make available for selection. All other dates will be
unavailable.

Note

Only one of `disabled_dates` and
`enabled_dates` should be specified.

**inline**
Whether the calendar sholud be displayed inline.

**max_date**
Optional latest allowable date.

**military_time**

**min_date**
Optional earliest allowable date.

**mode**
Should either be “single” or “range”.

**position**
Where the calendar is rendered relative to the input when
`inline` is False.

**value**
The initial or picked date.

allow_input
Enable manual date input in the widget.

disabled_dates
A list of dates of
`(start,`` ``end)`
date ranges to make unavailable for selection. All other dates will be
available.

Note

Only one of `disabled_dates` and
`enabled_dates` should be specified.

enabled_dates
A list of dates of
`(start,`` ``end)`
date ranges to make available for selection. All other dates will be
unavailable.

Note

Only one of `disabled_dates` and
`enabled_dates` should be specified.

inline
Whether the calendar sholud be displayed inline.

max_date
Optional latest allowable date.

min_date
Optional earliest allowable date.

mode
Should either be “single” or “range”.

position
Where the calendar is rendered relative to the input when
`inline` is False.

value
The initial or picked date.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
