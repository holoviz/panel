import pandas as pd
import param
import pytest

from panel.io.location import Location, _get_location_params
from panel.io.state import state
from panel.tests.util import serve_and_request, wait_until
from panel.util import edit_readonly


@pytest.fixture
def location():
    loc = Location()
    with edit_readonly(loc):
        loc.href = "http://localhost:5006"
        loc.hostname = "localhost"
        loc.pathname = ""
        loc.protocol = 'http'
        loc.search = ""
        loc.hash = ""
    return loc


class SyncParameterized(param.Parameterized):

    integer = param.Integer(default=None)

    string = param.String(default=None)

    dataframe = param.DataFrame(default=None)


def test_location_update_query(location):
    location.update_query(a=1)
    assert location.search == "?a=1"
    location.update_query(b='c')
    assert location.search == "?a=1&b=c"

def test_location_sync_query_init(location):
    p = SyncParameterized(integer=1, string='abc')
    location.sync(p)
    assert location.search == "?integer=1&string=abc"
    location.unsync(p)
    assert location._synced == []
    assert location.search == ""

def test_location_unsync(location):
    p = SyncParameterized(integer=1, string='abc')
    location.sync(p)
    assert location.search == "?integer=1&string=abc"
    location.unsync(p)
    assert location.search == ""
    location.update_query(integer=2, string='def')
    assert p.integer == 1
    assert p.string == "abc"
    p.integer = 3
    p.string = "ghi"
    assert location.search == "?integer=2&string=def"

def test_location_unsync_partial(location):
    p = SyncParameterized(integer=1, string='abc')
    location.sync(p)
    assert location.search == "?integer=1&string=abc"
    location.unsync(p, ['string'])
    assert location.search == "?integer=1"
    location.update_query(integer=2, string='def')
    assert p.integer == 2
    assert p.string == "abc"
    p.integer = 3
    p.string = "ghi"
    assert location.search == "?integer=3&string=def"

def test_location_sync_query_init_partial(location):
    p = SyncParameterized(integer=1, string='abc')
    location.sync(p, ['integer'])
    assert location.search == "?integer=1"
    location.unsync(p)
    assert location._synced == []

def test_location_sync_query_init_rename(location):
    p = SyncParameterized(integer=1, string='abc')
    location.sync(p, {'integer': 'int', 'string': 'str'})
    assert location.search == "?int=1&str=abc"
    location.unsync(p)
    assert location._synced == []
    assert location.search == ""

def test_location_sync_query(location):
    p = SyncParameterized()
    location.sync(p)
    p.integer = 2
    assert location.search == "?integer=2"
    location.unsync(p)
    assert location._synced == []
    assert location.search == ""

def test_location_sync_param_init(location):
    p = SyncParameterized()
    location.search = "?integer=1&string=abc"
    location.sync(p)
    assert p.integer == 1
    assert p.string == "abc"
    location.unsync(p)
    assert location._synced == []
    assert location.search == ""

def test_location_sync_on_error(location):
    p = SyncParameterized(string='abc')
    changes = []
    def on_error(change):
        changes.append(change)
    location.sync(p, on_error=on_error)
    location.search = "?integer=a&string=abc"
    assert changes == [{'integer': 'a'}]
    location.unsync(p)
    assert location._synced == []
    assert location.search == ""

def test_location_sync_param_init_partial(location):
    p = SyncParameterized()
    location.search = "?integer=1&string=abc"
    location.sync(p, ['integer'])
    assert p.integer == 1
    assert p.string is None
    location.unsync(p)
    assert location._synced == []
    assert location.search == "?string=abc"

def test_location_sync_param_init_rename(location):
    p = SyncParameterized()
    location.search = "?int=1&str=abc"
    location.sync(p, {'integer': 'int', 'string': 'str'})
    assert p.integer == 1
    assert p.string == 'abc'
    location.unsync(p)
    assert location._synced == []
    assert location.search == ""

def test_location_sync_param_update(location):
    p = SyncParameterized()
    location.sync(p)
    location.search = "?integer=1&string=abc"
    assert p.integer == 1
    assert p.string == "abc"
    location.unsync(p)
    assert location._synced == []
    assert location.search == ""

def test_server_location_populate_from_request():
    locs = []

    def app():
        loc = state.location
        locs.append(loc)
        return '# Location Test'

    request = serve_and_request(app, suffix='?foo=1')

    wait_until(lambda: len(locs) == 1)

    loc = locs[0]
    assert loc.href == request.url
    assert loc.protocol == 'http:'
    assert loc.hostname == 'localhost'
    assert loc.pathname == '/'
    assert loc.search == '?foo=1'

def test_iframe_srcdoc_location():
    Location(pathname="srcdoc")

@pytest.fixture
def dataframe():
    return pd.DataFrame({"x": [1]})

def test_location_sync_from_dataframe(location, dataframe):
    p = SyncParameterized(dataframe=dataframe)
    location.sync(p)
    assert location.search == "?dataframe=%5B%7B%22x%22%3A+1%7D%5D"

def test_location_sync_to_dataframe(location, dataframe):
    p = SyncParameterized()
    location.search = "?dataframe=%5B%7B%22x%22%3A+1%7D%5D"
    location.sync(p)
    pd.testing.assert_frame_equal(p.dataframe, dataframe)

def test_location_sync_to_dataframe_with_initial_value(location, dataframe):
    p = SyncParameterized(dataframe=pd.DataFrame({"y": [2]}))
    location.search = "?dataframe=%5B%7B%22x%22%3A+1%7D%5D"
    location.sync(p)
    pd.testing.assert_frame_equal(p.dataframe, dataframe)

@pytest.mark.parametrize(("protocol", "host", "uri", "expected"), [
    # Started with the command fastapi dev script.py on local laptop
    (
        "http", "127.0.0.1", "/panel",
        {'protocol': 'http:', 'hostname': '127.0.0.1', 'pathname': '/panel', 'href': 'http://127.0.0.1/panel'}
    ),
    # Started with the command fastapi dev script.py --root-path /some/path in VS Code terminal on JupyterHub
    (
        "http", "::ffff:172.20.0.233", "https,http://sub.domain.dk/some/path/panel",
        # I believe the below should be the result. But do not know for sure
        {"protocol": "http:", "hostname": "172.20.0.233", "pathname": "/some/path/panel", 'href': 'http://172.20.0.233/some/path/panel'}
    )
])
def test_get_location_params(protocol, host, uri, expected):
    params = _get_location_params(protocol, host, uri)
    assert params==expected
