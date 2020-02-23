"""In this module we test the Bokeh Location Model"""

import pytest
import panel as pn
from panel.models.location import Location


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
    bkmodel = pn.pane.Bokeh(Location())
    app = pn.Column(bkmodel)
    return app


if __name__.startswith("bk"):
    test_manual().servable()
