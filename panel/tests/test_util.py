import sys

from collections import OrderedDict

import param

from bokeh.models import Div

from panel.depends import bind
from panel.io.notebook import render_mimebundle
from panel.pane import PaneBase
from panel.tests.util import mpl_available
from panel.util import (
    abbreviated_repr, extract_dependencies, get_method_owner, parse_query,
    styler_update,
)


def test_get_method_owner_class():
    assert get_method_owner(PaneBase.get_pane_type) is PaneBase


def test_get_method_owner_instance():
    div = Div()
    assert get_method_owner(div.update) is div


def test_get_function_dependencies():
    class Test(param.Parameterized):
        a = param.Parameter()

    assert extract_dependencies(bind(lambda a: a, Test.param.a)) == [Test.param.a]


def test_get_parameterized_dependencies():
    class Test(param.Parameterized):

        a = param.Parameter()
        b = param.Parameter()

        @param.depends('a')
        def dep_a(self):
            return

        @param.depends('dep_a', 'b')
        def dep_ab(self):
            return

    test = Test()

    assert extract_dependencies(test.dep_a) == [test.param.a]
    assert extract_dependencies(test.dep_ab) == [test.param.a, test.param.b]


def test_get_parameterized_subobject_dependencies():
    class A(param.Parameterized):

        value = param.Parameter()

    class B(param.Parameterized):

        a = param.ClassSelector(default=A(), class_=A)

        @param.depends('a.value')
        def dep_a_value(self):
            return

    test = B()

    assert extract_dependencies(test.dep_a_value) == [test.a.param.value]

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
    if sys.version_info >= (3, 12):
        expected = "OrderedDict({'key': 'some ...])"
    else:
        expected = "OrderedDict([('key', ...])"

    result = abbreviated_repr(OrderedDict([('key', 'some really, really long string')]))
    assert result == expected


def test_parse_query():
    query = '?bool=true&int=2&float=3.0&json=["a"%2C+"b"]'
    expected_results = {
        "bool": True,
        "int": 2,
        "float": 3.0,
        "json": ["a", "b"],
    }
    results = parse_query(query)
    assert expected_results == results


def test_parse_query_singe_quoted():
    query = "?str=abc&json=%5B%27def%27%5D"
    expected_results = {
        "str": 'abc',
        "json": ['def'],
    }
    results = parse_query(query)
    assert expected_results == results


@mpl_available
def test_styler_update(dataframe):
    styler = dataframe.style.background_gradient('Reds')
    new_df = dataframe.iloc[:, :2]
    new_style = new_df.style
    new_style._todo = styler_update(styler, new_df)
    new_style._compute()
    assert dict(new_style.ctx) == {
        (0, 0): [('background-color', '#fff5f0'), ('color', '#000000')],
        (0, 1): [('background-color', '#fff5f0'), ('color', '#000000')],
        (1, 0): [('background-color', '#fb694a'), ('color', '#f1f1f1')],
        (1, 1): [('background-color', '#fb694a'), ('color', '#f1f1f1')],
        (2, 0): [('background-color', '#67000d'), ('color', '#f1f1f1')],
        (2, 1): [('background-color', '#67000d'), ('color', '#f1f1f1')]
    }
