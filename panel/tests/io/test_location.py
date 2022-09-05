import param
import pytest

from panel.io.location import Location
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
