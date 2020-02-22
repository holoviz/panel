from panel.widgets.location import Location

HREF = "https://panel.holoviz.org/user_guide/Interact.html:80?color=blue#interact"
HOSTNAME = "panel.holoviz.org"
PATHNAME = "user_guide/Interact.html"
PROTOCOL = "https"
PORT = "80"
SEARCH = "?color=blue"
HASH_ = "#interact"


def test_location(document, comm):
    # given

    # When
    location = Location(href=HREF, name="Location")

    widget = location.get_root(document, comm=comm)

    assert isinstance(widget, Location._widget_type)
    assert widget.href == HREF
    # assert widget.title == 'Slider'
    # assert widget.step == 0.1
    # assert widget.start == 0.1
    # assert widget.end == 0.5
    # assert widget.value == 0.4

    # slider._comm_change({'value': 0.2})
    # assert slider.value == 0.2

    # slider.value = 0.3
    # assert widget.value == 0.3
