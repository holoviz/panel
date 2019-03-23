from collections import OrderedDict

from bokeh.models import Div

from panel.io.notebook import render_mimebundle
from panel.pane import PaneBase
from panel.util import get_method_owner, abbreviated_repr


def test_get_method_owner_class():
    assert get_method_owner(PaneBase.get_pane_type) is PaneBase


def test_get_method_owner_instance():
    div = Div()
    assert get_method_owner(div.update) is div


def test_render_mimebundle(document, comm):
    div = Div()
    data, metadata = render_mimebundle(div, document, comm)

    assert metadata == {'application/vnd.holoviews_exec.v0+json': {'id': div.ref['id']}}
    assert 'application/vnd.holoviews_exec.v0+json' in data
    assert 'text/html' in data
    assert data['application/vnd.holoviews_exec.v0+json'] == ''


def test_abbreviated_repr_dict():
    assert abbreviated_repr({'key': 'some really, really long string'}) == "{'key': 'some really, ...}"


def test_abbreviated_repr_list():
    assert abbreviated_repr(['some really, really long string']) == "['some really, ...]"


def test_abbreviated_repr_ordereddict():
    assert (abbreviated_repr(OrderedDict([('key', 'some really, really long string')]))
            == "OrderedDict([('key', ...])")
