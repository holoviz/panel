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

def test_location_sync_query_init_partial(location):
    p = SyncParameterized(integer=1, string='abc')
    location.sync(p, ['integer'])
    assert location.search == "?integer=1"

def test_location_sync_query_init_rename(location):
    p = SyncParameterized(integer=1, string='abc')
    location.sync(p, {'integer': 'int', 'string': 'str'})
    assert location.search == "?int=1&str=abc"

def test_location_sync_query(location):
    p = SyncParameterized()
    location.sync(p)
    p.integer = 2
    assert location.search == "?integer=2"

def test_location_sync_param_init(location):
    p = SyncParameterized()
    location.search = "?integer=1&string=abc"
    location.sync(p)
    assert p.integer == 1
    assert p.string == "abc"

def test_location_sync_param_init_partial(location):
    p = SyncParameterized()
    location.search = "?integer=1&string=abc"
    location.sync(p, ['integer'])
    assert p.integer == 1
    assert p.string is None

def test_location_sync_param_init_rename(location):
    p = SyncParameterized()
    location.search = "?int=1&str=abc"
    location.sync(p, {'integer': 'int', 'string': 'str'})
    assert p.integer == 1
    assert p.string == 'abc'

def test_location_sync_param_update(location):
    p = SyncParameterized()
    location.sync(p)
    location.search = "?integer=1&string=abc"
    assert p.integer == 1
    assert p.string == "abc"
