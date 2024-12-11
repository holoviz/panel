from panel.widgets import Calendar


def test_calendar_value_snake_case():
    calendar = Calendar(value=[{"start": "2020-01-01", "all_day": True}])
    assert calendar.value == [{"start": "2020-01-01", "allDay": True}]

    calendar.add_event(start="2020-01-02", start_recur="2020-01-03")
    assert calendar.value == [
        {"start": "2020-01-01", "allDay": True},
        {"start": "2020-01-02", "startRecur": "2020-01-03", "title": "(no title)"},
    ]


def test_calendar_value_snake_case_disabled():
    calendar = Calendar(
        value=[{"start": "2020-01-01", "all_day": True}],
        event_keys_auto_camel_case=False,
    )
    assert calendar.value == [{"start": "2020-01-01", "all_day": True}]

    calendar.add_event(start="2020-01-02", start_recur="2020-01-03")
    assert calendar.value == [
        {"start": "2020-01-01", "all_day": True},
        {"start": "2020-01-02", "start_recur": "2020-01-03", "title": "(no title)"},
    ]


def test_calendar_value_camel_case():
    calendar = Calendar(value=[{"start": "2020-01-01", "allDay": True}])
    assert calendar.value == [{"start": "2020-01-01", "allDay": True}]


def test_calendar_add_event():
    calendar = Calendar()
    calendar.add_event(start="2020-01-01", end="2020-01-02", title="event")
    assert calendar.value == [
        {"start": "2020-01-01", "end": "2020-01-02", "title": "event"}
    ]

    calendar.add_event(
        start="2020-01-03", end="2020-01-04", title="event2", display="background"
    )
    assert calendar.value == [
        {"start": "2020-01-01", "end": "2020-01-02", "title": "event"},
        {
            "start": "2020-01-03",
            "end": "2020-01-04",
            "title": "event2",
            "display": "background",
        },
    ]


def test_calendar_add_event_camel_case_precedence():
    calendar = Calendar()
    calendar.add_event(start="2020-01-01", end="2020-01-02", allDay=True, all_day=False)
    assert calendar.value == [
        {
            "start": "2020-01-01",
            "end": "2020-01-02",
            'title': '(no title)',
            "allDay": True,
        }  # camelCase takes precedence
    ]
