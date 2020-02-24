import panel as pn
from panel.widgets.location import Location
import pytest

HREF = "https://panel.holoviz.org/user_guide/Interact.html:80?color=blue#interact"
HOSTNAME = "panel.holoviz.org"
PATHNAME = "user_guide/Interact.html"
PROTOCOL = "https"
PORT = "80"
SEARCH = "?color=blue"
HASH_ = "#interact"


@pytest.fixture
def href():
    return "https://panel.holoviz.org/user_guide/Interact.html:5006?color=blue#interact"


@pytest.fixture
def hostname():
    return "panel.holoviz.org"


@pytest.fixture
def pathname():
    return "user_guide/Interact.html"


@pytest.fixture
def protocol():
    return "https"


@pytest.fixture
def port():
    return "5006"


@pytest.fixture
def search():
    return "?color=blue"


@pytest.fixture
def hash_():
    return "#interact"


@pytest.fixture
def refresh():
    return False


def test_constructor():
    # When
    actual = Location()
    # Then/pyv
    assert actual.href == ""
    assert actual.hostname == ""
    assert actual.pathname == ""
    assert actual.protocol == ""
    assert actual.port == ""
    assert actual.search == ""
    assert actual.hash_ == ""
    assert actual.refresh == False


def test_href_is_readonly(href):
    # When/ Then
    with pytest.raises(TypeError):
        Location(href=href)


def test_hostname_is_readonly(hostname):
    # When/ Then
    with pytest.raises(TypeError):
        Location(hostname=hostname)


def test_protocol_is_readonly(protocol):
    # When/ Then
    with pytest.raises(TypeError):
        Location(protocol=protocol)


def test_port_is_readonly(port):
    # When/ Then
    with pytest.raises(TypeError):
        Location(port=port)


def test_attributes_are_not_readonly(pathname, search, hash_, refresh):
    # When
    location = Location(pathname=pathname, search=search, hash_=hash_, refresh=refresh)
    # Then
    assert location.pathname == pathname
    assert location.search == search
    assert location.hash_ == hash_
    assert location.refresh == refresh


@pytest.mark.parametrize(["invalid"], [("/",), ("/app",), ("/app/",), ("app/",),])
def test_pathname_raises_valueerror_if_string_invalid(invalid):
    "The pathname should be '' or (not start or end with '/')"
    with pytest.raises(ValueError):
        Location(search="a=b")


def test_search_raises_valueerror_if_string_invalid():
    "The search string should be '' or start with '?'"
    with pytest.raises(ValueError):
        Location(search="a=b")


def test_hash_raises_valueerror_if_string_invalid():
    "The hash string should be '' or start with '#'"
    # When/ Then
    with pytest.raises(ValueError):
        Location(hash="section2")


def test_location_comm(document, comm, pathname, search, hash_, refresh):
    # Given
    location = Location()

    # When
    widget = location.get_root(document, comm=comm)

    # Then
    assert isinstance(widget, Location._widget_type)

    location._comm_change({"pathname": pathname})
    assert location.pathname == pathname

    location._comm_change({"search": search})
    assert location.search == search

    location._comm_change({"hash_": hash_})
    assert location.hash_ == hash_

    location._comm_change({"refresh": refresh})
    assert location.refresh == refresh


if __name__.startswith("bk"):
    pn.config.sizing_mode = "stretch_width"
    location = Location(refresh=False)
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
    pn.Column(location, pn.Param(location, parameters=parameters)).servable()
