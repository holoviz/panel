from collections import OrderedDict

import param
import pytest

from bokeh.models import Div

from panel.depends import bind
from panel.io.notebook import render_mimebundle
from panel.pane import PaneBase
from panel.tests.util import mpl_available
from panel.util import (
    abbreviated_repr, extract_dependencies, get_method_owner, parse_query,
    splice_diff, styler_update, suffix_length, utf16_offset,
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

def test_abbreviated_repr_list_of_parameterized():
    class Foo(param.Parameterized):
        pass

    foo = Foo()
    assert abbreviated_repr(foo) == 'Foo'
    assert abbreviated_repr([foo, foo]) == '[Foo, Foo]'

def test_abbreviated_repr_ordereddict():
    result = abbreviated_repr(OrderedDict([('key', 'some really, really long string')]))
    assert result == "OrderedDict({'key': 'some ...])"


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


def test_parse_query_negative_int():
    assert parse_query('?neg=-5&pos=5') == {'neg': -5, 'pos': 5}
    assert type(parse_query('?neg=-5')['neg']) is int


def test_parse_query_non_ascii_digits_stay_strings():
    assert parse_query('?sup=%C2%B2') == {'sup': '\u00b2'}


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


@pytest.mark.parametrize('a, b, expected', [
    ('', '', 0),
    ('abc', '', 0),
    ('abc', 'xbc', 2),
    ('abc', 'abc', 3),
    ('x' * 200 + 'abc', 'y' * 300 + 'abc', 3),
    ('x' * 200, 'y' + 'x' * 150, 150),
])
def test_suffix_length(a, b, expected):
    assert suffix_length(a, b) == expected


def test_suffix_length_limit():
    assert suffix_length('aaaa', 'aaaa', 2) == 2


@pytest.mark.parametrize('old, new', [
    ('', 'abc'),
    ('abc', ''),
    ('<p>Hello</p>', '<p>Hello world</p>'),
    ('<p>a</p>', '<p>a</p><p>b</p>'),
    ('aaaa', 'aaaaaa'),
    ('abcabc', 'abc'),
    ('same', 'same'),
    ('<ul><li>a</li></ul>', '<ul><li>a</li><li>b</li></ul>'),
])
def test_splice_diff(old, new):
    start, end, patch = splice_diff(old, new)
    assert old[:start] + patch + old[end:] == new
    assert start <= end <= len(old)
    assert len(patch) == len(new) - (len(old) - (end - start))


def test_splice_diff_minimal_patch_before_closing_tags():
    assert splice_diff('<p>Hello</p>\n', '<p>Hello world</p>\n') == (8, 8, ' world')


@pytest.mark.parametrize('text, index, expected', [
    ('abc', 2, 2),
    ('é😀a', 1, 1),
    ('é😀a', 2, 3),
    ('😀😀a', 3, 5),
])
def test_utf16_offset(text, index, expected):
    assert utf16_offset(text, index) == expected
    assert len(text[:index].encode('utf-16-le')) // 2 == expected
