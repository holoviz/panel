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
    assert actual.hash == ""
    assert actual.reload == True


def test_constructor_with__href():
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
    assert actual.hash == ""
    assert actual.reload == True
