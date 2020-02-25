import panel as pn
from panel.widgets.location import Location
import pytest


@pytest.fixture
def href():
    return "https://panel.holoviz.org/user_guide/Interact.html:5006?color=blue#interact"


@pytest.fixture
def hostname():
    return "panel.holoviz.org"


@pytest.fixture
def pathname():
    return "/user_guide/Interact.html"


@pytest.fixture
def protocol():
    return "https:"


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
def reload():
    return True


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
    assert actual.reload == True


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


def test_attributes_are_not_readonly(pathname, search, hash_, reload):
    # When
    location = Location(pathname=pathname, search=search, hash_=hash_, reload=reload)
    # Then
    assert location.pathname == pathname
    assert location.search == search
    assert location.hash_ == hash_
    assert location.reload == reload


@pytest.mark.parametrize(["invalid"], [("app",), ("app/",),])
def test_pathname_raises_valueerror_if_string_invalid(invalid):
    "The pathname should be '' or (not start or end with '/')"
    with pytest.raises(ValueError):
        Location(pathname=invalid)


def test_search_raises_valueerror_if_string_invalid():
    "The search string should be '' or start with '?'"
    with pytest.raises(ValueError):
        Location(search="a=b")


def test_hash_raises_valueerror_if_string_invalid():
    "The hash string should be '' or start with '#'"
    # When/ Then
    with pytest.raises(ValueError):
        Location(hash_="section2")


def test_readonly_workaround_works(href, hostname, protocol, port):
    # Given
    location = Location()
    # When
    location._href = href
    location._hostname = hostname
    location._protocol = protocol
    location._port = port
    # Then
    location.href == href
    location.hostname == hostname
    location.protocol == protocol
    location.port == port


def test_location_comm(document, comm, pathname, search, hash_, reload):
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

    location._comm_change({"reload": reload})
    assert location.reload == reload


if __name__.startswith("bk"):
    pn.config.sizing_mode = "stretch_width"
    location = Location(reload=False)
    parameters = [
        "href",
        "hostname",
        "pathname",
        "protocol",
        "port",
        "search",
        "hash_",
        "reload",
    ]
    pn.Column(location, pn.Param(location, parameters=parameters)).servable()
