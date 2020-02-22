"""In this module we test the Bokeh Location Model"""

import pytest
from panel.widgets.location import Location
import panel as pn
from panel.models.location import Location as BKLocation


def test_constructor():
    # When
    actual = Location()
    # Then
    assert actual.href == ""
    assert actual.hostname == ""
    assert actual.pathname == ""
    assert actual.protocol == ""
    assert actual.port == ""
    assert actual.search == ""
    assert actual.hash_ == ""
    assert actual.refresh == True


def test_constructor_with_href():
    # Given
    href = "https://panel.holoviz.org/user_guide/Interact.html:80?color=blue#interact"
    # When
    actual = Location(
        href="https://panel.holoviz.org/user_guide/Interact.html:80?color=blue#interact"
    )
    # Then
    assert actual.href == href
    assert actual.hostname == ""
    assert actual.pathname == ""
    assert actual.protocol == ""
    assert actual.port == ""
    assert actual.search == ""
    assert actual.hash_ == ""
    assert actual.refresh == True


def test_manual():
    location = Location()
    parameters = [
        "href",
        "hostname",
        "pathname",
        "protocol",
        "port",
        "search",
        "hash_",
        "refresh",
    ]
    bkmodel = pn.pane.Bokeh(BKLocation())
    app = pn.Column(bkmodel, pn.Param(location, parameters=parameters))
    return app


if __name__.startswith("bk"):
    import ptvsd

    ptvsd.enable_attach(address=("localhost", 5678))
    ptvsd.wait_for_attach()  # Only include this line if you always wan't to attach the debugger
    test_manual().servable()
