import numpy as np
import pytest

from panel.pane import Perspective

data = {
    0: ['1981 01 01 00   161    28 10173   270    21     0     0     0',
        '1981 01 01 01   111    33 10175   270    21     0     0 -9999',
        '1981 01 01 02   111    39 10183   330    26     0     0 -9999',
        '1981 01 01 03    94    39 10192 -9999     0     0     0 -9999',
        '1981 01 01 04    72    39 10196 -9999     0     0     0 -9999'],
    'year': [1981, 1981, 1981, 1981, 1981],
 }


def test_perspective_rejects_unsupported_object():
    with pytest.raises(ValueError, match='does not support objects of type'):
        Perspective('not tabular')


def test_perspective_rejects_unsupported_object_on_assignment():
    psp = Perspective(data)

    with pytest.raises(ValueError, match='does not support objects of type'):
        psp.object = 'not tabular'


def test_perspective_int_cols(document, comm):
    psp = Perspective(
        data, columns=[0], aggregates={0: 'mean'}, sort=[[0, 'desc']],
        group_by=[0], split_by=[0], filters=[[0, '==', 'None']]
    )

    model = psp.get_root(document, comm)
    assert '0' in model.source.data
    assert model.columns == ['0']
    assert model.group_by == ['0']
    assert model.split_by == ['0']
    assert model.aggregates == {'0': 'mean'}
    assert model.filters == [['0', '==', 'None']]
    assert model.sort == [['0', 'desc']]

    psp2 = Perspective(data)

    psp2._process_events({
        'columns': ['0'],
        'group_by': ['0'],
        'split_by': ['0'],
        'aggregates': {'0': 'mean'},
        'filters': [['0', '==', 'None']],
        'sort': [['0', 'desc']]
    })

    assert psp2.columns == [0]
    assert psp2.group_by == [0]
    assert psp2.split_by == [0]
    assert psp2.aggregates == {0: 'mean'}
    assert psp2.sort == [[0, 'desc']]
    assert psp2.filters == [[0, '==', 'None']]

def test_perspective_can_drag_to_filter():
    # Given
    msg = {'filters': [['Curve', '==', None, 'integer', 'sum']]}
    # When
    actual = Perspective()._process_property_change(msg)
    # Then
    assert actual == msg

def test_perspective_can_filter_to_value():
    # Given
    msg = {'filters': [['Curve', '==', 4]]}
    # When
    actual = Perspective()._process_property_change(msg)
    # Then
    assert actual == msg

def test_perspective_can_drag_to_sort():
    # Given
    msg = {'sort': [['Curve']]}
    # When
    actual = Perspective()._process_property_change(msg)
    # Then
    assert actual == msg

def test_perspective_can_sort_desc():
    # Given
    msg = {'sort': [['Curve', 'desc']]}
    # When
    actual = Perspective()._process_property_change(msg)
    # Then
    assert actual == msg


def _polars_frame(data):
    pl = pytest.importorskip('polars')
    return pl.DataFrame(data)


def _pyarrow_frame(data):
    pa = pytest.importorskip('pyarrow')
    return pa.table(data)


def _pandas_frame(data):
    pd = pytest.importorskip('pandas')
    return pd.DataFrame(data)


def _column(df, col):
    from panel.util.dataframe import to_narwhals
    return to_narwhals(df)[col].to_list()


@pytest.fixture(params=[_polars_frame, _pyarrow_frame], ids=['polars', 'pyarrow'])
def indexless_backend(request):
    return request.param


@pytest.mark.parametrize('backend', [_pandas_frame, _polars_frame, _pyarrow_frame])
def test_perspective_applies_dataframe(backend):
    assert Perspective.applies(backend({'a': [1, 2]})) == 0


def test_perspective_indexless_frame(indexless_backend, document, comm):
    import datetime as dt

    df = indexless_backend({
        'int': [1, 2], 'float': [1.5, 2.5], 'str': ['a', 'b'], 'bool': [True, False],
        'datetime': [dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 2)],
    })
    psp = Perspective(df, columns=['int', 'str'])

    model = psp.get_root(document, comm)

    assert list(model.source.data) == ['int', 'float', 'str', 'bool', 'datetime']
    assert list(model.source.data['int']) == [1, 2]
    assert list(model.source.data['str']) == ['a', 'b']
    assert model.schema == {
        'int': 'integer', 'float': 'float', 'str': 'string', 'bool': 'boolean',
        'datetime': 'datetime',
    }
    assert model.columns == ['int', 'str']


def test_perspective_polars_categorical(document, comm):
    pl = pytest.importorskip('polars')
    df = pl.DataFrame({'cat': ['a', 'b']}, schema={'cat': pl.Categorical})

    model = Perspective(df).get_root(document, comm)

    assert model.schema == {'cat': 'string'}
    assert list(model.source.data['cat']) == ['a', 'b']


@pytest.mark.parametrize('rollover', [None, 2])
def test_perspective_indexless_stream(indexless_backend, rollover, document, comm):
    df = indexless_backend({'a': [1, 2], 'b': ['x', 'y']})
    psp = Perspective(df)
    model = psp.get_root(document, comm)
    events = []
    psp.param.watch(events.append, 'object')

    psp.stream({'a': [3], 'b': ['z']}, rollover=rollover)

    expected = [1, 2, 3][-(rollover or 3):]
    assert type(psp.object) is type(df)
    assert _column(psp.object, 'a') == expected
    assert list(model.source.data['a']) == expected
    assert len(events) == 1


def test_perspective_pandas_stream_does_not_duplicate(document, comm):
    psp = Perspective(_pandas_frame({'a': [1, 2]}))
    model = psp.get_root(document, comm)

    psp.stream({'a': [3]})

    assert list(model.source.data['a']) == [1, 2, 3]


def test_perspective_indexless_patch(indexless_backend, document, comm):
    df = indexless_backend({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
    psp = Perspective(df)
    model = psp.get_root(document, comm)

    psp.patch({'a': [(0, 10), (slice(1, 3), [20, 30])], 'b': [(1, 'Y')]})

    assert type(psp.object) is type(df)
    assert _column(psp.object, 'a') == [10, 20, 30]
    assert _column(psp.object, 'b') == ['x', 'Y', 'z']
    assert list(model.source.data['a']) == [10, 20, 30]
    assert list(model.source.data['b']) == ['x', 'Y', 'z']


def test_perspective_pandas_patch_dict(document, comm):
    pd = pytest.importorskip('pandas')
    df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
    psp = Perspective(df)
    model = psp.get_root(document, comm)

    psp.patch({'a': [(0, 10), (slice(1, 3), [20, 30])], 'b': [(1, 'Y')]})

    assert psp.object is df
    assert df.to_dict('list') == {'a': [10, 20, 30], 'b': ['x', 'Y', 'z']}
    assert list(model.source.data['a']) == [10, 20, 30]
    assert list(model.source.data['b']) == ['x', 'Y', 'z']


def test_perspective_patch_slice_scalar(document, comm):
    pd = pytest.importorskip('pandas')
    psp = Perspective(pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']}))
    model = psp.get_root(document, comm)

    psp.patch({'b': [(slice(0, 2), 'w')]})

    assert psp.object['b'].tolist() == ['w', 'w', 'z']
    assert list(model.source.data['b']) == ['w', 'w', 'z']


def test_perspective_pandas_patch_dataframe_custom_index(document, comm):
    pd = pytest.importorskip('pandas')
    psp = Perspective(pd.DataFrame({'a': [1, 2, 3]}, index=[10, 20, 30]))
    model = psp.get_root(document, comm)

    psp.patch(pd.DataFrame({'a': [5]}, index=[20]))

    assert psp.object['a'].tolist() == [1, 5, 3]
    assert list(model.source.data['a']) == [1, 5, 3]


def test_perspective_pandas_patch_series(document, comm):
    pd = pytest.importorskip('pandas')
    psp = Perspective(pd.DataFrame({'a': [1, 2], 'b': ['x', 'y']}))
    model = psp.get_root(document, comm)

    psp.patch(pd.Series({'index': 1, 'a': 9, 'b': 'z'}))

    assert psp.object.to_dict('list') == {'a': [1, 9], 'b': ['x', 'z']}
    assert list(model.source.data['b']) == ['x', 'z']


def test_perspective_dict_patch(document, comm):
    psp = Perspective({'a': np.array([1, 2])})
    model = psp.get_root(document, comm)

    psp.patch({'a': [(0, 5)]})

    assert list(psp.object['a']) == [5, 2]
    assert list(model.source.data['a']) == [5, 2]
