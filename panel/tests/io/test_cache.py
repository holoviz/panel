import datetime as dt
import io
import pathlib
import time

from collections import Counter

import numpy as np
import pandas as pd
import param
import pytest
import requests

try:
    import diskcache
except Exception:
    diskcache = None
diskcache_available = pytest.mark.skipif(diskcache is None, reason="requires diskcache")

from panel.io.cache import _generate_hash, cache, is_equal
from panel.io.state import set_curdoc, state
from panel.tests.util import serve_and_wait

################
# Test hashing #
################

def hashes_equal(v1, v2):
    a, b = _generate_hash(v1), _generate_hash(v2)
    return a == b

def test_str_hash():
    assert hashes_equal('foo', 'foo')
    assert not hashes_equal('foo', 'bar')

def test_int_hash():
    assert hashes_equal(12, 12)
    assert not hashes_equal(1, 2)

def test_float_hash():
    assert hashes_equal(3.14, 3.14)
    assert not hashes_equal(1.2, 3.14)

def test_bool_hash():
    assert hashes_equal(True, True)
    assert hashes_equal(False, False)
    assert not hashes_equal(True, False)

def test_none_hash():
    assert hashes_equal(None, None)
    assert not hashes_equal(None, False)

def test_object_hash():
    obj1, obj2 = object(), object()
    assert hashes_equal(obj1, obj1)
    assert not hashes_equal(obj1, obj2)

def test_bytes_hash():
    assert hashes_equal(b'0', b'0')
    assert not hashes_equal(b'0', b'1')

def test_date_hash():
    assert hashes_equal(dt.date(1988, 4, 14), dt.date(1988, 4, 14))
    assert not hashes_equal(dt.date(1988, 4, 14), dt.date(1988, 4, 15))

def test_datetime_hash():
    assert hashes_equal(dt.datetime(1988, 4, 14, 12, 3, 2, 1), dt.datetime(1988, 4, 14, 12, 3, 2, 1))
    assert not hashes_equal(dt.datetime(1988, 4, 14, 12, 3, 2, 1), dt.datetime(1988, 4, 14, 12, 3, 2, 2))

def test_list_hash():
    assert hashes_equal([0], [0])
    assert hashes_equal(['a', ['b']], ['a', ['b']])
    assert not hashes_equal([0], [1])
    assert not hashes_equal(['a', ['b']], ['a', ['c']])

def test_list_hash_recursive():
    # Recursion
    l = [0]
    l.append(l)
    assert hashes_equal(list(l), list(l))

def test_tuple_hash():
    assert hashes_equal((0,), (0,))
    assert hashes_equal(('a', ('b',)), ('a', ('b',)))
    assert not hashes_equal((0,), (1,))
    assert not hashes_equal(('a', ('b',)), ('a', ('c',)))

def test_dict_hash():
    assert hashes_equal({'a': 0}, {'a': 0})
    assert hashes_equal({'a': {'b': 0}}, {'a': {'b': 0}})
    assert not hashes_equal({'a': 0}, {'b': 0})
    assert not hashes_equal({'a': 0}, {'a': 1})
    assert not hashes_equal({'a': {'b': 0}}, {'a': {'b': 1}})

def test_dict_hash_recursive():
    d = {'a': {}}
    d['a'] = d
    assert hashes_equal(dict(d), dict(d))

def test_stringio_hash():
    sio1, sio2 = io.StringIO(), io.StringIO()
    sio1.write('foo')
    sio2.write('foo')
    sio1.seek(0)
    sio2.seek(0)
    assert hashes_equal(sio1, sio2)
    sio3 = io.StringIO()
    sio3.write('bar')
    sio3.seek(0)
    assert not hashes_equal(sio1, sio3)

def test_bytesio_hash():
    bio1, bio2 = io.BytesIO(), io.BytesIO()
    bio1.write(b'foo')
    bio2.write(b'foo')
    bio1.seek(0)
    bio2.seek(0)
    assert hashes_equal(bio1, bio2)
    bio3 = io.BytesIO()
    bio3.write(b'bar')
    bio3.seek(0)
    assert not hashes_equal(bio1, bio3)

def test_pathlib_hash():
    assert hashes_equal(pathlib.Path('./'), pathlib.Path('./'))
    assert not hashes_equal(pathlib.Path('./'), pathlib.Path('../'))

def test_ndarray_hash():
    assert hashes_equal(np.array([0, 1, 2]), np.array([0, 1, 2]))
    assert not hashes_equal(
        np.array([0, 1, 2], dtype='uint32'),
        np.array([0, 1, 2], dtype='float64')
    )
    assert not hashes_equal(
        np.array([0, 1, 2]),
        np.array([2, 1, 0])
    )

def test_dataframe_hash():
    data = {
        "A": [0.0, 1.0, 2.0, 3.0, 4.0],
        "B": [0.0, 1.0, 0.0, 1.0, 0.0],
        "C": ["foo1", "foo2", "foo3", "foo4", "foo5"],
        "D": pd.bdate_range("1/1/2009", periods=5),
    }
    df1, df2 = pd.DataFrame(data), pd.DataFrame(data)
    assert hashes_equal(df1, df2)
    df2['A'] = df2['A'].values[::-1]
    assert not hashes_equal(df1, df2)

def test_series_hash():
    series1 = pd.Series([0.0, 1.0, 2.0, 3.0, 4.0])
    series2 = series1.copy()
    assert hashes_equal(series1, series2)
    series2.iloc[0] = 3.14
    assert not hashes_equal(series1, series2)

def test_polars_dataframe_hash():
    pl = pytest.importorskip("polars")
    data = {
        "A": [0.0, 1.0, 2.0, 3.0, 4.0],
        "B": [0.0, 1.0, 0.0, 1.0, 0.0],
        "C": ["foo1", "foo2", "foo3", "foo4", "foo5"],
    }
    # DataFrame
    df1, df2 = pl.DataFrame(data), pl.DataFrame(data)
    assert hashes_equal(df1, df2)
    df2 = df2.with_columns(A=pl.col("A").sort(descending=True))
    assert not hashes_equal(df1, df2)

    # Lazy DataFrame
    df1, df2 = pl.LazyFrame(data), pl.LazyFrame(data)
    assert hashes_equal(df1, df2)
    df2 = df2.with_columns(A=pl.col("A").sort(descending=True))
    assert not hashes_equal(df1, df2)

def test_polars_series_hash():
    pl = pytest.importorskip("polars")
    ser1 = pl.Series([0.0, 1.0, 2.0, 3.0, 4.0])
    ser2 = ser1.clone()

    assert hashes_equal(ser1, ser2)
    ser2 = ser2.replace(0.0, 3.14)
    assert not hashes_equal(ser1, ser2)

def test_ufunc_hash():
    assert hashes_equal(np.absolute, np.absolute)
    assert not hashes_equal(np.sin, np.cos)

def test_builtin_hash():
    assert hashes_equal(max, max)
    assert not hashes_equal(max, min)

def test_module_hash():
    assert hashes_equal(np, np)
    assert not hashes_equal(np, io)

################
# Test caching #
################

OFFSET: dict[tuple, int] = {}

def function_with_args(a, b):
    global OFFSET
    offset = OFFSET.get((a, b), 0)
    result = a + b + offset
    OFFSET[(a, b)] = offset + 1
    return result

async def async_function_with_args(a, b):
    global OFFSET
    offset = OFFSET.get((a, b), 0)
    result = a + b + offset
    OFFSET[(a, b)] = offset + 1
    return result

def test_cache_with_args():
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args)
    assert fn(0, 0) == 0
    assert fn(0, 0) == 0

@pytest.mark.asyncio
async def test_async_cache_with_args():
    global OFFSET
    OFFSET.clear()
    fn = cache(async_function_with_args)
    assert (await fn(0, 0)) == 0
    assert (await fn(0, 0)) == 0

def test_cache_with_kwargs():
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args)
    assert fn(a=0, b=0) == 0
    assert fn(a=0, b=0) == 0

def test_cache_clear():
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args)
    assert fn(0, 0) == 0
    fn.clear()
    assert fn(0, 0) == 1

def test_cache_clear_before_cached():
    # https://github.com/holoviz/panel/issues/5968
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args)
    fn.clear()

def test_per_session_cache(document):
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, per_session=True)
    with set_curdoc(document):
        assert fn(a=0, b=0) == 0
    assert fn(a=0, b=0) == 1
    with set_curdoc(document):
        assert fn(a=0, b=0) == 0
    assert fn(a=0, b=0) == 1

def test_per_session_cache_server(port):
    counts = Counter()

    @cache(per_session=True)
    def get_data():
        counts[state.curdoc] += 1
        return "Some data"

    def app():
        get_data()
        get_data()
        return

    serve_and_wait(app, port=port)

    requests.get(f"http://localhost:{port}/")
    requests.get(f"http://localhost:{port}/")

    assert list(counts.values()) == [1, 1]

@diskcache_available
def test_disk_cache(tmp_path):
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, to_disk=True, cache_path=tmp_path)

    assert fn(0, 0) == 0
    assert tmp_path.exists()
    assert list(tmp_path.glob('*'))
    assert fn(0, 0) == 0
    fn.clear()
    assert fn(0, 0) == 1

@pytest.mark.parametrize('to_disk', (True, False))
def test_cache_fifo(to_disk, tmp_path):
    if to_disk and diskcache is None:
        pytest.skip('requires diskcache')
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, max_items=2, policy='fifo', to_disk=to_disk, cache_path=tmp_path)
    assert fn(0, 0) == 0
    assert fn(0, 1) == 1
    assert fn(0, 0) == 0
    assert fn(0, 2) == 2 # (0, 0) should be evicted
    assert fn(0, 0) == 1

@pytest.mark.parametrize('to_disk', (True, False))
def test_cache_lfu(to_disk, tmp_path):
    if to_disk and diskcache is None:
        pytest.skip('requires diskcache')
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, max_items=2, policy='lfu', to_disk=to_disk, cache_path=tmp_path)
    assert fn(0, 0) == 0
    assert fn(0, 0) == 0
    assert fn(0, 1) == 1
    assert fn(0, 2) == 2 # (0, 1) should be evicted
    assert fn(0, 1) == 2

@pytest.mark.parametrize('to_disk', (True, False))
def test_cache_lru(to_disk, tmp_path):
    if to_disk and diskcache is None:
        pytest.skip('requires diskcache')
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, max_items=3, policy='lru', to_disk=to_disk, cache_path=tmp_path)
    assert fn(0, 0) == 0
    assert fn(0, 1) == 1
    assert fn(0, 2) == 2
    assert fn(0, 0) == 0
    assert fn(0, 3) == 3 # (0, 1) should be evicted
    assert fn(0, 0) == 0
    assert fn(0, 1) == 2

@pytest.mark.parametrize('to_disk', (True, False))
def test_cache_ttl(to_disk, tmp_path):
    if to_disk and diskcache is None:
        pytest.skip('requires diskcache')
    global OFFSET
    OFFSET.clear()
    fn = cache(function_with_args, ttl=0.1, to_disk=to_disk, cache_path=tmp_path)
    assert fn(0, 0) == 0
    time.sleep(0.2)
    assert fn(0, 0) == 1

def test_cache_on_undecorated_parameterized_method():
    class Model(param.Parameterized):
        data = param.Parameter(default=1)
        executions = param.Integer(default=0)

        @cache
        def expensive_calculation(self, value):
            self.executions += 1
            return 2*value

    model = Model()
    assert model.expensive_calculation(1) == 2
    assert model.expensive_calculation(1) == 2

    assert model.executions == 1

    assert model.expensive_calculation(2) == 4

    assert model.executions == 2

DF1 = pd.DataFrame({"x": [1]})
DF2 = pd.DataFrame({"y": [1]})

def test_hash_on_simple_dataframes():
    assert _generate_hash(DF1)!=_generate_hash(DF2)

@pytest.mark.parametrize(["value", "other", "expected"], [
    (None, None, True),
    (True, False, False), (False, True, False), (False, False, True), (True, True, True),
    (None, 1, False), (1, None, False), (1, 1, True), (1,2,False),
    (None, "a", False), ("a", None, False), ("a", "a", True), ("a","b",False),
    (1,"1", False),
    (None, DF1, False), (DF1, None, False), (DF1, DF1, True), (DF1, DF1.copy(), True), (DF1,DF2,False),
])
def test_is_equal(value, other, expected):
    assert is_equal(value, other)==expected

def test_cache_clear_two_funcs():
    # see https://github.com/holoviz/panel/issues/6777
    @cache()
    def get_data_1(a=[0]):
        v = a[0]
        a[0] = v+1
        return v

    @cache()
    def get_data_2(b=[0]):
        v = b[0]
        b[0] = v+1
        return v

    assert get_data_1() == 0
    assert get_data_2() == 0

    get_data_1.clear()

    assert get_data_1() == 1
    assert get_data_2() == 0
    assert get_data_1() == 1
    assert get_data_2() == 0
