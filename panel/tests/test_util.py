from collections import OrderedDict

from bokeh.models import Div

from panel.pane import PaneBase
from panel.util import (
    render_mimebundle, default_label_formatter, get_method_owner,
    abbreviated_repr
)


def test_get_method_owner_class():
    assert get_method_owner(PaneBase.get_pane_type) is PaneBase


def test_get_method_owner_instance():
    div = Div()
    assert get_method_owner(div.update) is div


def test_render_mimebundle(document, comm):
    div = Div()
    data, metadata = render_mimebundle(div, document, comm)

    assert metadata == {'application/vnd.holoviews_exec.v0+json': {'id': div.ref['id']}}
    assert 'application/javascript' in data
    assert 'application/vnd.holoviews_exec.v0+json' in data
    assert 'text/html' in data
    assert data['application/vnd.holoviews_exec.v0+json'] == ''


def test_default_label_formatter():
    assert default_label_formatter('a_b_C') == 'A b C'


def test_default_label_formatter_not_capitalized():
    assert default_label_formatter.instance(capitalize=False)('a_b_C') == 'a b C'


def test_default_label_formatter_not_replace_underscores():
    assert default_label_formatter.instance(replace_underscores=False)('a_b_C') == 'A_b_C'


def test_default_label_formatter_overrides():
    assert default_label_formatter.instance(overrides={'a': 'b'})('a') == 'b'


def test_abbreviated_repr_dict():
    assert abbreviated_repr({'key': 'some really, really long string'}) == "{'key': 'some really, ...}"


def test_abbreviated_repr_list():
    assert abbreviated_repr(['some really, really long string']) == "['some really, ...]"


def test_abbreviated_repr_ordereddict():
    assert (abbreviated_repr(OrderedDict([('key', 'some really, really long string')]))
            == "OrderedDict([('key', ...])")
